import importlib
import os
import sys
import uuid
from pathlib import Path

from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from alembic import command

TEST_DB = Path("/tmp") / f"medsync-{uuid.uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["JWT_SECRET_KEY"] = "test-secret-with-at-least-32-characters"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
command.upgrade(Config("alembic.ini"), "head")
from database import SessionLocal
from models import ClinicalCase, ClinicalExam, ClinicalRubric
from services.clinical_content import seed_clinical_content

with SessionLocal() as db:
    seed_clinical_content(db)
main = importlib.import_module("main")
client = TestClient(main.app)


def _register_and_login(email: str = "aluno@example.com") -> str:
    response = client.post(
        "/usuarios/registrar",
        json={
            "nome": "Aluno MedSync",
            "email": email,
            "periodo_curso": 6,
            "faculdade": "Universidade Federal do Maranhão",
            "password": "senha-segura",
        },
    )
    assert response.status_code == 201

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
        assert db.scalar(select(func.count()).select_from(ClinicalCase)) == 40
        assert db.scalar(select(func.count()).select_from(ClinicalExam)) > 40
        rubric = db.scalar(select(ClinicalRubric).where(ClinicalRubric.id_caso == 8))
        assert rubric is not None
        assert rubric.versao == 2
        assert rubric.status == "revisada"
        assert seed_clinical_content(db) is False


def test_existing_pilot_rubric_is_safely_upgraded():
    with SessionLocal() as db:
        rubric = db.scalar(select(ClinicalRubric).where(ClinicalRubric.id_caso == 8))
        rubric.versao = 1
        rubric.definicao = {"formato": "legado"}
        db.commit()

        assert seed_clinical_content(db) is False
        db.refresh(rubric)

        assert rubric.versao == 2
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
        },
    )

    assert response.status_code == 201
    assert response.json()["nome"] == "Maria da Silva"
    assert response.json()["periodo_curso"] == 4
    assert response.json()["faculdade"] == "Universidade Federal do Piauí"


def test_registration_requires_valid_academic_profile():
    payload = {
        "nome": "Aluno sem perfil",
        "email": "perfil-invalido@example.com",
        "password": "senha-segura",
    }
    assert client.post("/usuarios/registrar", json=payload).status_code == 422

    payload.update({"periodo_curso": 13, "faculdade": "UFMA"})
    assert client.post("/usuarios/registrar", json=payload).status_code == 422


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
    webhook_headers = {
        "asaas-access-token": os.environ["ASAAS_WEBHOOK_TOKEN"]
    }
    checkout_paid = {
        "id": "evt_checkout_recurring_paid_123",
        "event": "CHECKOUT_PAID",
        "checkout": {"id": "checkout_sandbox_123", "status": "PAID"},
    }
    assert client.post(
        "/pagamentos/webhooks/asaas",
        json=checkout_paid,
        headers=webhook_headers,
    ).status_code == 200
    checkout_expiry = client.get(
        f"/pagamentos/pedidos/{order_id}", headers=headers
    ).json()["premium_valido_ate"]
    replay = client.post(
        "/pagamentos/webhooks/asaas",
        json=checkout_paid,
        headers=webhook_headers,
    )
    assert replay.json()["duplicate"] is True
    assert client.get(
        f"/pagamentos/pedidos/{order_id}", headers=headers
    ).json()["premium_valido_ate"] == checkout_expiry

    first = client.post(
        "/pagamentos/webhooks/asaas", json=event, headers=webhook_headers
    )
    assert first.status_code == 200
    assert first.json()["duplicate"] is False

    status_response = client.get(
        f"/pagamentos/pedidos/{order_id}", headers=headers
    )
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
    webhook_headers = {
        "asaas-access-token": os.environ["ASAAS_WEBHOOK_TOKEN"]
    }
    paid = {
        "id": "evt_checkout_paid_123",
        "event": "CHECKOUT_PAID",
        "checkout": {"id": "checkout_detached_123", "status": "PAID"},
    }
    assert client.post(
        "/pagamentos/webhooks/asaas", json=paid, headers=webhook_headers
    ).status_code == 200
    first_status = client.get(
        f"/pagamentos/pedidos/{order_id}", headers=headers
    ).json()
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
    assert client.post(
        "/pagamentos/webhooks/asaas", json=payment, headers=webhook_headers
    ).status_code == 200
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
    assert len(case_catalog.json()) == 40
    assert {item["nivel_dificuldade"] for item in case_catalog.json()} >= {
        "Intermediário",
        "Crítico",
    }

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
    legacy = next(case for case in cases if case["id"] == 1)
    assert pilot["titulo"].startswith("Caso #008 – ")
    assert "tromboembolismo" not in pilot["titulo"].lower()
    assert "pericardite" not in legacy["titulo"].lower()
    assert pilot["avaliacao_2_disponivel"] is True
    assert legacy["avaliacao_2_disponivel"] is False


def test_clinical_simulation_v2_scores_and_persists_structured_feedback():
    token = _register_and_login("simulacao-v2@example.com")
    response = client.post(
        "/simulacoes/8/finalizar",
        json={
            "exames_solicitados": ["angiotc", "doppler_mmss", "gaso"],
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
    assert result["diagnostico_referencia"].startswith(
        "Tromboembolismo pulmonar agudo"
    )
    assert result["exames"]["essenciais_ausentes"] == []
    assert result["exames"]["desnecessarios"] == []
    assert result["feedback"]["feedback_seguranca"]

    saved = client.get(
        f"/simulacoes/resultados/{result['progresso_id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert saved.status_code == 200
    assert saved.json() == result


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
    assert narrative.feedback_seguranca == rubric["feedback_seguranca"]
    assert "tromboembolismo" not in narrative.model_dump_json().lower()


def test_legacy_case_cannot_use_v2_until_its_rubric_is_reviewed():
    token = _register_and_login("caso-legado@example.com")
    response = client.post(
        "/simulacoes/1/finalizar",
        json={
            "exames_solicitados": ["ecg"],
            "hipotese_diagnostica": "Pericardite aguda",
            "conduta_proposta": "Monitorização e tratamento conforme avaliação.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 409
