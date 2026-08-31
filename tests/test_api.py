import importlib
import os
import sys
import tempfile
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import func, select

from alembic import command

TEST_DB = Path(tempfile.gettempdir()) / f"medsync-{uuid.uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["JWT_SECRET_KEY"] = "test-secret-with-at-least-32-characters"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
command.upgrade(Config("alembic.ini"), "head")
from challenge_answers import BUILTIN_CHALLENGE_ANSWERS, BUILTIN_CHALLENGE_SOURCES
from clinical_cases_batch_two import EXPANSION_BATCH_TWO_CASES
from clinical_cases_psychiatry import PSYCHIATRY_CASES
from clinical_rubric_catalog import CLINICAL_RUBRICS
from database import SessionLocal
from evaluation import (
    ClinicalRubricDefinition,
    SimulationSubmission,
    evaluate_objective,
)
from models import (
    AIUsageRecord,
    ClinicalCase,
    ClinicalExam,
    ClinicalRubric,
    ExamQuestion,
    PaymentGrant,
    PaymentOrder,
    QuestionAttempt,
    QuestionReport,
    SimulationRequest,
    StudyError,
    User,
    UserEntitlement,
)
from schemas import (
    AdminVisualChallengeUpsert,
    AnnouncementUpsert,
    QuestionExplanation,
)
from services.clinical_content import seed_clinical_content
from services.question_content import seed_question_content

with SessionLocal() as db:
    seed_clinical_content(db)
    seed_question_content(db)
main = importlib.import_module("main")
client = TestClient(main.app)


def test_builtin_visual_challenge_catalog_is_complete():
    expected_ids = {f"desafio-visual-{index:03d}" for index in range(1, 111)}

    assert set(BUILTIN_CHALLENGE_ANSWERS) == expected_ids
    assert set(BUILTIN_CHALLENGE_SOURCES) == expected_ids

    for challenge in BUILTIN_CHALLENGE_ANSWERS.values():
        assert challenge["correct_option_id"]
        assert challenge["diagnosis"]
        assert challenge["explanation"]
        assert len(challenge["key_findings"]) == 3

    for credit, license_name, source_url in BUILTIN_CHALLENGE_SOURCES.values():
        assert credit
        assert license_name
        assert source_url.startswith("https://")


def _register_and_login(email: str = "aluno@example.com") -> str:
    response = client.post(
        "/usuarios/registrar",
        json={
            "nome": "Aluno MedSync",
            "email": email,
            "periodo_curso": 6,
            "faculdade": "Universidade Federal do Maranhão",
            "password": "senha-segura",
            "aceite_termos": True,
        },
    )
    assert response.status_code == 201

    # Os demais testes exercitam áreas autenticadas; a verificação em si possui
    # cenários dedicados abaixo.
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email.lower()))
        user.email_verified_at = datetime.now(UTC)
        user.email_verification_token_hash = None
        user.email_verification_expires_at = None
        user.email_verification_sent_at = None
        db.commit()

    response = client.post(
        "/usuarios/login", json={"email": email, "password": "senha-segura"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["x-request-id"]
    assert response.headers["x-content-type-options"] == "nosniff"

    ready = client.get("/ready")
    assert ready.status_code == 200
    assert ready.json() == {"status": "ready", "database": "ok"}


def test_production_disables_interactive_api_documentation():
    previous_environment = os.environ.get("ENVIRONMENT")
    os.environ["ENVIRONMENT"] = "production"
    try:
        production_client = TestClient(main.create_app())
        assert production_client.get("/docs").status_code == 404
        assert production_client.get("/openapi.json").status_code == 404
    finally:
        if previous_environment is None:
            os.environ.pop("ENVIRONMENT", None)
        else:
            os.environ["ENVIRONMENT"] = previous_environment


def test_security_headers_and_request_body_limit():
    response = client.get("/health", headers={"x-forwarded-proto": "https"})
    assert response.headers["strict-transport-security"].startswith("max-age=")
    assert response.headers["content-security-policy"].startswith("default-src 'none'")

    oversized = client.post(
        "/usuarios/login",
        content=b"x" * 1_000_001,
        headers={"content-type": "application/json"},
    )
    assert oversized.status_code == 413


def test_admin_urls_reject_unsafe_protocols():
    with pytest.raises(ValidationError):
        AnnouncementUpsert(
            titulo="Aviso seguro",
            mensagem="Mensagem de exemplo",
            link_url="javascript:alert(1)",
        )

    with pytest.raises(ValidationError):
        AdminVisualChallengeUpsert(
            id="desafio-seguro",
            titulo="Desafio seguro",
            especialidade="Cardiologia",
            dificuldade="Fácil",
            modalidade="ECG",
            pergunta="Qual é o diagnóstico mais provável?",
            imagem_url="http://example.com/image.png",
            imagem_alt="Traçado eletrocardiográfico",
            alternativas=["A", "B", "C", "D"],
            alternativa_correta=0,
            diagnostico_correto="Diagnóstico",
            explicacao="Explicação clínica suficientemente detalhada.",
        )


def test_public_stats_counts_students_without_exposing_admins():
    admin_email = f"admin-{uuid.uuid4().hex}@example.com"
    student_email = f"student-{uuid.uuid4().hex}@example.com"
    previous_admin_emails = os.environ.get("ADMIN_EMAILS")
    os.environ["ADMIN_EMAILS"] = admin_email

    try:
        before = client.get("/estatisticas-publicas")
        assert before.status_code == 200

        for email in (student_email, admin_email):
            response = client.post(
                "/usuarios/registrar",
                json={
                    "nome": "Estudante MedSync",
                    "email": email,
                    "periodo_curso": 6,
                    "faculdade": "Universidade Federal do Maranhão",
                    "password": "senha-segura",
                    "aceite_termos": True,
                },
            )
            assert response.status_code == 201

        after = client.get("/estatisticas-publicas")
        assert after.status_code == 200
        assert after.json() == {
            "estudantes_medsync": before.json()["estudantes_medsync"] + 1
        }
        assert after.headers["cache-control"] == "public, max-age=300"
    finally:
        if previous_admin_emails is None:
            os.environ.pop("ADMIN_EMAILS", None)
        else:
            os.environ["ADMIN_EMAILS"] = previous_admin_emails


def test_login_rate_limit_can_be_enabled():
    os.environ["RATE_LIMIT_ENABLED"] = "true"
    limited_client = TestClient(main.create_app())
    payload = {"email": "inexistente@example.com", "password": "senha-invalida"}
    for _ in range(10):
        assert limited_client.post("/usuarios/login", json=payload).status_code == 401
    limited = limited_client.post("/usuarios/login", json=payload)
    assert limited.status_code == 429
    assert int(limited.headers["retry-after"]) >= 1
    os.environ["RATE_LIMIT_ENABLED"] = "false"


def test_clinical_catalog_is_seeded_once_with_versioned_rubric():
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(ClinicalCase)) == 80
        assert db.scalar(select(func.count()).select_from(ClinicalExam)) > 65
        rubric = db.scalar(select(ClinicalRubric).where(ClinicalRubric.id_caso == 8))
        assert rubric is not None
        assert rubric.versao == 8
        assert rubric.status == "revisada"
        assert seed_clinical_content(db) is False


def test_primary_care_collection_has_revised_rubrics_and_is_easy():
    with SessionLocal() as db:
        cases = list(
            db.scalars(
                select(ClinicalCase)
                .where(ClinicalCase.id.between(41, 55))
                .order_by(ClinicalCase.id)
            ).all()
        )
        assert [case.id for case in cases] == list(range(41, 56))
        assert all(case.nivel_dificuldade == "Fácil" for case in cases)
        assert all(case.status == "publicado" for case in cases)
        assert all(case.is_premium is False for case in cases)

        rubrics = list(
            db.scalars(
                select(ClinicalRubric).where(ClinicalRubric.id_caso.between(41, 55))
            ).all()
        )
        assert len(rubrics) == 15
        assert all(rubric.status == "revisada" for rubric in rubrics)

    for case_id in range(41, 56):
        ClinicalRubricDefinition.model_validate(CLINICAL_RUBRICS[case_id])


def test_first_expansion_batch_is_complete_rich_and_revised():
    batch_ids = set(range(56, 61))

    with SessionLocal() as db:
        cases = list(
            db.scalars(
                select(ClinicalCase)
                .where(ClinicalCase.id.in_(batch_ids))
                .order_by(ClinicalCase.id)
            ).all()
        )
        rubrics = list(
            db.scalars(
                select(ClinicalRubric).where(ClinicalRubric.id_caso.in_(batch_ids))
            ).all()
        )

        assert [case.id for case in cases] == list(range(56, 61))
        assert all(case.nivel_dificuldade == "Difícil" for case in cases)
        assert all(case.status == "publicado" for case in cases)
        assert all(len(case.exames) == 10 for case in cases)
        assert len(rubrics) == 5
        assert all(rubric.status == "revisada" for rubric in rubrics)
        assert all(rubric.versao == 8 for rubric in rubrics)

        for case in cases:
            rubric = ClinicalRubricDefinition.model_validate(CLINICAL_RUBRICS[case.id])
            exam_ids = {exam.codigo for exam in case.exames}
            classified_ids = set(
                rubric.exames_essenciais
                + rubric.exames_opcionais
                + rubric.exames_desnecessarios
            )

            assert classified_ids == exam_ids
            assert set(rubric.justificativa_exames) == exam_ids
            assert rubric.fontes_clinicas
            assert rubric.desfechos_conduta is not None
            assert len(rubric.desfechos_conduta.adequada.reavaliacao) >= 4
            assert len(rubric.desfechos_conduta.parcial.reavaliacao) >= 4
            assert len(rubric.desfechos_conduta.insegura.reavaliacao) >= 4


def test_first_expansion_batch_exposes_multiple_vital_signs_without_diagnosis_in_title():
    token = _register_and_login("lote-expansao-um@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    for case_id in range(56, 61):
        response = client.get(f"/casos-clinicos/{case_id}", headers=headers)
        assert response.status_code == 200
        body = response.json()
        documented_vitals = [
            item for item in body["sinais_vitais"] if item["valor"] is not None
        ]

        assert len(documented_vitals) == 5
        assert body["avaliacao_2_disponivel"] is True
        assert body["titulo"].startswith(f"Caso #{case_id:03d} – ")
        assert "infarto" not in body["titulo"].lower()
        assert "dissec" not in body["titulo"].lower()
        assert "tampon" not in body["titulo"].lower()


def test_second_expansion_batch_is_intermediate_and_uses_six_exams_per_case():
    batch_ids = set(range(61, 66))

    with SessionLocal() as db:
        cases = list(
            db.scalars(
                select(ClinicalCase)
                .where(ClinicalCase.id.in_(batch_ids))
                .order_by(ClinicalCase.id)
            ).all()
        )
        rubrics = list(
            db.scalars(
                select(ClinicalRubric).where(ClinicalRubric.id_caso.in_(batch_ids))
            ).all()
        )

        assert [case.id for case in cases] == list(range(61, 66))
        assert all(case.nivel_dificuldade == "Intermediário" for case in cases)
        assert all(len(case.exames) == 6 for case in cases)
        assert len(rubrics) == 5
        assert all(rubric.status == "revisada" for rubric in rubrics)
        assert all(rubric.versao == 8 for rubric in rubrics)

        for case in cases:
            rubric = ClinicalRubricDefinition.model_validate(CLINICAL_RUBRICS[case.id])
            exam_ids = {exam.codigo for exam in case.exames}
            classified_ids = set(
                rubric.exames_essenciais
                + rubric.exames_opcionais
                + rubric.exames_desnecessarios
            )
            assert exam_ids == classified_ids
            assert set(rubric.justificativa_exames) == exam_ids
            assert rubric.fontes_clinicas


def test_second_expansion_batch_accepts_short_diagnostic_answers():
    short_answers = {
        61: "Pneumonia",
        62: "Colecistite aguda",
        63: "Cetoacidose diabética",
        64: "Gravidez ectópica",
        65: "Glaucoma agudo",
    }
    cases = {case["id"]: case for case in EXPANSION_BATCH_TWO_CASES}

    for case_id, answer in short_answers.items():
        rubric = CLINICAL_RUBRICS[case_id]
        submission = SimulationSubmission(
            exames_solicitados=rubric["exames_essenciais"],
            hipotese_diagnostica=answer,
            conduta_proposta="Monitorizar, estabilizar e realizar tratamento indicado.",
        )
        score, _, context = evaluate_objective(cases[case_id], submission, rubric)

        assert score.hipotese == 30
        assert context["classificacao_hipotese"] == "correta"


def test_psychiatry_batch_has_balanced_difficulty_and_complete_rubrics():
    batch_ids = set(range(66, 81))

    with SessionLocal() as db:
        cases = list(
            db.scalars(
                select(ClinicalCase)
                .where(ClinicalCase.id.in_(batch_ids))
                .order_by(ClinicalCase.id)
            ).all()
        )
        rubrics = list(
            db.scalars(
                select(ClinicalRubric).where(ClinicalRubric.id_caso.in_(batch_ids))
            ).all()
        )

        assert [case.id for case in cases] == list(range(66, 81))
        assert all(case.especialidade == "Psiquiatria e Saúde Mental" for case in cases)
        assert [case.nivel_dificuldade for case in cases].count("Fácil") == 5
        assert [case.nivel_dificuldade for case in cases].count("Intermediário") == 5
        assert [case.nivel_dificuldade for case in cases].count("Difícil") == 5
        assert all(len(case.exames) == 6 for case in cases)
        assert len(rubrics) == 15
        assert all(rubric.status == "revisada" for rubric in rubrics)
        assert all(rubric.versao == 8 for rubric in rubrics)

        for case in cases:
            rubric = ClinicalRubricDefinition.model_validate(CLINICAL_RUBRICS[case.id])
            exam_ids = {exam.codigo for exam in case.exames}
            classified_ids = set(
                rubric.exames_essenciais
                + rubric.exames_opcionais
                + rubric.exames_desnecessarios
            )
            assert exam_ids == classified_ids
            assert set(rubric.justificativa_exames) == exam_ids
            assert rubric.fontes_clinicas
            assert len(rubric.desfechos_conduta.adequada.reavaliacao) >= 4
            assert len(rubric.desfechos_conduta.parcial.reavaliacao) >= 4
            assert len(rubric.desfechos_conduta.insegura.reavaliacao) >= 4


def test_psychiatry_batch_accepts_short_diagnostic_answers():
    short_answers = {
        66: "Depressão maior",
        67: "Ansiedade generalizada",
        68: "Transtorno do pânico",
        69: "Ansiedade social",
        70: "TDAH",
        71: "TOC",
        72: "TEPT",
        73: "Mania",
        74: "Abstinência alcoólica",
        75: "Anorexia nervosa",
        76: "Esquizofrenia",
        77: "Psicose pós-parto",
        78: "Catatonia",
        79: "Borderline",
        80: "Delirium",
    }
    cases = {case["id"]: case for case in PSYCHIATRY_CASES}

    for case_id, answer in short_answers.items():
        rubric = CLINICAL_RUBRICS[case_id]
        submission = SimulationSubmission(
            exames_solicitados=rubric["exames_essenciais"],
            hipotese_diagnostica=answer,
            conduta_proposta="Proteger, monitorar, tratar e organizar seguimento.",
        )
        score, _, context = evaluate_objective(cases[case_id], submission, rubric)

        assert score.hipotese == 30
        assert context["classificacao_hipotese"] == "correta"


def test_premium_case_is_enforced_by_the_api():
    email = f"premium-gate-{uuid.uuid4().hex}@example.com"
    token = _register_and_login(email)
    headers = {"Authorization": f"Bearer {token}"}

    with SessionLocal() as db:
        case = db.get(ClinicalCase, 8)
        case.is_premium = True
        db.commit()

    try:
        blocked = client.get("/casos-clinicos/8", headers=headers)
        assert blocked.status_code == 403
        assert "Premium" in blocked.json()["detail"]

        with SessionLocal() as db:
            user = db.scalar(select(User).where(User.email == email))
            db.add(
                UserEntitlement(
                    id_usuario=user.id,
                    plano_id="avulso",
                    status="ativo",
                    valido_ate=datetime.now(UTC) + timedelta(days=30),
                )
            )
            db.commit()

        allowed = client.get("/casos-clinicos/8", headers=headers)
        assert allowed.status_code == 200
    finally:
        with SessionLocal() as db:
            case = db.get(ClinicalCase, 8)
            case.is_premium = False
            user = db.scalar(select(User).where(User.email == email))
            entitlement = db.get(UserEntitlement, user.id)
            if entitlement:
                db.delete(entitlement)
            db.commit()


def test_seed_adds_catalog_expansions_to_an_existing_database():
    with SessionLocal() as db:
        case = db.get(ClinicalCase, 55)
        assert case is not None
        db.delete(case)
        db.commit()
        assert db.scalar(select(func.count()).select_from(ClinicalCase)) == 79

        assert seed_clinical_content(db) is False
        restored = db.get(ClinicalCase, 55)
        assert restored is not None
        assert restored.titulo_publico == "Acordei com o olho vermelho"
        assert restored.rubrica is not None
        assert restored.rubrica.status == "revisada"


def test_case_without_essential_exams_rewards_avoiding_low_value_tests():
    case = {
        "id": 41,
        "exames_disponiveis": [
            {"id": "teste_estreptococo", "nome": "Teste rápido"},
            {"id": "hemograma", "nome": "Hemograma"},
        ],
    }
    submission = SimulationSubmission(
        exames_solicitados=[],
        hipotese_diagnostica="Faringite viral",
        conduta_proposta="Hidratação, analgesia, sem antibiótico e retorno se piora.",
    )
    score, _, _ = evaluate_objective(case, submission, CLINICAL_RUBRICS[41])
    assert score.exames == 40

    submission.exames_solicitados = ["hemograma"]
    score_with_low_value_test, _, _ = evaluate_objective(
        case,
        submission,
        CLINICAL_RUBRICS[41],
    )
    assert score_with_low_value_test.exames == 36


def test_existing_pilot_rubric_is_safely_upgraded():
    with SessionLocal() as db:
        rubric = db.scalar(select(ClinicalRubric).where(ClinicalRubric.id_caso == 8))
        rubric.versao = 1
        rubric.definicao = {"formato": "legado"}
        db.commit()

        assert seed_clinical_content(db) is False
        db.refresh(rubric)

        assert rubric.versao == 8
        assert rubric.definicao["feedback_seguranca"]


def test_duplicate_registration_is_rejected():
    _register_and_login()
    response = client.post(
        "/usuarios/registrar",
        json={
            "nome": "Outro nome",
            "email": "ALUNO@example.com",
            "periodo_curso": 7,
            "faculdade": "UFMA",
            "password": "outra-senha",
            "aceite_termos": True,
        },
    )
    assert response.status_code == 409


def test_registration_saves_academic_profile():
    response = client.post(
        "/usuarios/registrar",
        json={
            "nome": "  Maria   da Silva  ",
            "email": "maria.academica@example.com",
            "periodo_curso": 4,
            "faculdade": "  Universidade   Federal do Piauí ",
            "password": "senha-segura",
            "aceite_termos": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["nome"] == "Maria da Silva"
    assert response.json()["periodo_curso"] == 4
    assert response.json()["faculdade"] == "Universidade Federal do Piauí"
    assert response.json()["email_verificado"] is False


def test_new_account_requires_email_verification(monkeypatch):
    captured = {}

    def fake_send_verification_email(**payload):
        captured.update(payload)

    monkeypatch.setattr(
        "routers.users.send_verification_email", fake_send_verification_email
    )
    email = "confirmacao@example.com"
    registration = client.post(
        "/usuarios/registrar",
        json={
            "nome": "Aluno Confirmação",
            "email": email,
            "periodo_curso": 6,
            "faculdade": "UFMA",
            "password": "senha-segura",
            "aceite_termos": True,
        },
    )

    assert registration.status_code == 201
    assert registration.json()["email_verificado"] is False
    assert captured["email"] == email
    blocked_login = client.post(
        "/usuarios/login", json={"email": email, "password": "senha-segura"}
    )
    assert blocked_login.status_code == 403
    assert "ainda não foi confirmado" in blocked_login.json()["detail"]

    confirmation = client.post(
        "/usuarios/verificar-email", json={"token": captured["raw_token"]}
    )
    assert confirmation.status_code == 200
    assert "conta MedSync está pronta" in confirmation.json()["message"]
    assert (
        client.post(
            "/usuarios/login", json={"email": email, "password": "senha-segura"}
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/usuarios/verificar-email", json={"token": captured["raw_token"]}
        ).status_code
        == 400
    )


def test_email_verification_can_be_resent_without_account_enumeration(monkeypatch):
    sent_tokens = []

    def fake_send_verification_email(**payload):
        sent_tokens.append(payload["raw_token"])

    monkeypatch.setattr(
        "routers.users.send_verification_email", fake_send_verification_email
    )
    email = "reenvio@example.com"
    registration = client.post(
        "/usuarios/registrar",
        json={
            "nome": "Aluno Reenvio",
            "email": email,
            "periodo_curso": 5,
            "faculdade": "UFMA",
            "password": "senha-segura",
            "aceite_termos": True,
        },
    )
    assert registration.status_code == 201

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        user.email_verification_sent_at = datetime.now(UTC) - timedelta(minutes=2)
        db.commit()

    resend = client.post("/usuarios/reenviar-verificacao", json={"email": email})
    unknown = client.post(
        "/usuarios/reenviar-verificacao", json={"email": "desconhecido@example.com"}
    )
    assert resend.status_code == 202
    assert unknown.status_code == 202
    assert resend.json() == unknown.json()
    assert len(sent_tokens) == 2


def test_password_recovery_is_private_one_time_and_revokes_old_sessions(monkeypatch):
    email = f"recuperacao-{uuid.uuid4().hex}@example.com"
    old_token = _register_and_login(email)
    captured = {}

    def fake_send_password_reset_email(**payload):
        captured.update(payload)

    monkeypatch.setattr(
        "routers.users.send_password_reset_email",
        fake_send_password_reset_email,
    )

    recovery = client.post("/usuarios/recuperar-senha", json={"email": email})
    unknown = client.post(
        "/usuarios/recuperar-senha",
        json={"email": f"desconhecido-{uuid.uuid4().hex}@example.com"},
    )
    assert recovery.status_code == 202
    assert unknown.status_code == 202
    assert recovery.json() == unknown.json()
    assert captured["email"] == email
    assert captured["expires_minutes"] == 30

    raw_token = captured["raw_token"]
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        assert user.password_reset_token_hash
        assert user.password_reset_token_hash != raw_token
        assert len(user.password_reset_token_hash) == 64

    captured.clear()
    cooldown = client.post("/usuarios/recuperar-senha", json={"email": email})
    assert cooldown.status_code == 202
    assert captured == {}

    reset = client.post(
        "/usuarios/redefinir-senha",
        json={"token": raw_token, "password": "nova-senha-segura"},
    )
    assert reset.status_code == 200

    assert (
        client.get(
            "/usuarios/me", headers={"Authorization": f"Bearer {old_token}"}
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/usuarios/login",
            json={"email": email, "password": "senha-segura"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/usuarios/login",
            json={"email": email, "password": "nova-senha-segura"},
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/usuarios/redefinir-senha",
            json={"token": raw_token, "password": "outra-senha-segura"},
        ).status_code
        == 400
    )


def test_expired_password_reset_link_is_rejected(monkeypatch):
    email = f"recuperacao-expirada-{uuid.uuid4().hex}@example.com"
    _register_and_login(email)
    captured = {}
    monkeypatch.setattr(
        "routers.users.send_password_reset_email",
        lambda **payload: captured.update(payload),
    )
    assert (
        client.post("/usuarios/recuperar-senha", json={"email": email}).status_code
        == 202
    )

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        user.password_reset_expires_at = datetime.now(UTC) - timedelta(seconds=1)
        db.commit()

    response = client.post(
        "/usuarios/redefinir-senha",
        json={"token": captured["raw_token"], "password": "nova-senha-segura"},
    )
    assert response.status_code == 400
    assert "inválido ou expirou" in response.json()["detail"]


def test_registration_requires_valid_academic_profile():
    payload = {
        "nome": "Aluno sem perfil",
        "email": "perfil-invalido@example.com",
        "password": "senha-segura",
    }
    assert client.post("/usuarios/registrar", json=payload).status_code == 422

    payload.update({"periodo_curso": 13, "faculdade": "UFMA"})
    assert client.post("/usuarios/registrar", json=payload).status_code == 422


def test_registration_requires_and_records_legal_acceptance():
    payload = {
        "nome": "Aluno Legal",
        "email": "legal@example.com",
        "periodo_curso": 5,
        "faculdade": "UFMA",
        "password": "senha-segura",
    }
    assert client.post("/usuarios/registrar", json=payload).status_code == 422

    payload["aceite_termos"] = False
    assert client.post("/usuarios/registrar", json=payload).status_code == 422

    payload["aceite_termos"] = True
    assert client.post("/usuarios/registrar", json=payload).status_code == 201
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == "legal@example.com"))
        assert user.terms_accepted_at is not None
        assert user.terms_version == "2026-08-11"
        assert user.privacy_version == "2026-08-11"


def test_asaas_checkout_and_webhook_activate_premium_once(monkeypatch):
    token = _register_and_login("pagamentos@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    captured = {}

    def fake_checkout(payload):
        captured.update(payload)
        return {
            "id": "checkout_sandbox_123",
            "link": "https://sandbox.asaas.com/checkoutSession/show?id=checkout_sandbox_123",
            "status": "ACTIVE",
        }

    monkeypatch.setattr("routers.payments.create_checkout", fake_checkout)
    checkout = client.post(
        "/pagamentos/checkout",
        headers=headers,
        json={"plano_id": "recorrente"},
    )
    assert checkout.status_code == 201
    order_id = checkout.json()["pedido_id"]
    assert captured["externalReference"] == order_id
    assert captured["billingTypes"] == ["CREDIT_CARD"]
    assert captured["chargeTypes"] == ["RECURRENT"]
    assert captured["items"][0]["value"] == 23.9
    assert captured["subscription"]["cycle"] == "MONTHLY"
    assert "customerData" not in captured

    os.environ["ASAAS_WEBHOOK_TOKEN"] = "token-webhook-seguro-com-mais-de-32-caracteres"
    event = {
        "id": "evt_payment_confirmed_123",
        "event": "PAYMENT_CONFIRMED",
        "payment": {
            "id": "pay_123",
            "externalReference": order_id,
            "subscription": "sub_123",
        },
    }
    assert client.post("/pagamentos/webhooks/asaas", json=event).status_code == 401
    webhook_headers = {"asaas-access-token": os.environ["ASAAS_WEBHOOK_TOKEN"]}
    checkout_paid = {
        "id": "evt_checkout_recurring_paid_123",
        "event": "CHECKOUT_PAID",
        "checkout": {"id": "checkout_sandbox_123", "status": "PAID"},
    }
    assert (
        client.post(
            "/pagamentos/webhooks/asaas",
            json=checkout_paid,
            headers=webhook_headers,
        ).status_code
        == 200
    )
    checkout_expiry = client.get(
        f"/pagamentos/pedidos/{order_id}", headers=headers
    ).json()["premium_valido_ate"]
    replay = client.post(
        "/pagamentos/webhooks/asaas",
        json=checkout_paid,
        headers=webhook_headers,
    )
    assert replay.json()["duplicate"] is True
    assert (
        client.get(f"/pagamentos/pedidos/{order_id}", headers=headers).json()[
            "premium_valido_ate"
        ]
        == checkout_expiry
    )

    first = client.post(
        "/pagamentos/webhooks/asaas", json=event, headers=webhook_headers
    )
    assert first.status_code == 200
    assert first.json()["duplicate"] is False

    status_response = client.get(f"/pagamentos/pedidos/{order_id}", headers=headers)
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "pago"
    assert status_response.json()["premium_ativo"] is True
    expiry = status_response.json()["premium_valido_ate"]
    assert expiry == checkout_expiry

    duplicate = client.post(
        "/pagamentos/webhooks/asaas", json=event, headers=webhook_headers
    )
    assert duplicate.json()["duplicate"] is True
    assert (
        client.get(f"/pagamentos/pedidos/{order_id}", headers=headers).json()[
            "premium_valido_ate"
        ]
        == expiry
    )
    me = client.get("/usuarios/me", headers=headers).json()
    assert me["premium_ativo"] is True
    assert me["premium_plano"] == "recorrente"
    os.environ.pop("ASAAS_WEBHOOK_TOKEN")


def test_checkout_paid_activates_detached_plan_without_double_grant(monkeypatch):
    token = _register_and_login("checkout-pago@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    monkeypatch.setattr(
        "routers.payments.create_checkout",
        lambda payload: {
            "id": "checkout_detached_123",
            "link": "https://sandbox.asaas.com/checkoutSession/show/id",
            "status": "ACTIVE",
        },
    )
    checkout = client.post(
        "/pagamentos/checkout", headers=headers, json={"plano_id": "avulso"}
    )
    order_id = checkout.json()["pedido_id"]

    os.environ["ASAAS_WEBHOOK_TOKEN"] = "token-webhook-seguro-com-mais-de-32-caracteres"
    webhook_headers = {"asaas-access-token": os.environ["ASAAS_WEBHOOK_TOKEN"]}
    paid = {
        "id": "evt_checkout_paid_123",
        "event": "CHECKOUT_PAID",
        "checkout": {"id": "checkout_detached_123", "status": "PAID"},
    }
    assert (
        client.post(
            "/pagamentos/webhooks/asaas", json=paid, headers=webhook_headers
        ).status_code
        == 200
    )
    first_status = client.get(f"/pagamentos/pedidos/{order_id}", headers=headers).json()
    assert first_status["status"] == "pago"
    assert first_status["premium_ativo"] is True

    payment = {
        "id": "evt_payment_received_same_checkout",
        "event": "PAYMENT_RECEIVED",
        "payment": {
            "id": "pay_same_checkout",
            "externalReference": order_id,
        },
    }
    assert (
        client.post(
            "/pagamentos/webhooks/asaas", json=payment, headers=webhook_headers
        ).status_code
        == 200
    )
    second_status = client.get(
        f"/pagamentos/pedidos/{order_id}", headers=headers
    ).json()
    assert second_status["premium_valido_ate"] == first_status["premium_valido_ate"]
    os.environ.pop("ASAAS_WEBHOOK_TOKEN")


def test_checkout_rejects_unknown_plan():
    token = _register_and_login("plano-invalido@example.com")
    response = client.post(
        "/pagamentos/checkout",
        headers={"Authorization": f"Bearer {token}"},
        json={"plano_id": "vitalicio"},
    )
    assert response.status_code == 422


def test_transparent_pix_returns_qr_code_without_redirect(monkeypatch):
    token = _register_and_login("pix-transparente@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    captured = {}

    monkeypatch.setattr(
        "routers.payments.create_customer",
        lambda payload: {"id": "cus_pix_123"},
    )

    def fake_payment(payload):
        captured.update(payload)
        return {"id": "pay_pix_123", "status": "PENDING"}

    monkeypatch.setattr("routers.payments.create_payment", fake_payment)
    monkeypatch.setattr(
        "routers.payments.get_pix_qr_code",
        lambda payment_id: {
            "encodedImage": "base64-do-qr-code",
            "payload": "000201-pix-copia-cola",
            "expirationDate": "2026-08-12T23:59:00Z",
        },
    )
    response = client.post(
        "/pagamentos/transparente",
        headers=headers,
        json={
            "plano_id": "avulso",
            "pagador": {
                "cpf_cnpj": "123.456.789-01",
                "telefone": "(86) 99999-9999",
                "cep": "64000-000",
                "numero_endereco": "42",
            },
        },
    )

    assert response.status_code == 201
    assert response.json()["forma_pagamento"] == "PIX"
    assert response.json()["pix_qr_code"] == "base64-do-qr-code"
    assert response.json()["pix_copia_cola"] == "000201-pix-copia-cola"
    assert captured["billingType"] == "PIX"
    assert captured["value"] == 25.9
    assert captured["externalReference"] == response.json()["pedido_id"]


def test_transparent_recurring_card_forwards_secrets_without_persisting_them(
    monkeypatch,
):
    token = _register_and_login("cartao-transparente@example.com")
    headers = {
        "Authorization": f"Bearer {token}",
        "x-forwarded-for": "203.0.113.55",
    }
    captured = {}
    monkeypatch.setattr(
        "routers.payments.create_customer",
        lambda payload: {"id": "cus_card_123"},
    )

    def fake_subscription(payload):
        captured.update(payload)
        return {"id": "sub_card_123", "status": "ACTIVE"}

    monkeypatch.setattr("routers.payments.create_subscription", fake_subscription)
    response = client.post(
        "/pagamentos/transparente",
        headers=headers,
        json={
            "plano_id": "recorrente",
            "pagador": {
                "cpf_cnpj": "12345678901",
                "telefone": "86999999999",
                "cep": "64000000",
                "numero_endereco": "42",
                "complemento": "Apto 2",
            },
            "cartao": {
                "titular": "Aluno MedSync",
                "numero": "4444 4444 4444 4444",
                "mes_validade": "12",
                "ano_validade": "2030",
                "ccv": "123",
            },
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "aguardando_confirmacao"
    assert captured["billingType"] == "CREDIT_CARD"
    assert captured["creditCard"]["number"] == "4444444444444444"
    assert captured["remoteIp"] == "203.0.113.55"
    assert captured["cycle"] == "MONTHLY"
    assert "dueDate" not in captured

    order_id = response.json()["pedido_id"]
    order = client.get(f"/pagamentos/pedidos/{order_id}", headers=headers).json()
    serialized = str(order)
    assert "4444444444444444" not in serialized


def test_transparent_checkout_validates_plan_payment_method():
    token = _register_and_login("checkout-validacao@example.com")
    response = client.post(
        "/pagamentos/transparente",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "plano_id": "recorrente",
            "pagador": {
                "cpf_cnpj": "12345678901",
                "telefone": "86999999999",
                "cep": "64000000",
                "numero_endereco": "42",
            },
        },
    )
    assert response.status_code == 422


def test_quarterly_checkout_supports_up_to_three_installments(monkeypatch):
    token = _register_and_login("trimestral@example.com")
    captured = {}

    def fake_checkout(payload):
        captured.update(payload)
        return {
            "id": "checkout_quarterly_123",
            "link": "https://sandbox.asaas.com/checkoutSession/show/quarterly",
            "status": "ACTIVE",
        }

    monkeypatch.setattr("routers.payments.create_checkout", fake_checkout)
    response = client.post(
        "/pagamentos/checkout",
        headers={"Authorization": f"Bearer {token}"},
        json={"plano_id": "trimestral"},
    )

    assert response.status_code == 201
    assert captured["billingTypes"] == ["CREDIT_CARD"]
    assert captured["chargeTypes"] == ["DETACHED", "INSTALLMENT"]
    assert captured["installment"] == {"maxInstallmentCount": 3}
    assert captured["items"][0]["value"] == 65.9


def test_production_never_falls_back_to_sandbox_credentials(monkeypatch):
    from settings import asaas_api_key, asaas_webhook_token

    monkeypatch.setenv("ASAAS_ENVIRONMENT", "production")
    monkeypatch.setenv("ASAAS_API_KEY", "legacy-sandbox-key")
    monkeypatch.setenv("ASAAS_WEBHOOK_TOKEN", "legacy-sandbox-token")
    monkeypatch.delenv("ASAAS_PRODUCTION_API_KEY", raising=False)
    monkeypatch.delenv("ASAAS_PRODUCTION_WEBHOOK_TOKEN", raising=False)

    assert asaas_api_key() is None
    assert asaas_webhook_token() is None

    monkeypatch.setenv("ASAAS_PRODUCTION_API_KEY", "$aact_prod_example")
    monkeypatch.setenv("ASAAS_PRODUCTION_WEBHOOK_TOKEN", "production-token")
    assert asaas_api_key() == "$aact_prod_example"
    assert asaas_webhook_token() == "production-token"


def test_production_checkout_is_restricted_to_pilot(monkeypatch):
    email = "piloto-producao@example.com"
    token = _register_and_login(email)
    headers = {"Authorization": f"Bearer {token}"}
    monkeypatch.setenv("ASAAS_ENVIRONMENT", "production")
    monkeypatch.setenv("PAYMENTS_ENABLED", "false")
    monkeypatch.delenv("PAYMENTS_PILOT_EMAILS", raising=False)

    blocked = client.post(
        "/pagamentos/checkout", headers=headers, json={"plano_id": "avulso"}
    )
    assert blocked.status_code == 503

    monkeypatch.setenv("PAYMENTS_PILOT_EMAILS", email)
    monkeypatch.setattr(
        "routers.payments.create_checkout",
        lambda payload: {
            "id": "checkout_production_pilot",
            "link": "https://asaas.com/checkoutSession/show/pilot",
            "status": "ACTIVE",
        },
    )
    allowed = client.post(
        "/pagamentos/checkout", headers=headers, json={"plano_id": "avulso"}
    )
    assert allowed.status_code == 201


def test_academic_analytics_are_restricted_and_aggregated():
    regular_token = _register_and_login("usuario-comum@example.com")
    assert (
        client.get(
            "/admin/analytics/academico",
            headers={"Authorization": f"Bearer {regular_token}"},
        ).status_code
        == 403
    )

    os.environ["ADMIN_EMAILS"] = "administrador@example.com"
    admin_token = _register_and_login("administrador@example.com")
    current_user = client.get(
        "/usuarios/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert current_user.json()["is_admin"] is True

    response = client.get(
        "/admin/analytics/academico",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    os.environ.pop("ADMIN_EMAILS")

    assert response.status_code == 200
    data = response.json()
    assert data["total_usuarios"] >= 2
    assert data["perfis_academicos_preenchidos"] >= 2
    assert any(item["periodo"] == 6 for item in data["periodos"])
    assert any(
        item["faculdade"] == "Universidade Federal do Maranhão"
        for item in data["faculdades"]
    )
    assert "email" not in response.text


def test_admin_operations_manage_content_metrics_announcements_and_export():
    regular_token = _register_and_login("operacao-comum@example.com")
    assert (
        client.get(
            "/admin/overview",
            headers={"Authorization": f"Bearer {regular_token}"},
        ).status_code
        == 403
    )

    os.environ["ADMIN_EMAILS"] = "operacoes-admin@example.com"
    admin_token = _register_and_login("operacoes-admin@example.com")
    headers = {"Authorization": f"Bearer {admin_token}"}

    overview = client.get("/admin/overview", headers=headers)
    assert overview.status_code == 200
    assert overview.json()["total_usuarios"] >= 2
    assert "retencao_7_dias" in overview.json()

    case_catalog = client.get("/admin/casos", headers=headers)
    assert case_catalog.status_code == 200
    assert len(case_catalog.json()) == 80
    assert {item["nivel_dificuldade"] for item in case_catalog.json()} >= {
        "Intermediário",
        "Crítico",
    }
    second_batch = {
        item["id"]: item
        for item in case_catalog.json()
        if item["id"] in {33, 36, 38, 39, 40}
    }
    assert set(second_batch) == {33, 36, 38, 39, 40}
    assert all(item["rubrica_status"] == "revisada" for item in second_batch.values())
    assert all(item["avaliacao_2_disponivel"] is True for item in second_batch.values())

    new_case = client.post(
        "/admin/casos",
        headers=headers,
        json={
            "titulo": "Dor torácica em adulto jovem",
            "titulo_publico": "Dor torácica ventilatório-dependente em adulto jovem",
            "especialidade": "Cardiologia",
            "nivel_dificuldade": "Médio",
            "historia_clinica": "Paciente adulto jovem com dor torácica ventilatório-dependente.",
            "exame_fisico": "Paciente estável, sem sinais de choque.",
            "status": "rascunho",
            "premium": True,
            "exames": [
                {
                    "codigo": "ecg_admin",
                    "nome": "Eletrocardiograma",
                    "resultado": "Ritmo sinusal sem alterações isquêmicas.",
                    "referencia_adequada": True,
                }
            ],
            "rubrica": None,
        },
    )
    assert new_case.status_code == 201
    assert new_case.json()["premium"] is True
    assert new_case.json()["status"] == "rascunho"
    assert new_case.json()["rubrica_status"] == "rascunho"
    case_payload = new_case.json()
    update_payload = {
        key: case_payload[key]
        for key in (
            "titulo",
            "titulo_publico",
            "especialidade",
            "nivel_dificuldade",
            "historia_clinica",
            "exame_fisico",
            "premium",
            "exames",
            "rubrica",
        )
    }
    update_payload["status"] = "publicado"
    updated_case = client.put(
        f"/admin/casos/{new_case.json()['id']}",
        headers=headers,
        json=update_payload,
    )
    assert updated_case.status_code == 200
    assert updated_case.json()["versao_conteudo"] == 2
    assert updated_case.json()["status"] == "publicado"

    challenge_payload = {
        "id": "admin-radiografia-teste",
        "titulo": "Radiografia cadastrada pelo painel",
        "especialidade": "Radiologia",
        "dificuldade": "Fácil",
        "modalidade": "Radiografia",
        "pergunta": "Qual é o diagnóstico mais provável nesta imagem?",
        "imagem_url": "https://example.com/radiografia.webp",
        "imagem_alt": "Radiografia de tórax para desafio educacional",
        "alternativas": ["Pneumonia", "Pneumotórax", "Derrame", "Normal"],
        "alternativa_correta": 0,
        "diagnostico_correto": "Pneumonia",
        "explicacao": "A consolidação focal com broncograma aéreo favorece pneumonia.",
        "achados_chave": ["Consolidação", "Broncograma aéreo"],
        "fonte_credito": "MedSync",
        "fonte_licenca": "Uso educacional",
        "fonte_url": "#",
        "status": "publicado",
    }
    challenge = client.post("/admin/desafios", headers=headers, json=challenge_payload)
    assert challenge.status_code == 201
    public_challenges = client.get("/desafios-visuais", headers=headers)
    assert public_challenges.status_code == 200
    assert [
        option["texto"] for option in public_challenges.json()[0]["alternativas"]
    ] == challenge_payload["alternativas"]
    assert "alternativa_correta" not in public_challenges.json()[0]
    assert "diagnostico_correto" not in public_challenges.json()[0]
    assert "explicacao" not in public_challenges.json()[0]
    assert "titulo" not in public_challenges.json()[0]

    correction = client.post(
        "/desafios-visuais/admin-radiografia-teste/responder",
        headers=headers,
        json={"alternativa_id": "option-1"},
    )
    assert correction.status_code == 200
    assert correction.json()["correta"] is True
    assert correction.json()["diagnostico_correto"] == "Pneumonia"

    built_in_correction = client.post(
        "/desafios-visuais/desafio-visual-001/responder",
        headers=headers,
        json={"alternativa_id": "pneumonia"},
    )
    assert built_in_correction.status_code == 200
    assert built_in_correction.json()["correta"] is False
    assert built_in_correction.json()["alternativa_correta_id"] == "pneumotorax"

    announcement = client.post(
        "/admin/avisos",
        headers=headers,
        json={
            "titulo": "Nova trilha disponível",
            "mensagem": "Conheça a nova sequência de casos cardiológicos.",
            "tom": "informativo",
            "ativo": True,
        },
    )
    assert announcement.status_code == 201
    assert (
        client.get("/avisos", headers=headers).json()[0]["titulo"]
        == "Nova trilha disponível"
    )

    report = client.get("/admin/relatorios/anonimizado.csv", headers=headers)
    os.environ.pop("ADMIN_EMAILS")
    assert report.status_code == 200
    assert "usuario_anonimo" in report.text
    assert "operacoes-admin@example.com" not in report.text


def test_admin_financial_center_consolidates_orders_revenue_and_subscriptions():
    admin_email = f"financeiro-admin-{uuid.uuid4().hex}@example.com"
    student_email = f"financeiro-aluno-{uuid.uuid4().hex}@example.com"
    os.environ["ADMIN_EMAILS"] = admin_email
    admin_token = _register_and_login(admin_email)
    _register_and_login(student_email)
    headers = {"Authorization": f"Bearer {admin_token}"}
    now = datetime.now(UTC)
    paid_order_id = str(uuid.uuid4())
    failed_order_id = str(uuid.uuid4())

    with SessionLocal() as db:
        student = db.scalar(select(User).where(User.email == student_email))
        db.add_all(
            [
                PaymentOrder(
                    id=paid_order_id,
                    id_usuario=student.id,
                    plano_id="recorrente",
                    valor_centavos=2390,
                    tipo_cobranca="RECURRENT",
                    forma_pagamento="CREDIT_CARD",
                    status="pago",
                    ultimo_pagamento_asaas_id="pay_financeiro_confirmado",
                    created_at=now - timedelta(days=2),
                    updated_at=now - timedelta(days=2),
                    paid_at=now - timedelta(days=2),
                ),
                PaymentOrder(
                    id=failed_order_id,
                    id_usuario=student.id,
                    plano_id="trimestral",
                    valor_centavos=6590,
                    tipo_cobranca="INSTALLMENT",
                    forma_pagamento="CREDIT_CARD",
                    status="recusado",
                    ultimo_pagamento_asaas_id="pay_financeiro_recusado",
                    created_at=now - timedelta(days=1),
                    updated_at=now - timedelta(days=1),
                ),
                UserEntitlement(
                    id_usuario=student.id,
                    plano_id="recorrente",
                    status="ativo",
                    valido_ate=now + timedelta(days=28),
                    renovacao_automatica=True,
                    asaas_subscription_id="sub_financeiro_ativo",
                ),
            ]
        )
        db.flush()
        db.add(
            PaymentGrant(
                asaas_payment_id="pay_financeiro_confirmado",
                pedido_id=paid_order_id,
                granted_at=now - timedelta(days=2),
            )
        )
        db.commit()

    response = client.get("/admin/financeiro", headers=headers)
    os.environ.pop("ADMIN_EMAILS")

    assert response.status_code == 200
    data = response.json()
    assert data["resumo"]["receita_bruta_centavos"] >= 2390
    assert data["resumo"]["receita_liquida_centavos"] >= 2390
    assert data["resumo"]["assinaturas_ativas"] >= 1
    assert data["resumo"]["assinaturas_recorrentes"] >= 1
    assert data["resumo"]["mrr_centavos"] >= 2390
    assert any(item["id"] == paid_order_id for item in data["pedidos"])
    assert any(
        item["pagamento_id"] == "pay_financeiro_confirmado"
        for item in data["pagamentos"]
    )
    assert any(item["pedido_id"] == failed_order_id for item in data["falhas"])
    assert any(
        item["assinatura_asaas_id"] == "sub_financeiro_ativo"
        for item in data["assinaturas"]
    )


def test_admin_synapse_usage_aggregates_tokens_cost_latency_and_models(monkeypatch):
    admin_email = f"synapse-admin-{uuid.uuid4().hex}@example.com"
    student_email = f"synapse-aluno-{uuid.uuid4().hex}@example.com"
    monkeypatch.setenv("ADMIN_EMAILS", admin_email)
    monkeypatch.setenv("OPENAI_ROUTINE_MODEL", "gpt-5.6-luna")
    monkeypatch.setenv("OPENAI_ADVANCED_MODEL", "gpt-5.6-terra")
    admin_token = _register_and_login(admin_email)
    regular_token = _register_and_login(student_email)
    now = datetime.now(UTC)

    with SessionLocal() as db:
        student = db.scalar(select(User).where(User.email == student_email))
        db.add_all(
            [
                UserEntitlement(
                    id_usuario=student.id,
                    plano_id="recorrente",
                    status="ativo",
                    valido_ate=now + timedelta(days=30),
                    renovacao_automatica=True,
                ),
                AIUsageRecord(
                    id_usuario=student.id,
                    operacao="avaliacao_simulacao",
                    modelo="gpt-5.6-luna",
                    input_tokens=1000,
                    cached_input_tokens=200,
                    output_tokens=220,
                    reasoning_tokens=0,
                    total_tokens=1220,
                    duracao_ms=800,
                    custo_estimado_usd=0.0003,
                    response_id=f"resp-{uuid.uuid4().hex}",
                    created_at=now - timedelta(days=1),
                ),
                AIUsageRecord(
                    id_usuario=student.id,
                    operacao="pergunta_pos_simulacao",
                    modelo="gpt-5.6-luna",
                    input_tokens=400,
                    cached_input_tokens=0,
                    output_tokens=100,
                    reasoning_tokens=0,
                    total_tokens=500,
                    duracao_ms=400,
                    custo_estimado_usd=0.0001,
                    response_id=f"resp-{uuid.uuid4().hex}",
                    created_at=now,
                ),
                AIUsageRecord(
                    id_usuario=student.id,
                    operacao="avaliacao_simulacao",
                    modelo="gpt-5.6-terra",
                    input_tokens=1600,
                    cached_input_tokens=400,
                    output_tokens=300,
                    reasoning_tokens=50,
                    total_tokens=1900,
                    duracao_ms=1200,
                    custo_estimado_usd=0.003,
                    response_id=f"resp-{uuid.uuid4().hex}",
                    created_at=now,
                ),
            ]
        )
        db.commit()
        active_subscriber_count = db.scalar(
            select(func.count())
            .select_from(UserEntitlement)
            .where(
                UserEntitlement.status == "ativo",
                UserEntitlement.valido_ate > now,
            )
        )

    forbidden = client.get(
        "/admin/synapse/consumo?dias=7",
        headers={"Authorization": f"Bearer {regular_token}"},
    )
    response = client.get(
        "/admin/synapse/consumo?dias=7",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert forbidden.status_code == 403
    assert response.status_code == 200
    data = response.json()
    assert data["periodo_dias"] == 7
    assert data["resumo"]["chamadas"] == 3
    assert data["resumo"]["usuarios_ativos"] == 1
    assert data["resumo"]["casos_avaliados"] == 2
    assert data["resumo"]["assinantes_ativos"] == active_subscriber_count
    assert data["resumo"]["chamadas_assinantes"] == 3
    assert data["resumo"]["chamadas_por_assinante"] == round(
        3 / active_subscriber_count, 2
    )
    assert data["resumo"]["input_tokens"] == 3000
    assert data["resumo"]["cached_input_tokens"] == 600
    assert data["resumo"]["output_tokens"] == 620
    assert data["resumo"]["total_tokens"] == 3620
    assert data["resumo"]["taxa_cache_percentual"] == 20
    assert data["resumo"]["duracao_media_ms"] == 800
    assert data["resumo"]["custo_estimado_usd"] == pytest.approx(0.0034)
    assert data["resumo"]["custo_medio_por_caso_usd"] == pytest.approx(0.00165)
    assert data["resumo"]["custo_medio_por_usuario_usd"] == pytest.approx(0.0034)
    assert {item["chave"] for item in data["por_modelo"]} == {
        "gpt-5.6-luna",
        "gpt-5.6-terra",
    }
    assert data["usuarios_mais_ativos"][0]["email"] == student_email
    assert data["configuracao"]["modelo_rotina"] == "gpt-5.6-luna"
    assert "franquia" not in response.text.lower()


def test_protected_routes_require_a_valid_token():
    assert client.get("/casos-clinicos/").status_code == 401
    assert (
        client.get(
            "/casos-clinicos/", headers={"Authorization": "Bearer token-invalido"}
        ).status_code
        == 401
    )


def test_progress_is_persistent_and_isolated_by_user():
    first_token = _register_and_login("primeiro@example.com")
    second_token = _register_and_login("segundo@example.com")

    payload = {
        "id_caso": 1,
        "respostas_usuario": {"hipotese_diagnostica": "Pericardite"},
        "pontuacao": 85,
    }
    response = client.post(
        "/progresso/registrar",
        json=payload,
        headers={"Authorization": f"Bearer {first_token}"},
    )
    assert response.status_code == 201
    assert response.json()["id_usuario"] != 0

    first_progress = client.get(
        "/progresso/meu", headers={"Authorization": f"Bearer {first_token}"}
    )
    second_progress = client.get(
        "/progresso/meu", headers={"Authorization": f"Bearer {second_token}"}
    )
    assert len(first_progress.json()) == 1
    assert second_progress.json() == []


def test_user_can_reset_only_their_own_progress_without_deleting_account():
    first_token = _register_and_login("reset@example.com")
    second_token = _register_and_login("preservado@example.com")
    payload = {
        "id_caso": 1,
        "respostas_usuario": {"hipotese_diagnostica": "Pericardite"},
        "pontuacao": 85,
    }

    for token in (first_token, second_token):
        response = client.post(
            "/progresso/registrar",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 201

    reset = client.delete(
        "/progresso/meu",
        headers={"Authorization": f"Bearer {first_token}"},
    )
    assert reset.status_code == 200
    assert reset.json() == {
        "registros_removidos": 1,
        "message": "Estatísticas redefinidas com sucesso.",
    }

    first_progress = client.get(
        "/progresso/meu", headers={"Authorization": f"Bearer {first_token}"}
    )
    second_progress = client.get(
        "/progresso/meu", headers={"Authorization": f"Bearer {second_token}"}
    )
    current_user = client.get(
        "/usuarios/me", headers={"Authorization": f"Bearer {first_token}"}
    )

    assert first_progress.json() == []
    assert len(second_progress.json()) == 1
    assert current_user.status_code == 200
    assert current_user.json()["email"] == "reset@example.com"


def test_v2_case_is_identified_in_case_catalog():
    token = _register_and_login("catalogo-v2@example.com")
    response = client.get(
        "/casos-clinicos/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    cases = response.json()
    pilot = next(case for case in cases if case["id"] == 8)
    final_case = next(case for case in cases if case["id"] == 31)
    assert pilot["titulo"].startswith("Caso #008 – ")
    assert "tromboembolismo" not in pilot["titulo"].lower()
    assert "pericardite" not in final_case["titulo"].lower()
    assert pilot["avaliacao_2_disponivel"] is True
    assert final_case["avaliacao_2_disponivel"] is True

    detail = client.get(
        "/casos-clinicos/8",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail.status_code == 200
    vitals = {item["id"]: item for item in detail.json()["sinais_vitais"]}
    assert vitals["fr"]["valor"] == "27"
    assert vitals["fr"]["status"] == "alterado"
    assert vitals["spo2"]["valor"] == "83"
    assert vitals["spo2"]["status"] == "alterado"
    assert vitals["pa"]["status"] == "nao_informado"


def test_first_rubric_v2_batch_is_available_and_has_clinical_sources():
    token = _register_and_login("lote-rubricas@example.com")
    response = client.get(
        "/casos-clinicos/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    availability = {
        case["id"]: case["avaliacao_2_disponivel"] for case in response.json()
    }
    assert all(availability[case_id] for case_id in {6, 7, 8, 11, 12})
    assert all(availability[case_id] for case_id in range(1, 66))

    with SessionLocal() as db:
        for case_id in {6, 7, 8, 11, 12}:
            rubric = db.scalar(
                select(ClinicalRubric).where(ClinicalRubric.id_caso == case_id)
            )
            assert rubric is not None
            assert rubric.versao == 8
            assert rubric.definicao["objetivos_aprendizagem"]
            assert rubric.definicao["criterios_seguranca"]
            assert rubric.definicao["fontes_clinicas"]


def test_first_feedback_expansion_batch_is_structured_and_clinically_corrected():
    token = _register_and_login("primeiro-lote-feedback@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    batch_ids = {14, 18, 19, 21, 22}

    response = client.get("/casos-clinicos/", headers=headers)
    assert response.status_code == 200
    availability = {
        case["id"]: case["avaliacao_2_disponivel"] for case in response.json()
    }
    assert all(availability[case_id] for case_id in batch_ids)

    with SessionLocal() as db:
        rubrics = list(
            db.scalars(
                select(ClinicalRubric).where(ClinicalRubric.id_caso.in_(batch_ids))
            ).all()
        )
        assert len(rubrics) == len(batch_ids)
        assert all(rubric.status == "revisada" for rubric in rubrics)
        assert all(rubric.versao == 8 for rubric in rubrics)
        for rubric in rubrics:
            ClinicalRubricDefinition.model_validate(rubric.definicao)
            assert rubric.definicao["criterios_seguranca"]
            assert rubric.definicao["desfechos_conduta"]
            assert rubric.definicao["fontes_clinicas"]

    herpes = client.get("/casos-clinicos/18", headers=headers)
    assert herpes.status_code == 200
    herpes_exams = {exam["id"]: exam for exam in herpes.json()["exames_disponiveis"]}
    assert herpes_exams["pcr_hsv_lesao"]["correto"] is True
    assert herpes_exams["raspado"]["correto"] is False

    gonorrhea = client.get("/casos-clinicos/19", headers=headers)
    assert gonorrhea.status_code == 200
    gonorrhea_exams = {
        exam["id"]: exam for exam in gonorrhea.json()["exames_disponiveis"]
    }
    assert gonorrhea_exams["pcr_gonococo"]["correto"] is True

    bells_palsy = client.get("/casos-clinicos/21", headers=headers)
    assert bells_palsy.status_code == 200
    bell_exams = {exam["id"]: exam for exam in bells_palsy.json()["exames_disponiveis"]}
    assert bell_exams["avaliacao_clinica_bell"]["correto"] is True
    assert bell_exams["rm_cranio"]["correto"] is False


def test_first_feedback_expansion_batch_generates_complete_safe_feedback():
    token = _register_and_login("primeiro-lote-simulacoes@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    submissions = {
        14: {
            "exames_solicitados": [
                "amilase_lipase",
                "usg_abdome",
                "funcao_renal_hepatica_eletrolitos",
            ],
            "hipotese_diagnostica": "Pancreatite aguda biliar",
            "conduta_proposta": (
                "Internar, avaliar gravidade e falência orgânica, monitorização e "
                "diurese; hidratação venosa com Ringer lactato, analgesia e "
                "alimentação precoce conforme tolerância. Avaliar colangite e provas "
                "hepáticas e programar colecistectomia na mesma internação."
            ),
        },
        18: {
            "exames_solicitados": ["pcr_hsv_lesao", "hiv_sifilis"],
            "hipotese_diagnostica": "Primeiro episódio de herpes genital",
            "conduta_proposta": (
                "Iniciar aciclovir por 7 a 10 dias, analgesia e hidratação. Testar "
                "HIV e sífilis, investigar coinfecção e retenção urinária, orientar "
                "parceiro, preservativo e abstinência durante as lesões."
            ),
        },
        19: {
            "exames_solicitados": [
                "pcr_gonococo",
                "pcr_clamidia",
                "hiv_sifilis",
            ],
            "hipotese_diagnostica": "Cervicite gonocócica",
            "conduta_proposta": (
                "Ceftriaxona 500 mg IM em dose única; tratar clamídia se não "
                "excluída. Testar HIV e sífilis, avaliar DIP, dor pélvica e gestação, "
                "tratar parceiro, orientar abstinência por 7 dias e reteste em 3 meses."
            ),
        },
        21: {
            "exames_solicitados": ["avaliacao_clinica_bell"],
            "hipotese_diagnostica": "Paralisia de Bell",
            "conduta_proposta": (
                "Realizar exame neurológico e iniciar prednisona dentro de 72 horas. "
                "Fazer proteção ocular com lágrima artificial e pomada oftálmica; "
                "reavaliar novos sintomas neurológicos e encaminhar se necessário."
            ),
        },
        22: {
            "exames_solicitados": ["clinico"],
            "hipotese_diagnostica": "Migrânea sem aura",
            "conduta_proposta": (
                "Pesquisar sinais de alarme, cefaleia súbita, déficit neurológico, "
                "febre e papiledema. Tratar no início com sumatriptana e naproxeno, "
                "antiemético e repouso; manter diário de cefaleia, evitar opioide e "
                "orientar sobre uso excessivo de analgésico."
            ),
        },
    }

    for case_id, submission in submissions.items():
        response = client.post(
            f"/simulacoes/{case_id}/finalizar",
            json=submission,
            headers=headers,
        )
        assert response.status_code == 201, (case_id, response.text)
        result = response.json()
        assert result["nivel_conduta"] == "adequada", case_id
        assert result["pontuacao_total"] >= 90, case_id
        assert result["feedback"]["sintese_raciocinio"], case_id
        assert result["feedback"]["feedback_seguranca"], case_id
        assert result["feedback"]["reacao_paciente"], case_id
        assert result["feedback"]["desfecho_clinico"], case_id
        assert result["feedback"]["plano_pessoal_melhoria"], case_id


def test_second_feedback_expansion_batch_is_structured_and_clinically_corrected():
    token = _register_and_login("segundo-lote-feedback@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    batch_ids = {2, 5, 15, 16, 17}

    response = client.get("/casos-clinicos/", headers=headers)
    assert response.status_code == 200
    availability = {
        case["id"]: case["avaliacao_2_disponivel"] for case in response.json()
    }
    assert all(availability[case_id] for case_id in batch_ids)

    with SessionLocal() as db:
        rubrics = list(
            db.scalars(
                select(ClinicalRubric).where(ClinicalRubric.id_caso.in_(batch_ids))
            ).all()
        )
        assert len(rubrics) == len(batch_ids)
        assert all(rubric.status == "revisada" for rubric in rubrics)
        assert all(rubric.versao == 8 for rubric in rubrics)
        for rubric in rubrics:
            ClinicalRubricDefinition.model_validate(rubric.definicao)
            assert rubric.definicao["objetivos_aprendizagem"]
            assert rubric.definicao["criterios_seguranca"]
            assert rubric.definicao["desfechos_conduta"]
            assert rubric.definicao["fontes_clinicas"]

    fibroid = client.get("/casos-clinicos/5", headers=headers)
    assert fibroid.status_code == 200
    fibroid_exams = {exam["id"]: exam for exam in fibroid.json()["exames_disponiveis"]}
    assert "primeira linha" in fibroid_exams["usg_tv"]["resultado"].lower()
    assert fibroid_exams["ferritina"]["correto"] is True

    adenomyosis = client.get("/casos-clinicos/15", headers=headers)
    assert adenomyosis.status_code == 200
    adenomyosis_exams = {
        exam["id"]: exam for exam in adenomyosis.json()["exames_disponiveis"]
    }
    assert adenomyosis_exams["usg_tv_adenomiose"]["correto"] is True
    assert "complementar" in adenomyosis_exams["rm_pelvica"]["resultado"].lower()

    turner = client.get("/casos-clinicos/16", headers=headers)
    assert turner.status_code == 200
    turner_exams = {exam["id"]: exam for exam in turner.json()["exames_disponiveis"]}
    assert turner_exams["imagem_cardio_aorta"]["correto"] is True
    assert turner_exams["usg_renal"]["correto"] is True

    endometriosis = client.get("/casos-clinicos/17", headers=headers)
    assert endometriosis.status_code == 200
    endometriosis_exams = {
        exam["id"]: exam for exam in endometriosis.json()["exames_disponiveis"]
    }
    assert endometriosis_exams["ca125"]["correto"] is False
    assert "confirmar ou excluir" in endometriosis_exams["ca125"]["resultado"]


def test_second_feedback_expansion_batch_generates_complete_safe_feedback():
    token = _register_and_login("segundo-lote-simulacoes@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    submissions = {
        2: {
            "exames_solicitados": [
                "mapa",
                "lab_renal",
                "urina_albumina",
                "risco_cv",
            ],
            "hipotese_diagnostica": "Hipertensão arterial mascarada com lesão de órgão-alvo",
            "conduta_proposta": (
                "Reconhecer retinopatia e hipertrofia ventricular como lesão de "
                "órgão-alvo e estratificar risco cardiovascular. Iniciar "
                "anti-hipertensivo individualizado, orientar redução de sal e "
                "atividade física e acompanhar com MAPA ou pressão domiciliar, "
                "reavaliando função renal e eletrólitos."
            ),
        },
        5: {
            "exames_solicitados": ["beta_hcg", "hemo", "ferritina", "usg_tv"],
            "hipotese_diagnostica": "Sangramento uterino anormal por leiomioma uterino com anemia ferropriva",
            "conduta_proposta": (
                "Avaliar sinais vitais e estabilidade hemodinâmica, sangramento "
                "ativo e beta-HCG. Controlar o fluxo com ácido tranexâmico ou "
                "progestagênio conforme contraindicações, fazer reposição de ferro "
                "e avaliação ginecológica considerando desejo reprodutivo e "
                "possível miomectomia."
            ),
        },
        15: {
            "exames_solicitados": [
                "beta_hcg",
                "hemo",
                "ferritina",
                "usg_tv_adenomiose",
            ],
            "hipotese_diagnostica": "Adenomiose uterina com anemia ferropriva",
            "conduta_proposta": (
                "Discutir SIU-LNG com levonorgestrel ou outra opção individualizada "
                "para dor e sangramento, fazer reposição de ferro e reavaliar "
                "hemoglobina. Considerar desejo reprodutivo e decisão compartilhada, "
                "com avaliação ginecológica pela anemia importante."
            ),
        },
        16: {
            "exames_solicitados": [
                "cariotipo",
                "hormonios",
                "imagem_cardio_aorta",
                "usg_renal",
                "tireoide_metabolico",
            ],
            "hipotese_diagnostica": "Síndrome de Turner 45,X com insuficiência ovariana",
            "conduta_proposta": (
                "Iniciar reposição estrogênica com estradiol e planejar adicionar "
                "progestagênio. Realizar ecocardiograma e avaliar aorta e coarctação "
                "antes de gestação. Organizar seguimento multidisciplinar com função "
                "tireoidiana, saúde óssea e ultrassom renal, além de aconselhamento "
                "reprodutivo e discussão do risco gestacional."
            ),
        },
        17: {
            "exames_solicitados": ["usg_tv_preparo"],
            "hipotese_diagnostica": "Endometriose profunda",
            "conduta_proposta": (
                "Explicar que CA-125 não confirma endometriose. Iniciar tratamento "
                "empírico com progestagênio e analgesia, reavaliar dor e encaminhar "
                "à ginecologia especializada. Fazer decisão compartilhada conforme "
                "desejo reprodutivo e fertilidade, reservando laparoscopia se falha "
                "do tratamento ou imagem negativa."
            ),
        },
    }

    for case_id, submission in submissions.items():
        response = client.post(
            f"/simulacoes/{case_id}/finalizar",
            json=submission,
            headers=headers,
        )
        assert response.status_code == 201, (case_id, response.text)
        result = response.json()
        assert result["nivel_conduta"] == "adequada", case_id
        assert result["pontuacao_total"] >= 90, case_id
        assert result["feedback"]["sintese_raciocinio"], case_id
        assert result["feedback"]["feedback_seguranca"], case_id
        assert result["feedback"]["reacao_paciente"], case_id
        assert result["feedback"]["desfecho_clinico"], case_id
        assert result["feedback"]["plano_pessoal_melhoria"], case_id


def test_third_feedback_expansion_batch_is_structured_and_clinically_corrected():
    token = _register_and_login("terceiro-lote-feedback@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    batch_ids = {1, 3, 4, 9, 10}

    response = client.get("/casos-clinicos/", headers=headers)
    assert response.status_code == 200
    availability = {
        case["id"]: case["avaliacao_2_disponivel"] for case in response.json()
    }
    assert all(availability[case_id] for case_id in batch_ids)

    with SessionLocal() as db:
        rubrics = list(
            db.scalars(
                select(ClinicalRubric).where(ClinicalRubric.id_caso.in_(batch_ids))
            ).all()
        )
        assert len(rubrics) == len(batch_ids)
        assert all(rubric.status == "revisada" for rubric in rubrics)
        for rubric in rubrics:
            ClinicalRubricDefinition.model_validate(rubric.definicao)
            assert rubric.definicao["criterios_seguranca"]
            assert rubric.definicao["desfechos_conduta"]
            assert rubric.definicao["fontes_clinicas"]

    chest_pain = client.get("/casos-clinicos/1", headers=headers)
    assert chest_pain.status_code == 200
    chest_exams = {exam["id"]: exam for exam in chest_pain.json()["exames_disponiveis"]}
    assert chest_exams["confirmacao_histologica"]["correto"] is True
    assert chest_exams["pet_ct_rotina"]["correto"] is False

    amyloidosis = client.get("/casos-clinicos/3", headers=headers)
    assert amyloidosis.status_code == 200
    amyloid_exams = {
        exam["id"]: exam for exam in amyloidosis.json()["exames_disponiveis"]
    }
    assert "AL lambda" in amyloid_exams["biopsia_amiloide"]["resultado"]
    assert amyloid_exams["cintilografia_isolada"]["correto"] is False

    leprosy_reaction = client.get("/casos-clinicos/10", headers=headers)
    assert leprosy_reaction.status_code == 200
    leprosy_exams = {
        exam["id"]: exam for exam in leprosy_reaction.json()["exames_disponiveis"]
    }
    assert leprosy_exams["avaliacao_funcao_neural"]["correto"] is True
    assert leprosy_exams["baciloscopia"]["correto"] is False
    assert "DRESS" in leprosy_exams["revisao_medicamentos_renal"]["resultado"]


def test_third_feedback_expansion_batch_generates_complete_safe_feedback():
    token = _register_and_login("terceiro-lote-simulacoes@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    submissions = {
        1: {
            "exames_solicitados": [
                "tc_torax",
                "marcadores_tumorais",
                "tc_abdome_pelve",
                "confirmacao_histologica",
            ],
            "hipotese_diagnostica": "Recidiva de seminoma com massa mediastinal",
            "conduta_proposta": (
                "Avaliar estabilidade e excluir síndrome coronariana e embolia "
                "pulmonar. Dosar AFP, beta-HCG e LDH, completar estadiamento com "
                "TC de abdome, controlar com analgesia e encaminhar à oncologia e "
                "cirurgia torácica para biópsia e confirmação histológica."
            ),
        },
        3: {
            "exames_solicitados": [
                "imunofixacao_cadeias_leves",
                "biopsia_mo",
                "biopsia_amiloide",
                "biomarcadores_cardiorrenais",
            ],
            "hipotese_diagnostica": "Amiloidose AL cardíaca associada a mieloma múltiplo",
            "conduta_proposta": (
                "Internação para diurético e avaliar transfusão pela anemia grave. "
                "Confirmar com biópsia, vermelho Congo, tipagem do amiloide e cadeias "
                "leves livres. Acionar hematologia e cardiologia especializada para "
                "tratamento do clone plasmocitário com bortezomibe conforme "
                "estratificação cardíaca."
            ),
        },
        4: {
            "exames_solicitados": [
                "eco",
                "troponina_bnp",
                "rm_cardiaca",
                "atividade_les_renal",
                "investigacao_infecciosa",
            ],
            "hipotese_diagnostica": "Miopericardite lúpica com insuficiência cardíaca de fração reduzida",
            "conduta_proposta": (
                "Internação com telemetria e monitorização cardíaca, diurético e "
                "tratamento da insuficiência cardíaca conforme tolerância. Fazer "
                "hemoculturas e excluir infecção antes de imunossupressão; discutir "
                "corticosteroide em alta dose com reumatologia e cardiologia."
            ),
        },
        9: {
            "exames_solicitados": [
                "clinico",
                "avaliacao_ocular_neurologica",
                "audiometria",
            ],
            "hipotese_diagnostica": "Síndrome de Ramsay Hunt por herpes zóster ótico",
            "conduta_proposta": (
                "Iniciar valaciclovir e prednisona após avaliar contraindicações. "
                "Fazer proteção ocular com lágrima artificial e oclusão noturna, "
                "analgesia, controle da vertigem e encaminhar ao otorrino para "
                "audiometria e seguimento."
            ),
        },
        10: {
            "exames_solicitados": [
                "avaliacao_funcao_neural",
                "hemo",
                "funcao_hepatica",
                "revisao_medicamentos_renal",
            ],
            "hipotese_diagnostica": "Reação hansênica tipo 1 com neurite",
            "conduta_proposta": (
                "Documentar função neural, sensibilidade e força muscular e iniciar "
                "prednisona em tratamento supervisionado com desmame gradual. "
                "Investigar DRESS e hipersensibilidade à dapsona pela hepatite e "
                "eosinofilia, suspendendo dapsona se confirmada; encaminhar ao "
                "serviço de referência para ajustar a PQT."
            ),
        },
    }

    for case_id, submission in submissions.items():
        response = client.post(
            f"/simulacoes/{case_id}/finalizar",
            json=submission,
            headers=headers,
        )
        assert response.status_code == 201, (case_id, response.text)
        result = response.json()
        assert result["nivel_conduta"] == "adequada", case_id
        assert result["pontuacao_total"] >= 90, case_id
        assert result["feedback"]["sintese_raciocinio"], case_id
        assert result["feedback"]["feedback_seguranca"], case_id
        assert result["feedback"]["reacao_paciente"], case_id
        assert result["feedback"]["desfecho_clinico"], case_id
        assert result["feedback"]["plano_pessoal_melhoria"], case_id


def test_fourth_feedback_expansion_batch_is_structured_and_clinically_corrected():
    token = _register_and_login("quarto-lote-feedback@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    batch_ids = {13, 20, 23, 24, 25}

    response = client.get("/casos-clinicos/", headers=headers)
    assert response.status_code == 200
    availability = {
        case["id"]: case["avaliacao_2_disponivel"] for case in response.json()
    }
    assert all(availability[case_id] for case_id in batch_ids)

    with SessionLocal() as db:
        rubrics = list(
            db.scalars(
                select(ClinicalRubric).where(ClinicalRubric.id_caso.in_(batch_ids))
            ).all()
        )
        assert len(rubrics) == len(batch_ids)
        assert all(rubric.status == "revisada" for rubric in rubrics)
        assert all(rubric.versao == 8 for rubric in rubrics)
        for rubric in rubrics:
            ClinicalRubricDefinition.model_validate(rubric.definicao)
            assert rubric.definicao["objetivos_aprendizagem"]
            assert rubric.definicao["criterios_seguranca"]
            assert rubric.definicao["desfechos_conduta"]
            assert rubric.definicao["fontes_clinicas"]

    psc = client.get("/casos-clinicos/13", headers=headers)
    assert psc.status_code == 200
    psc_exams = {exam["id"]: exam for exam in psc.json()["exames_disponiveis"]}
    assert psc_exams["colangio_rm"]["correto"] is True
    assert psc_exams["anticorpos"]["correto"] is False
    assert "terapêutica" in psc_exams["cpre"]["nome"].lower()

    locked_in = client.get("/casos-clinicos/20", headers=headers)
    assert locked_in.status_code == 200
    locked_exams = {exam["id"]: exam for exam in locked_in.json()["exames_disponiveis"]}
    assert locked_exams["angio_tc_basilar"]["correto"] is True
    assert locked_exams["puncao_lombar"]["correto"] is False

    west = client.get("/casos-clinicos/23", headers=headers)
    assert west.status_code == 200
    west_exams = {exam["id"]: exam for exam in west.json()["exames_disponiveis"]}
    assert west_exams["video_eeg_sono"]["correto"] is True
    assert west_exams["rm_encefalo"]["correto"] is True
    assert west_exams["tc_cranio"]["correto"] is False

    migraine = client.get("/casos-clinicos/24", headers=headers)
    assert migraine.status_code == 200
    migraine_exams = {
        exam["id"]: exam for exam in migraine.json()["exames_disponiveis"]
    }
    assert migraine_exams["avaliacao_tempo_neuro_glicemia"]["correto"] is True

    status = client.get("/casos-clinicos/25", headers=headers)
    assert status.status_code == 200
    status_exams = {exam["id"]: exam for exam in status.json()["exames_disponiveis"]}
    assert status_exams["glicemia_capilar"]["correto"] is True
    assert "sem atrasar" in status_exams["eeg"]["resultado"].lower()


def test_fourth_feedback_expansion_batch_generates_complete_safe_feedback():
    token = _register_and_login("quarto-lote-simulacoes@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    submissions = {
        13: {
            "exames_solicitados": [
                "funcao_hepatica",
                "hemoculturas_lactato",
                "usg_abdome",
                "colangio_rm",
                "cpre",
            ],
            "hipotese_diagnostica": (
                "Colangite bacteriana aguda em colangite esclerosante primária"
            ),
            "conduta_proposta": (
                "Internar, avaliar sepse, colher hemoculturas e lactato, fazer "
                "reposição volêmica e monitorização. Iniciar antibiótico com "
                "cobertura biliar e acionar hepatologia e endoscopia para CPRE "
                "terapêutica com drenagem biliar da estenose dominante. Manter "
                "seguimento para colangiocarcinoma, retocolite e transplante hepático."
            ),
        },
        20: {
            "exames_solicitados": [
                "glicemia_abc",
                "tc_cranio",
                "angio_tc_basilar",
                "rm_difusao",
            ],
            "hipotese_diagnostica": (
                "Síndrome do encarceramento por oclusão da artéria basilar"
            ),
            "conduta_proposta": (
                "Ativar protocolo de AVC, proteger via aérea, verificar glicemia e "
                "monitorizar. Avaliar trombólise na janela terapêutica e transferir "
                "para centro de AVC para trombectomia mecânica urgente. Reconhecer "
                "consciência preservada, estabelecer comunicação por movimentos "
                "oculares verticais e prevenir broncoaspiração."
            ),
        },
        23: {
            "exames_solicitados": [
                "video_eeg_sono",
                "rm_encefalo",
                "avaliacao_etiologica",
            ],
            "hipotese_diagnostica": "Síndrome de West com espasmos e hipsarritmia",
            "conduta_proposta": (
                "Encaminhar com urgência à neuropediatria e iniciar prednisolona em "
                "alta dose associada a vigabatrina conforme protocolo. Investigar "
                "esclerose tuberosa com ressonância de encéfalo e teste genético. "
                "Confirmar cessação dos espasmos e repetir vídeo-EEG em 14 dias, "
                "acompanhando o desenvolvimento."
            ),
        },
        24: {
            "exames_solicitados": [
                "avaliacao_tempo_neuro_glicemia",
                "tc_cranio",
                "angio_rm_se_atipica",
            ],
            "hipotese_diagnostica": "Migrânea com aura de linguagem",
            "conduta_proposta": (
                "Ativar protocolo de AVC e registrar tempo de início para excluir AVC "
                "antes de confirmar aura. Após a avaliação, tratar com sumatriptana, "
                "naproxeno e antiemético. Suspender contraceptivo combinado, evitar "
                "estrogênio e discutir método sem estrogênio. Manter diário de "
                "cefaleia e retornar se houver déficit persistente."
            ),
        },
        25: {
            "exames_solicitados": [
                "glicemia_capilar",
                "laboratorio_causa_status",
                "eeg",
                "tc_pos_estabilizacao",
            ],
            "hipotese_diagnostica": "Estado de mal epiléptico convulsivo",
            "conduta_proposta": (
                "Proteger via aérea, oferecer oxigênio, monitorização, acesso venoso "
                "e glicemia. Administrar lorazepam em dose plena e, se persistir, "
                "carregar levetiracetam. Se evoluir como estado refratário, realizar "
                "intubação, encaminhar à UTI, iniciar anestésico contínuo e EEG contínuo."
            ),
        },
    }

    for case_id, submission in submissions.items():
        response = client.post(
            f"/simulacoes/{case_id}/finalizar",
            json=submission,
            headers=headers,
        )
        assert response.status_code == 201, (case_id, response.text)
        result = response.json()
        assert result["nivel_conduta"] == "adequada", case_id
        assert result["pontuacao_total"] >= 90, case_id
        assert result["feedback"]["sintese_raciocinio"], case_id
        assert result["feedback"]["feedback_seguranca"], case_id
        assert result["feedback"]["reacao_paciente"], case_id
        assert result["feedback"]["desfecho_clinico"], case_id
        assert result["feedback"]["plano_pessoal_melhoria"], case_id


def test_fifth_feedback_expansion_batch_is_structured_and_clinically_corrected():
    token = _register_and_login("quinto-lote-feedback@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    batch_ids = {26, 27, 28, 29, 30}

    response = client.get("/casos-clinicos/", headers=headers)
    assert response.status_code == 200
    availability = {
        case["id"]: case["avaliacao_2_disponivel"] for case in response.json()
    }
    assert all(availability[case_id] for case_id in batch_ids)

    with SessionLocal() as db:
        rubrics = list(
            db.scalars(
                select(ClinicalRubric).where(ClinicalRubric.id_caso.in_(batch_ids))
            ).all()
        )
        assert len(rubrics) == len(batch_ids)
        assert all(rubric.status == "revisada" for rubric in rubrics)
        for rubric in rubrics:
            ClinicalRubricDefinition.model_validate(rubric.definicao)
            assert rubric.definicao["criterios_seguranca"]
            assert rubric.definicao["desfechos_conduta"]
            assert rubric.definicao["fontes_clinicas"]

    stroke = client.get("/casos-clinicos/26", headers=headers)
    stroke_exams = {exam["id"]: exam for exam in stroke.json()["exames_disponiveis"]}
    assert stroke_exams["angio_tc"]["correto"] is True
    assert "sem hemorragia" in stroke_exams["tc_cranio"]["resultado"].lower()

    chagas = client.get("/casos-clinicos/27", headers=headers)
    chagas_exams = {exam["id"]: exam for exam in chagas.json()["exames_disponiveis"]}
    assert chagas_exams["avaliacao_nutricional"]["correto"] is True
    assert "não diagnostica" in chagas_exams["albumina"]["resultado"].lower()

    celiac = client.get("/casos-clinicos/28", headers=headers)
    celiac_exams = {exam["id"]: exam for exam in celiac.json()["exames_disponiveis"]}
    assert celiac_exams["iga_total"]["correto"] is True
    assert (
        "não dispensa biópsia"
        in celiac_exams["ema_segunda_amostra"]["resultado"].lower()
    )

    scarlet = client.get("/casos-clinicos/29", headers=headers)
    scarlet_exams = {exam["id"]: exam for exam in scarlet.json()["exames_disponiveis"]}
    assert scarlet_exams["avaliacao_exantema"]["correto"] is True
    assert scarlet_exams["cultura_orofaringe"]["correto"] is False

    rheumatic = client.get("/casos-clinicos/30", headers=headers)
    rheumatic_exams = {
        exam["id"]: exam for exam in rheumatic.json()["exames_disponiveis"]
    }
    assert rheumatic_exams["ecg"]["correto"] is True
    assert "isoladamente não confirma" in rheumatic_exams["aslo"]["resultado"].lower()


def test_fifth_feedback_expansion_batch_generates_complete_safe_feedback():
    token = _register_and_login("quinto-lote-simulacoes@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    submissions = {
        26: {
            "exames_solicitados": [
                "glicemia_abc",
                "nihss_tempo",
                "tc_cranio",
                "angio_tc",
                "rm_difusao",
            ],
            "hipotese_diagnostica": "AVC isquêmico de circulação posterior",
            "conduta_proposta": (
                "Ativar protocolo de AVC, proteger via aérea e verificar glicemia. "
                "Avaliar trombólise na janela terapêutica e trombectomia em centro de "
                "AVC. Tratar convulsão ativa, fazer avaliação da deglutição e, após "
                "excluir hemorragia, iniciar antiagregante e estatina."
            ),
        },
        27: {
            "exames_solicitados": [
                "avaliacao_nutricional",
                "esofagograma",
                "avaliacao_degluticao",
                "laboratorio_refeeding",
                "enema_opaco",
            ],
            "hipotese_diagnostica": (
                "Doença de Chagas digestiva com megaesôfago e megacólon"
            ),
            "conduta_proposta": (
                "Iniciar realimentação cautelosa com tiamina, fósforo e eletrólitos. "
                "Adaptar consistência, pequenas refeições e avaliar com fonoaudiologia "
                "para prevenir aspiração. Acionar gastroenterologia para dilatação ou "
                "miotomia, tratar megacólon com laxativo e acompanhar nutricionista, "
                "suplementação e peso semanal."
            ),
        },
        28: {
            "exames_solicitados": [
                "anti_ttg",
                "iga_total",
                "hemo_ferritina",
                "biopsia_duodeno",
            ],
            "hipotese_diagnostica": "Doença celíaca",
            "conduta_proposta": (
                "Manter glúten até confirmar o diagnóstico e encaminhar à "
                "gastroenterologia pediátrica para biópsia duodenal. Após confirmação, "
                "iniciar dieta sem glúten com nutricionista e orientar contaminação "
                "cruzada. Repor ferro conforme ferritina e acompanhar peso e crescimento."
            ),
        },
        29: {
            "exames_solicitados": [
                "avaliacao_exantema",
                "teste_rapido_strepto",
                "avaliacao_cardio_renal",
            ],
            "hipotese_diagnostica": "Escarlatina",
            "conduta_proposta": (
                "Avaliar dispneia e edema com oximetria, função renal e pesquisa de "
                "insuficiência cardíaca. Tratar com amoxicilina por 10 dias, hidratação "
                "e paracetamol. Orientar higiene, retorno se piora e afastamento da escola "
                "até estar afebril e completar 24 horas de antibiótico."
            ),
        },
        30: {
            "exames_solicitados": [
                "eco",
                "aslo_anti_dnase",
                "vhs_pcr",
                "ecg",
                "raiox_bnp_funcao_renal",
            ],
            "hipotese_diagnostica": "Febre reumática aguda com cardite",
            "conduta_proposta": (
                "Internação e cardiologia para tratar insuficiência cardíaca com "
                "diurético. Erradicar estreptococo com penicilina benzatina, controlar "
                "artrite com naproxeno e iniciar profilaxia secundária com penicilina "
                "benzatina a cada intervalo recomendado e por longo prazo para prevenir "
                "recorrência."
            ),
        },
    }

    for case_id, submission in submissions.items():
        response = client.post(
            f"/simulacoes/{case_id}/finalizar",
            json=submission,
            headers=headers,
        )
        assert response.status_code == 201, (case_id, response.text)
        result = response.json()
        assert result["nivel_conduta"] == "adequada", case_id
        assert result["pontuacao_total"] >= 90, case_id
        assert result["feedback"]["sintese_raciocinio"], case_id
        assert result["feedback"]["feedback_seguranca"], case_id
        assert result["feedback"]["reacao_paciente"], case_id
        assert result["feedback"]["desfecho_clinico"], case_id
        assert result["feedback"]["plano_pessoal_melhoria"], case_id


def test_final_feedback_batch_is_structured_and_clinically_corrected():
    token = _register_and_login("lote-final-feedback@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    batch_ids = {31, 32, 34, 35, 37}

    response = client.get("/casos-clinicos/", headers=headers)
    assert response.status_code == 200
    availability = {
        case["id"]: case["avaliacao_2_disponivel"] for case in response.json()
    }
    assert all(availability[case_id] for case_id in batch_ids)

    with SessionLocal() as db:
        rubrics = list(
            db.scalars(
                select(ClinicalRubric).where(ClinicalRubric.id_caso.in_(batch_ids))
            ).all()
        )
        assert len(rubrics) == len(batch_ids)
        assert all(rubric.status == "revisada" for rubric in rubrics)
        for rubric in rubrics:
            ClinicalRubricDefinition.model_validate(rubric.definicao)
            assert rubric.definicao["criterios_seguranca"]
            assert rubric.definicao["desfechos_conduta"]
            assert rubric.definicao["fontes_clinicas"]

    infant = client.get("/casos-clinicos/31", headers=headers)
    infant_exams = {exam["id"]: exam for exam in infant.json()["exames_disponiveis"]}
    assert infant_exams["inventario_osseo"]["correto"] is True
    assert (
        "não determina isoladamente" in infant_exams["fundo_olho"]["resultado"].lower()
    )

    autism = client.get("/casos-clinicos/32", headers=headers)
    autism_exams = {exam["id"]: exam for exam in autism.json()["exames_disponiveis"]}
    assert autism_exams["avaliacao_auditiva"]["correto"] is True
    assert "não equivale a diagnóstico" in autism_exams["mchat"]["resultado"].lower()

    tia = client.get("/casos-clinicos/34", headers=headers)
    tia_exams = {exam["id"]: exam for exam in tia.json()["exames_disponiveis"]}
    assert tia_exams["ecg_monitorizacao"]["correto"] is True
    assert (
        "não provam isoladamente"
        in tia_exams["eco_transesofagico"]["resultado"].lower()
    )

    abuse = client.get("/casos-clinicos/35", headers=headers)
    abuse_exams = {exam["id"]: exam for exam in abuse.json()["exames_disponiveis"]}
    assert "série esquelética" in abuse_exams["rx_corpo"]["nome"].lower()

    emergency = client.get("/casos-clinicos/37", headers=headers)
    emergency_exams = {
        exam["id"]: exam for exam in emergency.json()["exames_disponiveis"]
    }
    assert emergency_exams["rm_pres"]["correto"] is True
    assert "não exclui" in emergency_exams["tc_cranio"]["resultado"].lower()


def test_final_feedback_batch_generates_complete_safe_feedback():
    token = _register_and_login("lote-final-simulacoes@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    submissions = {
        31: {
            "exames_solicitados": [
                "abc_glicemia_coagulacao",
                "tc_cranio",
                "rm_cranio_coluna",
                "oftalmo_documentacao",
                "inventario_osseo",
            ],
            "hipotese_diagnostica": "Trauma craniano abusivo",
            "conduta_proposta": (
                "Proteger via aérea, tratar crises com levetiracetam e acionar "
                "neurocirurgia. Internação em ambiente seguro, afastar do agressor, "
                "fazer notificação compulsória e acionar conselho tutelar e serviço "
                "social. Documentar lesões, fotografar e envolver pediatria forense."
            ),
        },
        32: {
            "exames_solicitados": [
                "mchat",
                "avaliacao_multidisciplinar",
                "avaliacao_auditiva",
                "avaliacao_genetica",
            ],
            "hipotese_diagnostica": "Transtorno do espectro autista",
            "conduta_proposta": (
                "Encaminhar para avaliação multidisciplinar e neuropediatria. Iniciar "
                "intervenção precoce com fonoaudiologia e terapia ocupacional sem "
                "aguardar o laudo. Fazer avaliação auditiva, rastrear sono, epilepsia "
                "e alimentação, orientar família e construir plano individual com a escola."
            ),
        },
        34: {
            "exames_solicitados": [
                "tempo_neuro_glicemia",
                "tc_angio_tc",
                "rm_cranio",
                "ecg_monitorizacao",
                "eco_transesofagico",
            ],
            "hipotese_diagnostica": (
                "Ataque isquêmico transitório por embolia paradoxal"
            ),
            "conduta_proposta": (
                "Ativar protocolo de AVC e avaliação urgente em unidade de AVC. Após "
                "excluir hemorragia, iniciar aspirina e considerar dupla antiagregação "
                "curta com clopidogrel. Fazer monitorização cardíaca para fibrilação "
                "atrial, investigar outras causas e discutir fechamento do FOP e mixoma "
                "com heart team e cirurgia cardíaca."
            ),
        },
        35: {
            "exames_solicitados": [
                "abc_labs_abdominais",
                "tc_cranio",
                "rm_cranio_coluna",
                "rx_corpo",
                "oftalmo_documentacao",
            ],
            "hipotese_diagnostica": "Trauma craniano abusivo",
            "conduta_proposta": (
                "Proteger via aérea, tratar pressão intracraniana e acionar UTI "
                "pediátrica e neurocirurgia. Internação em ambiente seguro, afastar "
                "do agressor, realizar notificação compulsória, conselho tutelar e "
                "serviço social. Fotografar e documentar lesões com pediatria forense."
            ),
        },
        37: {
            "exames_solicitados": [
                "fundo_olho",
                "tc_cranio",
                "ecg_troponina_renal_urina",
                "rm_pres",
                "metanefrinas_pos_estabilizacao",
            ],
            "hipotese_diagnostica": (
                "Emergência hipertensiva com encefalopatia por feocromocitoma"
            ),
            "conduta_proposta": (
                "Internar em UTI com monitorização contínua e iniciar nicardipina "
                "titulável, reduzindo a pressão arterial média em 20 a 25% na primeira "
                "hora e depois gradualmente. Avaliar ECG, troponina, função renal e "
                "PRES. Após estabilização dosar metanefrinas e fazer bloqueio alfa com "
                "doxazosina, sem usar beta isolado."
            ),
        },
    }

    for case_id, submission in submissions.items():
        response = client.post(
            f"/simulacoes/{case_id}/finalizar",
            json=submission,
            headers=headers,
        )
        assert response.status_code == 201, (case_id, response.text)
        result = response.json()
        assert result["nivel_conduta"] == "adequada", case_id
        assert result["pontuacao_total"] >= 90, case_id
        assert result["feedback"]["sintese_raciocinio"], case_id
        assert result["feedback"]["feedback_seguranca"], case_id
        assert result["feedback"]["reacao_paciente"], case_id
        assert result["feedback"]["desfecho_clinico"], case_id
        assert result["feedback"]["plano_pessoal_melhoria"], case_id


def test_second_batch_is_released_after_editorial_approval():
    token = _register_and_login("lote-rubricas-rascunho@example.com")
    response = client.get(
        "/casos-clinicos/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    availability = {
        case["id"]: case["avaliacao_2_disponivel"] for case in response.json()
    }
    draft_case_ids = {33, 36, 38, 39, 40}
    assert all(availability[case_id] is True for case_id in draft_case_ids)

    with SessionLocal() as db:
        for case_id in draft_case_ids:
            rubric = db.scalar(
                select(ClinicalRubric).where(ClinicalRubric.id_caso == case_id)
            )
            assert rubric is not None
            assert rubric.status == "revisada"
            assert rubric.revisado_por == "Administração MedSync — liberação editorial"
            assert rubric.revisado_em is not None
            assert rubric.definicao["fontes_clinicas"]


def test_second_batch_exam_content_is_structured_and_corrected():
    token = _register_and_login("lote-exames-corrigidos@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    sepsis = client.get("/casos-clinicos/36", headers=headers)
    assert sepsis.status_code == 200
    sepsis_exams = {exam["id"]: exam for exam in sepsis.json()["exames_disponiveis"]}
    assert "coletadas" in sepsis_exams["hemoculturas"]["resultado"].lower()
    assert sepsis_exams["colonoscopia"]["correto"] is False

    luts = client.get("/casos-clinicos/39", headers=headers)
    assert luts.status_code == 200
    luts_exams = {exam["id"]: exam for exam in luts.json()["exames_disponiveis"]}
    assert "ng/ml" in luts_exams["psa"]["resultado"].lower()
    assert "funcao_renal" in luts_exams

    pyelonephritis = client.get("/casos-clinicos/40", headers=headers)
    assert pyelonephritis.status_code == 200
    pyelo_exams = {
        exam["id"]: exam for exam in pyelonephritis.json()["exames_disponiveis"]
    }
    assert pyelo_exams["tc_abdome"]["correto"] is False


def test_perforated_ulcer_case_prioritizes_imaging_over_endoscopy():
    token = _register_and_login("ulcera-perfurada@example.com")
    detail = client.get(
        "/casos-clinicos/6",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail.status_code == 200
    exams = {item["id"]: item for item in detail.json()["exames_disponiveis"]}
    assert exams["tc_abdome"]["correto"] is True
    assert exams["gaso_lactato"]["correto"] is True
    assert exams["eda"]["correto"] is False


def test_safety_omission_drives_unsafe_outcome():
    token = _register_and_login("conduta-insegura@example.com")
    response = client.post(
        "/simulacoes/12/finalizar",
        json={
            "exames_solicitados": ["cortisol_acth"],
            "hipotese_diagnostica": "Síndrome de Cushing iatrogênica",
            "conduta_proposta": "Suspender betametasona imediatamente e acompanhar pressão arterial.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    result = response.json()
    assert result["nivel_conduta"] == "insegura"
    assert "suspensão abrupta" in result["feedback"]["feedback_seguranca"].lower()
    assert "hipotensão" in result["feedback"]["reacao_paciente"].lower()
    assert result["objetivos_aprendizagem"]
    assert result["fontes_clinicas"][0]["organizacao"]


def test_clinical_simulation_v2_scores_and_persists_structured_feedback():
    token = _register_and_login("simulacao-v2@example.com")
    response = client.post(
        "/simulacoes/8/finalizar",
        json={
            "exames_solicitados": ["angiotc", "doppler_mmss", "gaso"],
            "justificativas_exames": {
                "angiotc": "Confirmar falhas de enchimento compatíveis com embolia pulmonar.",
            },
            "hipotese_diagnostica": "Tromboembolismo pulmonar agudo",
            "conduta_proposta": (
                "Estabilização pelo ABC, oxigenoterapia, anticoagulação com "
                "heparina, estratificação de risco e internação para monitorização."
            ),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    result = response.json()
    assert result["pontuacao_total"] == 100
    assert result["pontuacao"] == {
        "exames": 40,
        "hipotese": 30,
        "conduta": 30,
    }
    assert result["fonte_feedback"] == "agente_regras"
    assert result["diagnostico_referencia"].startswith("Tromboembolismo pulmonar agudo")
    assert result["exames"]["essenciais_ausentes"] == []
    assert result["exames"]["desnecessarios"] == []
    assert result["feedback"]["feedback_seguranca"].startswith(
        "Você contemplou os critérios de segurança rastreados neste caso."
    )
    assert "hipoxemia" in result["feedback"]["reacao_paciente"].lower()
    assert "monitor" in result["feedback"]["desfecho_clinico"].lower()
    assert result["feedback"]["sintese_raciocinio"]
    assert result["feedback"]["justificativas_exames"][0]["justificativa_estudante"]
    assert result["feedback"]["plano_pessoal_melhoria"]
    assert result["consequencias"]["estado_paciente"] == "estabilizado"
    assert result["consequencias"]["reavaliacao"]

    saved = client.get(
        f"/simulacoes/resultados/{result['progresso_id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert saved.status_code == 200
    assert saved.json() == result


def test_simulation_submission_is_idempotent():
    email = "simulacao-idempotente@example.com"
    token = _register_and_login(email)
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Idempotency-Key": "simulation-test-key-00000001",
    }
    payload = {
        "exames_solicitados": ["angiotc", "doppler_mmss", "gaso"],
        "hipotese_diagnostica": "Tromboembolismo pulmonar agudo",
        "conduta_proposta": (
            "Estabilização pelo ABC, oxigênio, anticoagulação com heparina, "
            "estratificação de risco e internação para monitorização."
        ),
    }

    first = client.post("/simulacoes/8/finalizar", json=payload, headers=headers)
    repeated = client.post("/simulacoes/8/finalizar", json=payload, headers=headers)

    assert first.status_code == 201
    assert repeated.status_code == 201
    assert repeated.json() == first.json()
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        requests = db.scalars(
            select(SimulationRequest).where(SimulationRequest.id_usuario == user.id)
        ).all()
        assert len(requests) == 1
        assert requests[0].status == "completed"
        assert requests[0].progresso_id == first.json()["progresso_id"]


def test_simulation_duplicate_is_blocked_while_original_is_processing():
    email = "simulacao-processando@example.com"
    token = _register_and_login(email)
    idempotency_key = "simulation-test-key-processing"
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        db.add(
            SimulationRequest(
                id_usuario=user.id,
                id_caso=8,
                idempotency_key=idempotency_key,
                status="processing",
            )
        )
        db.commit()

    response = client.post(
        "/simulacoes/8/finalizar",
        json={
            "exames_solicitados": ["angiotc"],
            "hipotese_diagnostica": "Tromboembolismo pulmonar",
            "conduta_proposta": "Oxigênio, anticoagulação e monitorização.",
        },
        headers={
            "Authorization": f"Bearer {token}",
            "X-Idempotency-Key": idempotency_key,
        },
    )

    assert response.status_code == 409
    assert "ainda está processando" in response.json()["detail"]


def test_simulation_v2_penalizes_low_value_exam_and_missing_actions():
    token = _register_and_login("simulacao-parcial@example.com")
    response = client.post(
        "/simulacoes/8/finalizar",
        json={
            "exames_solicitados": ["angiotc", "dimerod"],
            "hipotese_diagnostica": "Trombose venosa",
            "conduta_proposta": "Iniciar anticoagulação com heparina.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    result = response.json()
    assert result["pontuacao"]["exames"] < 40
    assert result["pontuacao"]["hipotese"] == 15
    assert result["pontuacao"]["conduta"] == 12
    assert result["exames"]["desnecessarios"] == ["D-dímero"]
    assert len(result["exames"]["essenciais_ausentes"]) == 2
    assert result["consequencias"]["tempo_desperdicado_minutos"] == 12
    assert result["consequencias"]["atraso_diagnostico_minutos"] == 36
    assert result["consequencias"]["tempo_total_impactado_minutos"] == 48

    follow_up = client.post(
        f"/simulacoes/resultados/{result['progresso_id']}/perguntar",
        json={"pergunta": "Por que este exame era desnecessário?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert follow_up.status_code == 200
    assert follow_up.json()["fonte_feedback"] == "agente_regras"
    assert "baixo valor" in follow_up.json()["resposta"].lower()

    notebook = client.get(
        "/caderno-erros/meu",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert notebook.status_code == 200
    assert len(notebook.json()) == 1
    assert notebook.json()[0]["tipo_origem"] == "caso_clinico"
    assert notebook.json()[0]["id_origem"] == "8"
    assert (
        notebook.json()[0]["detalhes"]["pontuacao_total"] == result["pontuacao_total"]
    )


def test_error_notebook_tracks_recurrence_status_mastery_and_user_isolation():
    first_token = _register_and_login("caderno@example.com")
    second_token = _register_and_login("caderno-isolado@example.com")
    headers = {"Authorization": f"Bearer {first_token}"}
    attempt = {
        "desafio_id": "pneumotorax-hipertensivo",
        "titulo": "Pneumotórax hipertensivo à esquerda",
        "especialidade": "Radiologia",
        "dificuldade": "Intermediário",
        "pergunta": "Qual é o diagnóstico mais provável nesta radiografia?",
        "resposta_usuario": "Pneumonia lobar",
        "resposta_correta": "Pneumotórax hipertensivo à esquerda",
        "explicacao": "A ausência de trama vascular indica ar no espaço pleural.",
        "imagem": "/images/desafios/pneumotorax.webp",
    }

    first = client.post("/caderno-erros/desafios", json=attempt, headers=headers)
    assert first.status_code == 200
    assert first.json()["status"] == "pendente"
    assert first.json()["quantidade_erros"] == 1

    repeated = client.post("/caderno-erros/desafios", json=attempt, headers=headers)
    assert repeated.status_code == 200
    assert repeated.json()["quantidade_erros"] == 2

    entry_id = repeated.json()["id"]
    reviewing = client.patch(
        f"/caderno-erros/{entry_id}/status",
        json={"status": "revisando"},
        headers=headers,
    )
    assert reviewing.status_code == 200
    assert reviewing.json()["status"] == "revisando"

    correct_attempt = {
        **attempt,
        "resposta_usuario": "Pneumotórax hipertensivo à esquerda",
    }
    mastered = client.post(
        "/caderno-erros/desafios", json=correct_attempt, headers=headers
    )
    assert mastered.status_code == 200
    assert mastered.json()["status"] == "dominado"
    assert mastered.json()["dominado_em"] is not None
    assert mastered.json()["quantidade_erros"] == 2

    isolated = client.get(
        "/caderno-erros/meu",
        headers={"Authorization": f"Bearer {second_token}"},
    )
    assert isolated.status_code == 200
    assert isolated.json() == []


def test_spaced_review_builds_daily_queue_and_updates_schedule():
    token = _register_and_login("revisao-espacada@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    attempt = {
        "desafio_id": "revisao-ecg",
        "titulo": "Ritmo irregular no ECG",
        "especialidade": "Cardiologia",
        "dificuldade": "Intermediário",
        "pergunta": "Qual é o diagnóstico mais provável?",
        "resposta_usuario": "Flutter atrial",
        "resposta_correta": "Fibrilação atrial",
        "explicacao": "A irregularidade dos intervalos RR favorece fibrilação atrial.",
        "imagem": "/images/desafios/ecg.webp",
    }

    created = client.post("/caderno-erros/desafios", json=attempt, headers=headers)
    assert created.status_code == 200
    entry_id = created.json()["id"]
    assert created.json()["revisoes_realizadas"] == 0

    due = client.get("/caderno-erros/revisoes-hoje", headers=headers)
    assert due.status_code == 200
    assert [entry["id"] for entry in due.json()] == [entry_id]

    plan = client.get("/caderno-erros/revisoes-plano", headers=headers)
    assert plan.status_code == 200
    assert [entry["id"] for entry in plan.json()] == [entry_id]
    assert {
        rating: forecast["intervalo_dias"]
        for rating, forecast in plan.json()[0]["previsoes"].items()
    } == {"errei": 1, "dificil": 1, "bom": 1, "facil": 3}
    assert plan.json()[0]["sequencia_acertos"] == 0

    first = client.post(
        f"/caderno-erros/{entry_id}/revisar",
        json={"avaliacao": "bom"},
        headers=headers,
    )
    assert first.status_code == 200
    assert first.json()["revisoes_realizadas"] == 1
    assert first.json()["sequencia_acertos"] == 1
    assert first.json()["intervalo_dias"] == 1
    assert first.json()["status"] == "revisando"

    assert client.get("/caderno-erros/revisoes-hoje", headers=headers).json() == []
    future_plan = client.get("/caderno-erros/revisoes-plano", headers=headers)
    assert [entry["id"] for entry in future_plan.json()] == [entry_id]
    assert future_plan.json()[0]["previsoes"]["bom"]["intervalo_dias"] == 7
    assert future_plan.json()[0]["previsoes"]["facil"]["intervalo_dias"] == 10

    second = client.post(
        f"/caderno-erros/{entry_id}/revisar",
        json={"avaliacao": "bom"},
        headers=headers,
    )
    assert second.json()["intervalo_dias"] == 7
    third = client.post(
        f"/caderno-erros/{entry_id}/revisar",
        json={"avaliacao": "bom"},
        headers=headers,
    )
    assert third.json()["intervalo_dias"] == 15
    assert third.json()["status"] == "dominado"

    forgotten = client.post(
        f"/caderno-erros/{entry_id}/revisar",
        json={"avaliacao": "errei"},
        headers=headers,
    )
    assert forgotten.json()["sequencia_acertos"] == 0
    assert forgotten.json()["intervalo_dias"] == 1
    assert forgotten.json()["status"] == "pendente"


def test_learning_paths_persist_progress_best_score_and_user_isolation():
    first_token = _register_and_login("trilhas@example.com")
    second_token = _register_and_login("trilhas-isolado@example.com")
    headers = {"Authorization": f"Bearer {first_token}"}

    catalog = client.get("/trilhas", headers=headers)
    assert catalog.status_code == 200
    assert len(catalog.json()) == 4
    image_path = next(
        path for path in catalog.json() if path["id"] == "diagnostico-por-imagem"
    )
    assert image_path["progresso"]["percentual"] == 0
    assert image_path["progresso"]["total"] == 9

    endpoint = "/trilhas/diagnostico-por-imagem/atividades/imagem-pneumonia/concluir"
    completed = client.post(endpoint, json={"pontuacao": 100}, headers=headers)
    assert completed.status_code == 200
    assert completed.json()["tentativas"] == 1
    assert completed.json()["melhor_pontuacao"] == 100

    repeated = client.post(endpoint, json={"pontuacao": 0}, headers=headers)
    assert repeated.status_code == 200
    assert repeated.json()["tentativas"] == 2
    assert repeated.json()["melhor_pontuacao"] == 100

    updated_catalog = client.get("/trilhas", headers=headers)
    updated_path = next(
        path
        for path in updated_catalog.json()
        if path["id"] == "diagnostico-por-imagem"
    )
    assert updated_path["progresso"]["concluidas"] == 1
    activity = updated_path["modulos"][0]["atividades"][0]
    assert activity["progresso"] == {
        "concluida": True,
        "tentativas": 2,
        "melhor_pontuacao": 100,
        "concluido_em": activity["progresso"]["concluido_em"],
    }

    isolated_catalog = client.get(
        "/trilhas",
        headers={"Authorization": f"Bearer {second_token}"},
    )
    isolated_path = next(
        path
        for path in isolated_catalog.json()
        if path["id"] == "diagnostico-por-imagem"
    )
    assert isolated_path["progresso"]["concluidas"] == 0

    invalid = client.post(
        "/trilhas/inexistente/atividades/atividade/concluir",
        json={"pontuacao": 50},
        headers=headers,
    )
    assert invalid.status_code == 404


def test_rule_based_feedback_is_driven_by_the_reviewed_rubric():
    from evaluation import (
        SimulationSubmission,
        build_rule_based_narrative,
        evaluate_objective,
    )

    case = {
        "id": 99,
        "titulo": "Caso genérico",
        "exames_disponiveis": [
            {"id": "teste_a", "nome": "Teste A", "resultado": "Positivo"},
        ],
    }
    rubric = {
        "diagnostico_referencia": "Diagnóstico alfa",
        "diagnostico_termos": ["diagnostico alfa"],
        "diagnostico_parcial": ["sindrome alfa"],
        "exames_essenciais": ["teste_a"],
        "exames_opcionais": [],
        "exames_desnecessarios": [],
        "justificativa_exames": {},
        "conduta_criterios": [
            {"nome": "Conduta alfa", "pontos": 30, "termos": ["tratamento alfa"]},
        ],
        "conduta_referencia": "Realizar tratamento alfa.",
        "feedback_hipotese_parcial": "A hipótese alfa ficou incompleta.",
        "feedback_hipotese_incorreta": "A hipótese não identificou o diagnóstico alfa.",
        "feedback_seguranca": "Verifique o sinal de alarme alfa.",
        "temas_estudo": ["Tema alfa"],
    }
    submission = SimulationSubmission(
        exames_solicitados=["teste_a"],
        hipotese_diagnostica="Síndrome beta",
        conduta_proposta="Observação clínica",
    )

    score, exams, context = evaluate_objective(case, submission, rubric)
    narrative = build_rule_based_narrative(submission, score, exams, context)

    assert rubric["feedback_hipotese_incorreta"] in narrative.pontos_melhoria
    assert rubric["feedback_seguranca"] in narrative.feedback_seguranca
    assert narrative.feedback_seguranca.startswith(
        "Mantenha como referência de segurança:"
    )
    assert "tromboembolismo" not in narrative.model_dump_json().lower()


def test_all_cases_are_available_after_final_rubric_review():
    token = _register_and_login("caso-legado@example.com")
    response = client.get(
        "/casos-clinicos/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    official_cases = [case for case in response.json() if case["id"] <= 80]
    assert len(official_cases) == 80
    assert all(case["avaliacao_2_disponivel"] for case in official_cases)


def _independent_question_explanation(question: ExamQuestion) -> QuestionExplanation:
    return QuestionExplanation(
        resumo="A resposta foi analisada a partir do enunciado e do gabarito validado.",
        porque_correta=(
            "A alternativa correta é compatível com os dados apresentados e com "
            "a prioridade clínica descrita na questão."
        ),
        analise_alternativas=[
            {
                "id": alternative["id"],
                "correta": alternative["id"] == question.alternativa_correta_id,
                "explicacao": (
                    "Esta alternativa corresponde ao gabarito validado."
                    if alternative["id"] == question.alternativa_correta_id
                    else "Esta alternativa não atende ao objetivo principal do enunciado."
                ),
            }
            for alternative in question.alternativas
        ],
        alerta_atualizacao=None,
        fonte="synapse",
    )


def test_question_catalog_and_answer_flow_are_isolated_from_review_features(
    monkeypatch,
):
    token = _register_and_login("questoes-fluxo@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    monkeypatch.setattr(
        "routers.questions.generate_question_explanation",
        _independent_question_explanation,
    )

    metadata = client.get("/questoes/meta", headers=headers)
    assert metadata.status_code == 200
    assert metadata.json()["total_questoes"] == 2811
    assert metadata.json()["limite_diario"] == 10

    listing = client.get("/questoes?quantidade=10", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()) == 10
    public_question = listing.json()[0]
    assert "alternativa_correta_id" not in public_question
    assert "explicacao" not in public_question

    hidden_explanation = client.post(
        f"/questoes/{public_question['id']}/explicacao",
        headers=headers,
    )
    assert hidden_explanation.status_code == 403

    with SessionLocal() as db:
        question = db.get(ExamQuestion, public_question["id"])
        correct_id = question.alternativa_correta_id
        user_id = db.scalar(
            select(User.id).where(User.email == "questoes-fluxo@example.com")
        )
        study_errors_before = db.scalar(
            select(func.count(StudyError.id)).where(StudyError.id_usuario == user_id)
        )

    answer = client.post(
        f"/questoes/{public_question['id']}/responder",
        headers=headers,
        json={"alternativa_id": correct_id, "tempo_segundos": 42},
    )
    assert answer.status_code == 200
    assert answer.json()["correta"] is True
    assert answer.json()["alternativa_correta_id"] == correct_id
    assert answer.json()["explicacao"]["fonte"] == "synapse"
    assert "ponto_chave" not in answer.json()["explicacao"]
    assert answer.json()["total_respondentes"] >= 1
    assert {item["id"] for item in answer.json()["distribuicao_alternativas"]} == {
        item["id"] for item in public_question["alternativas"]
    }
    assert round(
        sum(item["percentual"] for item in answer.json()["distribuicao_alternativas"]),
        1,
    ) in {99.9, 100.0, 100.1}
    assert answer.json()["respondidas_hoje"] == 1

    retry_explanation = client.post(
        f"/questoes/{public_question['id']}/explicacao",
        headers=headers,
    )
    assert retry_explanation.status_code == 200
    assert retry_explanation.json()["fonte"] == "synapse"
    assert "ponto_chave" not in retry_explanation.json()

    performance = client.get("/questoes/desempenho", headers=headers)
    assert performance.status_code == 200
    assert performance.json()["respondidas"] == 1
    assert performance.json()["acertos"] == 1

    report = client.post(
        f"/questoes/{public_question['id']}/reportar",
        headers=headers,
        json={"motivo": "desatualizada", "descricao": "Solicito revisão editorial."},
    )
    assert report.status_code == 200
    repeated_report = client.post(
        f"/questoes/{public_question['id']}/reportar",
        headers=headers,
        json={"motivo": "gabarito", "descricao": "Detalhes atualizados."},
    )
    assert repeated_report.status_code == 200
    assert repeated_report.json()["id"] == report.json()["id"]

    with SessionLocal() as db:
        assert (
            db.scalar(
                select(func.count(QuestionAttempt.id)).where(
                    QuestionAttempt.id_usuario == user_id
                )
            )
            == 1
        )
        assert (
            db.scalar(
                select(func.count(QuestionReport.id)).where(
                    QuestionReport.id_usuario == user_id
                )
            )
            == 1
        )
        assert (
            db.scalar(
                select(func.count(StudyError.id)).where(
                    StudyError.id_usuario == user_id
                )
            )
            == study_errors_before
        )


def test_question_distribution_counts_each_user_latest_answer_once():
    first_email = "questoes-distribuicao-1@example.com"
    second_email = "questoes-distribuicao-2@example.com"
    first_token = _register_and_login(first_email)
    _register_and_login(second_email)

    with SessionLocal() as db:
        first_user_id = db.scalar(select(User.id).where(User.email == first_email))
        second_user_id = db.scalar(select(User.id).where(User.email == second_email))
        question = ExamQuestion(
            ano=2026,
            instituicao="MedSync",
            cabecalho="Questão de validação interna",
            especialidade="Clínica Médica",
            assunto="Distribuição de respostas",
            enunciado="Qual alternativa representa o gabarito desta questão?",
            alternativas=[
                {"id": "A", "texto": "Primeira alternativa"},
                {"id": "B", "texto": "Segunda alternativa"},
                {"id": "C", "texto": "Terceira alternativa"},
            ],
            alternativa_correta_id="B",
            fingerprint=uuid.uuid4().hex,
            status="publicada",
        )
        db.add(question)
        db.flush()
        question.explicacao = _independent_question_explanation(question).model_dump(
            mode="json"
        )
        question.explicacao_status = "gerada"
        db.add_all(
            [
                QuestionAttempt(
                    id_usuario=first_user_id,
                    id_questao=question.id,
                    alternativa_selecionada_id="A",
                    correta=False,
                    tempo_segundos=30,
                ),
                QuestionAttempt(
                    id_usuario=second_user_id,
                    id_questao=question.id,
                    alternativa_selecionada_id="C",
                    correta=False,
                    tempo_segundos=40,
                ),
            ]
        )
        db.commit()
        question_id = question.id

    response = client.post(
        f"/questoes/{question_id}/responder",
        headers={"Authorization": f"Bearer {first_token}"},
        json={"alternativa_id": "B", "tempo_segundos": 25},
    )
    assert response.status_code == 200
    assert response.json()["total_respondentes"] == 2
    distribution = {
        item["id"]: item for item in response.json()["distribuicao_alternativas"]
    }
    assert distribution["A"] == {"id": "A", "escolhas": 0, "percentual": 0.0}
    assert distribution["B"] == {"id": "B", "escolhas": 1, "percentual": 50.0}
    assert distribution["C"] == {"id": "C", "escolhas": 1, "percentual": 50.0}
    with SessionLocal() as db:
        db.delete(db.get(ExamQuestion, question_id))
        db.commit()


def test_free_question_limit_counts_unique_questions_per_day():
    email = "questoes-limite@example.com"
    token = _register_and_login(email)
    headers = {"Authorization": f"Bearer {token}"}

    with SessionLocal() as db:
        user_id = db.scalar(select(User.id).where(User.email == email))
        questions = list(
            db.scalars(
                select(ExamQuestion)
                .where(ExamQuestion.status == "publicada")
                .order_by(ExamQuestion.id)
                .limit(11)
            ).all()
        )
        db.add_all(
            [
                QuestionAttempt(
                    id_usuario=user_id,
                    id_questao=question.id,
                    alternativa_selecionada_id=question.alternativa_correta_id,
                    correta=True,
                    tempo_segundos=30,
                )
                for question in questions[:10]
            ]
        )
        db.commit()
        eleventh_id = questions[10].id
        eleventh_answer = questions[10].alternativa_correta_id

    metadata = client.get("/questoes/meta", headers=headers)
    assert metadata.json()["respondidas_hoje"] == 10
    assert metadata.json()["restantes_hoje"] == 0
    assert client.get("/questoes", headers=headers).json() == []

    blocked = client.post(
        f"/questoes/{eleventh_id}/responder",
        headers=headers,
        json={"alternativa_id": eleventh_answer},
    )
    assert blocked.status_code == 403
    assert "10 questões gratuitas" in blocked.json()["detail"]


def test_admin_can_search_moderate_and_generate_question_explanations(monkeypatch):
    email = "questoes-admin@example.com"
    previous_admin_emails = os.environ.get("ADMIN_EMAILS")
    os.environ["ADMIN_EMAILS"] = email
    try:
        token = _register_and_login(email)
        headers = {"Authorization": f"Bearer {token}"}
        question_id = client.get("/questoes?quantidade=1", headers=headers).json()[0][
            "id"
        ]
        with SessionLocal() as db:
            correct_id = db.get(ExamQuestion, question_id).alternativa_correta_id
        monkeypatch.setattr(
            "routers.questions.generate_question_explanation",
            _independent_question_explanation,
        )

        response = client.get(
            f"/admin/questoes?busca={question_id}&limite=20", headers=headers
        )
        assert response.status_code == 200
        assert response.json()["resumo"]["total"] == 2811
        assert [item["id"] for item in response.json()["questoes"]] == [question_id]

        hidden = client.patch(
            f"/admin/questoes/{question_id}",
            headers=headers,
            json={"status": "oculta", "assunto": "Cirurgia geral"},
        )
        assert hidden.status_code == 200
        assert (
            client.post(
                f"/questoes/{question_id}/responder",
                headers=headers,
                json={"alternativa_id": correct_id},
            ).status_code
            == 404
        )

        generated = client.post(
            f"/admin/questoes/{question_id}/gerar-explicacao", headers=headers
        )
        assert generated.status_code == 200
        with SessionLocal() as db:
            question = db.get(ExamQuestion, question_id)
            assert question.status == "oculta"
            assert question.assunto == "Cirurgia geral"
            assert question.explicacao_status == "gerada"
            question.status = "publicada"
            db.commit()
    finally:
        if previous_admin_emails is None:
            os.environ.pop("ADMIN_EMAILS", None)
        else:
            os.environ["ADMIN_EMAILS"] = previous_admin_emails
