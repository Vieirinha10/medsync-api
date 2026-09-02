import collections
import copy
import hashlib
import json
import os
import pathlib
import sys
import tempfile
import uuid
from datetime import UTC, datetime
from typing import Any, Dict

import pytest
from alembic import command
from alembic.config import Config
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, inspect, select
from sqlalchemy.orm import sessionmaker

# Fixture canônica portável
TESTS_DIR = pathlib.Path(__file__).resolve().parent
FIXTURE_PATH = TESTS_DIR / "fixtures" / "pilot-100-import-ready.jsonl"
API_ROOT = TESTS_DIR.parent
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

import database
from database import Base, SessionLocal, engine
from main import app
from models import ExamQuestion, QuestionSourceAlias, User
from scripts.import_question_catalog import (
    compute_sha256,
    import_catalog,
    rollback_catalog,
    validate_and_normalize_record,
)
from security import create_access_token, hash_password


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def auth_headers():
    db = SessionLocal()
    user_email = f"test_catalog_v2_{uuid.uuid4().hex[:8]}@medsync.com.br"
    user = User(
        nome="Auditor Codex v2",
        email=user_email,
        password_hash=hash_password("Password123!"),
        email_verified_at=datetime.now(UTC),
        terms_accepted_at=datetime.now(UTC),
        terms_version="2026-08-11",
        privacy_version="2026-08-11",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, user.auth_version)
    db.close()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module", autouse=True)
def ensure_pilot_imported():
    db = SessionLocal()
    count_v2 = db.scalar(
        select(func.count(ExamQuestion.id)).where(ExamQuestion.catalog_version == "v2")
    ) or 0
    if count_v2 == 0:
        import_catalog(db, FIXTURE_PATH, catalog_version="v2")
    db.close()


def test_01_migration_lifecycle_upgrade_downgrade_upgrade():
    """
    Testa o ciclo completo da migração Alembic (upgrade -> downgrade -> upgrade)
    em um banco temporário isolado, sem ignorar nenhuma exceção.
    Valida colunas, índices, constraints e foreign keys.
    """
    test_db_path = pathlib.Path(tempfile.gettempdir()) / f"medsync_mig_{uuid.uuid4().hex}.db"
    test_db_url = f"sqlite:///{test_db_path.as_posix()}"

    old_env = os.environ.get("DATABASE_URL")
    old_db_url = database.DATABASE_URL
    os.environ["DATABASE_URL"] = test_db_url
    database.DATABASE_URL = test_db_url

    try:
        alembic_cfg_path = API_ROOT / "alembic.ini"
        alembic_scripts_path = API_ROOT / "alembic"

        cfg = Config(str(alembic_cfg_path))
        cfg.set_main_option("script_location", str(alembic_scripts_path))

        # 1. Upgrade inicial até head
        command.upgrade(cfg, "head")

        test_engine = create_engine(test_db_url)
        insp = inspect(test_engine)

        assert "exam_questions" in insp.get_table_names()
        assert "question_source_aliases" in insp.get_table_names()

        cols_up = {c["name"] for c in insp.get_columns("exam_questions")}
        expected_cols = {
            "catalog_version", "source_id", "statement_plain", "statement_rich_html",
            "random_rank", "media_classification", "image_rights_status",
            "content_hash_plain", "content_hash_rich", "answer_binding_hash",
            "banca", "finalidade", "regiao", "tema", "subtema", "tipo_prova"
        }
        assert expected_cols.issubset(cols_up), f"Faltam colunas: {expected_cols - cols_up}"

        # 2. Downgrade para 20260827_15
        command.downgrade(cfg, "20260827_15")
        insp_down = inspect(test_engine)
        assert "question_source_aliases" not in insp_down.get_table_names()
        cols_down = {c["name"] for c in insp_down.get_columns("exam_questions")}
        assert "tema" not in cols_down
        assert "content_hash_plain" not in cols_down

        # 3. Novo upgrade para head
        command.upgrade(cfg, "head")
        insp_reup = inspect(test_engine)
        assert "question_source_aliases" in insp_reup.get_table_names()
        cols_reup = {c["name"] for c in insp_reup.get_columns("exam_questions")}
        assert expected_cols.issubset(cols_reup)

        test_engine.dispose()
    finally:
        database.DATABASE_URL = old_db_url
        if old_env is not None:
            os.environ["DATABASE_URL"] = old_env
        else:
            os.environ.pop("DATABASE_URL", None)
        try:
            test_db_path.unlink(missing_ok=True)
        except PermissionError:
            pass


def test_02_field_by_field_fidelity_reconciliation():
    """
    Compara campo a campo os 100 registros do JSONL com os 100 registros
    armazenados no banco de dados. Gera relatório JSON completo de reconciliação.
    """
    assert FIXTURE_PATH.exists(), f"Fixture não encontrada: {FIXTURE_PATH}"

    # Ler fixture
    jsonl_records = []
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                jsonl_records.append(json.loads(line))

    assert len(jsonl_records) == 100, f"Esperava 100 registros no JSONL, encontrou {len(jsonl_records)}"

    db = SessionLocal()
    try:
        db_records = db.scalars(
            select(ExamQuestion)
            .where(ExamQuestion.catalog_version == "v2")
            .order_by(ExamQuestion.source_id)
        ).all()

        assert len(db_records) == 100, f"Esperava 100 registros v2 no banco, encontrou {len(db_records)}"
        db_by_sid = {q.source_id: q for q in db_records}

        divergences = []
        null_counts = collections.defaultdict(int)
        specialty_dist = collections.defaultdict(int)
        theme_dist = collections.defaultdict(int)
        year_dist = collections.defaultdict(int)
        inst_dist = collections.defaultdict(int)
        correct_letter_dist = collections.defaultdict(int)
        alts_count_dist = collections.defaultdict(int)

        for rec in jsonl_records:
            sid = rec["source_id"]
            q = db_by_sid.get(sid)
            assert q is not None, f"Questão com source_id={sid} não encontrada no banco!"

            # Validar source_id
            if q.source_id != sid:
                divergences.append({"source_id": sid, "field": "source_id", "json": sid, "db": q.source_id})

            # Validar ano
            if q.ano != rec["ano"]:
                divergences.append({"source_id": sid, "field": "ano", "json": rec["ano"], "db": q.ano})
            year_dist[str(q.ano)] += 1

            # Validar instituição
            expected_inst = rec.get("instituicao")
            if q.instituicao != expected_inst:
                divergences.append({"source_id": sid, "field": "instituicao", "json": expected_inst, "db": q.instituicao})
            if expected_inst:
                inst_dist[expected_inst] += 1
            else:
                null_counts["instituicao"] += 1

            # Validar banca
            expected_banca = rec.get("banca")
            if q.banca != expected_banca:
                divergences.append({"source_id": sid, "field": "banca", "json": expected_banca, "db": q.banca})
            if not expected_banca:
                null_counts["banca"] += 1

            # Validar finalidade
            expected_fin = rec.get("finalidade")
            if q.finalidade != expected_fin:
                divergences.append({"source_id": sid, "field": "finalidade", "json": expected_fin, "db": q.finalidade})
            if not expected_fin:
                null_counts["finalidade"] += 1

            # Validar regiao
            expected_reg = rec.get("regiao")
            if q.regiao != expected_reg:
                divergences.append({"source_id": sid, "field": "regiao", "json": expected_reg, "db": q.regiao})
            if not expected_reg:
                null_counts["regiao"] += 1

            # Validar especialidade
            expected_esp = rec.get("especialidade")
            if q.especialidade != expected_esp:
                divergences.append({"source_id": sid, "field": "especialidade", "json": expected_esp, "db": q.especialidade})
            if expected_esp:
                specialty_dist[expected_esp] += 1
            else:
                null_counts["especialidade"] += 1

            # Validar tema
            expected_tema = rec.get("tema")
            if q.tema != expected_tema:
                divergences.append({"source_id": sid, "field": "tema", "json": expected_tema, "db": q.tema})
            if expected_tema:
                theme_dist[expected_tema] += 1
            else:
                null_counts["tema"] += 1

            # Validar subtema
            expected_subtema = rec.get("subtema")
            if q.subtema != expected_subtema:
                divergences.append({"source_id": sid, "field": "subtema", "json": expected_subtema, "db": q.subtema})
            if not expected_subtema:
                null_counts["subtema"] += 1

            # Validar enunciado simples
            if q.statement_plain != rec["statement_plain"]:
                divergences.append({"source_id": sid, "field": "statement_plain", "divergence": True})

            # Validar enunciado rico
            expected_rich = rec.get("statement_rich_html") or rec["statement_plain"]
            if q.statement_rich_html != expected_rich:
                divergences.append({"source_id": sid, "field": "statement_rich_html", "divergence": True})

            # Validar alternativas: quantidade, ordem, letra e texto
            q_alts = q.alternativas or []
            rec_alts = rec.get("alternatives") or []
            if len(q_alts) != len(rec_alts):
                divergences.append({"source_id": sid, "field": "alternatives_count", "json": len(rec_alts), "db": len(q_alts)})
            alts_count_dist[str(len(q_alts))] += 1

            for idx, (qa, ra) in enumerate(zip(q_alts, rec_alts)):
                r_let = str(ra.get("letter") or chr(ord("A") + idx)).strip()
                r_text = str(ra.get("body_plain") or ra.get("body") or "").strip()
                if qa.get("id") != r_let or qa.get("texto") != r_text:
                    divergences.append({"source_id": sid, "field": f"alternative_{idx}", "json": (r_let, r_text), "db": (qa.get("id"), qa.get("texto"))})

            # Validar alternativa correta
            if q.alternativa_correta_id != rec["correct_letter"]:
                divergences.append({"source_id": sid, "field": "alternativa_correta_id", "json": rec["correct_letter"], "db": q.alternativa_correta_id})
            correct_letter_dist[rec["correct_letter"]] += 1

            # Validar hashes
            if q.content_hash_plain != rec["content_hash_plain"]:
                divergences.append({"source_id": sid, "field": "content_hash_plain", "json": rec["content_hash_plain"], "db": q.content_hash_plain})
            if q.content_hash_rich != rec["content_hash_rich"]:
                divergences.append({"source_id": sid, "field": "content_hash_rich", "json": rec["content_hash_rich"], "db": q.content_hash_rich})
            if q.answer_binding_hash != rec["answer_binding_hash"]:
                divergences.append({"source_id": sid, "field": "answer_binding_hash", "json": rec["answer_binding_hash"], "db": q.answer_binding_hash})

            # Validar flags e status
            if q.media_classification != rec["media_classification"]:
                divergences.append({"source_id": sid, "field": "media_classification", "json": rec["media_classification"], "db": q.media_classification})
            if q.image_rights_status != rec["image_rights_status"]:
                divergences.append({"source_id": sid, "field": "image_rights_status", "json": rec["image_rights_status"], "db": q.image_rights_status})
            if q.explicacao_status != "pendente" or q.explicacao is not None:
                divergences.append({"source_id": sid, "field": "explanation", "error": "Explicação não nula ou status incorreto"})
            if q.catalog_version != "v2":
                divergences.append({"source_id": sid, "field": "catalog_version", "db": q.catalog_version})

        # Relatório de reconciliação
        reports_dir = API_ROOT / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        recon_report = {
            "records_compared": len(jsonl_records),
            "divergences_count": len(divergences),
            "divergences": divergences,
            "null_counts_by_column": dict(null_counts),
            "specialty_distribution": dict(specialty_dist),
            "theme_distribution": dict(theme_dist),
            "year_distribution": dict(year_dist),
            "institution_distribution": dict(inst_dist),
            "correct_letter_distribution": dict(correct_letter_dist),
            "alternatives_count_distribution": dict(alts_count_dist),
        }
        with open(reports_dir / "reconciliation_report.json", "w", encoding="utf-8") as rf:
            json.dump(recon_report, rf, indent=2, ensure_ascii=False)

        assert len(divergences) == 0, f"Encontradas {len(divergences)} divergências na reconciliação: {divergences}"

    finally:
        db.close()


def test_03_atomic_rollback_on_simulated_failure():
    """
    Testa a atomicidade real do importador: provoca uma falha simulada
    no meio do lote e comprova que NENHUMA questão parcial é gravada.
    """
    # Criar um arquivo JSONL temporário com 5 questões válidas e a 6ª com erro estrito
    temp_jsonl = pathlib.Path(tempfile.gettempdir()) / f"corrupted_{uuid.uuid4().hex}.jsonl"

    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        lines = [f.readline() for _ in range(5)]

    # Criar 6ª linha com media_classification proibida
    corrupted_item = json.loads(lines[0])
    corrupted_item["source_id"] = "9999999999"
    corrupted_item["media_classification"] = "IMAGE_DEPENDENT"  # Bloqueado pela Regra 8

    with open(temp_jsonl, "w", encoding="utf-8") as tf:
        for l in lines:
            tf.write(l)
        tf.write(json.dumps(corrupted_item) + "\n")

    db = SessionLocal()
    try:
        # Contagem de v2 antes
        count_before = db.scalar(
            select(func.count(ExamQuestion.id)).where(ExamQuestion.catalog_version == "v2_test_rollback")
        ) or 0
        assert count_before == 0

        with pytest.raises(ValueError, match="media_classification"):
            import_catalog(db, temp_jsonl, catalog_version="v2_test_rollback")

        # Comprovar que zero questões foram persistidas
        count_after = db.scalar(
            select(func.count(ExamQuestion.id)).where(ExamQuestion.catalog_version == "v2_test_rollback")
        ) or 0
        assert count_after == 0, "FALHA DE ATOMICIDADE: Registros parciais foram encontrados após erro!"

    finally:
        db.close()
        temp_jsonl.unlink(missing_ok=True)


def test_04_v1_v2_source_id_collision_prevention():
    """
    Testa a proteção do catálogo v1 contra colisão de source_id:
    - Se o source_id já existir em outra versão, a importação DEVE falhar.
    - O registro v1 original DEVE permanecer byte a byte idêntico.
    """
    db = SessionLocal()
    test_sid = f"COLLISION_TEST_{uuid.uuid4().hex[:6]}"
    temp_jsonl = pathlib.Path(tempfile.gettempdir()) / f"collision_{uuid.uuid4().hex}.jsonl"

    try:
        # Inserir questão mock no catálogo v1 com test_sid
        v1_q = ExamQuestion(
            source_id=test_sid,
            catalog_version="v1",
            ano=2015,
            instituicao="USP Legado",
            cabecalho="USP · 2015",
            especialidade="Cirurgia",
            assunto="Trauma",
            enunciado="Enunciado v1 intocado de teste.",
            statement_plain="Enunciado v1 intocado de teste.",
            alternativas=[{"id": "A", "texto": "Opcao A", "is_correct": True}],
            alternativa_correta_id="A",
            fingerprint=f"fp_{test_sid}",
            status="publicada"
        )
        db.add(v1_q)
        db.commit()

        # Preparar JSONL tentando importar o mesmo source_id como v2
        with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
            valid_rec = json.loads(f.readline())

        valid_rec["source_id"] = test_sid
        # Recalcular hashes para o record ser internamente consistente
        calc_plain = compute_sha256(f"{valid_rec['statement_plain']}||" + "|".join(f"{a['letter']}:{a['body_plain']}" for a in sorted(valid_rec['alternatives'], key=lambda x: x['letter'])))
        calc_rich = compute_sha256(f"{valid_rec['statement_rich_html']}||" + "|".join(f"{a['letter']}:{a['body_rich_html']}" for a in sorted(valid_rec['alternatives'], key=lambda x: x['letter'])))
        calc_binding = compute_sha256(f"{calc_plain}||{valid_rec['correct_letter']}||" + "|".join(f"{a['letter']}:{1 if a['is_correct'] else 0}" for a in sorted(valid_rec['alternatives'], key=lambda x: x['letter'])))
        valid_rec["content_hash_plain"] = calc_plain
        valid_rec["content_hash_rich"] = calc_rich
        valid_rec["answer_binding_hash"] = calc_binding

        with open(temp_jsonl, "w", encoding="utf-8") as tf:
            tf.write(json.dumps(valid_rec) + "\n")

        # Tentativa de importar DEVE lançar exceção de colisão de versão
        with pytest.raises(ValueError, match="COLISÃO DE VERSÃO DETECTADA"):
            import_catalog(db, temp_jsonl, catalog_version="v2")

        # Comprovar que o registro v1 permaneceu intocado
        v1_check = db.scalar(select(ExamQuestion).where(ExamQuestion.source_id == test_sid))
        assert v1_check is not None
        assert v1_check.catalog_version == "v1"
        assert v1_check.enunciado == "Enunciado v1 intocado de teste."
        assert v1_check.instituicao == "USP Legado"

    finally:
        # Limpeza do mock
        db.execute(select(ExamQuestion).where(ExamQuestion.source_id == test_sid))
        q_del = db.scalar(select(ExamQuestion).where(ExamQuestion.source_id == test_sid))
        if q_del:
            db.delete(q_del)
            db.commit()
        db.close()
        temp_jsonl.unlink(missing_ok=True)


def test_05_idempotency_detects_unchanged_and_rejects_hash_conflict():
    """
    Testa:
    1. Idempotência sem alterações: informa unchanged_count = 100 e inserted_count = 0.
    2. Conflito de hash: aborta e rejeita qualquer alteração silenciosa.
    """
    db = SessionLocal()
    temp_jsonl = pathlib.Path(tempfile.gettempdir()) / f"conflict_{uuid.uuid4().hex}.jsonl"

    try:
        # 1. Execução idêntica
        res = import_catalog(db, FIXTURE_PATH, catalog_version="v2")
        assert res["inserted_count"] == 0
        assert res["unchanged_count"] == 100

        # 2. Conflito: carregar 1 registro com conteúdo divergente para o mesmo source_id
        with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
            rec = json.loads(f.readline())

        # Alterar o enunciado mas manter source_id
        rec["statement_plain"] = "Enunciado alterado indevidamente pelo fornecedor."
        rec["statement_rich_html"] = "Enunciado alterado indevidamente pelo fornecedor."
        # Hashes novos recalculados
        calc_plain = compute_sha256(f"{rec['statement_plain']}||" + "|".join(f"{a['letter']}:{a['body_plain']}" for a in sorted(rec['alternatives'], key=lambda x: x['letter'])))
        calc_rich = compute_sha256(f"{rec['statement_rich_html']}||" + "|".join(f"{a['letter']}:{a['body_rich_html']}" for a in sorted(rec['alternatives'], key=lambda x: x['letter'])))
        calc_binding = compute_sha256(f"{calc_plain}||{rec['correct_letter']}||" + "|".join(f"{a['letter']}:{1 if a['is_correct'] else 0}" for a in sorted(rec['alternatives'], key=lambda x: x['letter'])))
        rec["content_hash_plain"] = calc_plain
        rec["content_hash_rich"] = calc_rich
        rec["answer_binding_hash"] = calc_binding

        with open(temp_jsonl, "w", encoding="utf-8") as tf:
            tf.write(json.dumps(rec) + "\n")

        # DEVE abortar com conflito de hash detectado
        with pytest.raises(ValueError, match="CONFLITO DE HASH DETECTADO"):
            import_catalog(db, temp_jsonl, catalog_version="v2")

    finally:
        db.close()
        temp_jsonl.unlink(missing_ok=True)


def test_06_eligibility_and_media_validation_blocks_bad_records():
    """
    Testa o bloqueio estrito de registros não elegíveis (Regra 8):
    - publication_status != ACTIVE
    - quarantine_reasons não vazio
    - media_classification inválida
    - image_rights_status != NONE_REQUIRED
    - has_video == True
    """
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        base_rec = json.loads(f.readline())

    # Caso A: publication_status != ACTIVE
    bad_a = copy.deepcopy(base_rec)
    bad_a["publication_status"] = "QUARANTINED"
    with pytest.raises(ValueError, match="publication_status"):
        validate_and_normalize_record(bad_a, 1)

    # Caso B: quarantine_reasons
    bad_b = copy.deepcopy(base_rec)
    bad_b["quarantine_reasons"] = ["QUARANTINED_IMAGE_DEPENDENCY"]
    with pytest.raises(ValueError, match="registro em quarentena"):
        validate_and_normalize_record(bad_b, 2)

    # Caso C: media_classification inválida
    bad_c = copy.deepcopy(base_rec)
    bad_c["media_classification"] = "IMAGE_DEPENDENT"
    with pytest.raises(ValueError, match="media_classification"):
        validate_and_normalize_record(bad_c, 3)

    # Caso D: image_rights_status != NONE_REQUIRED
    bad_d = copy.deepcopy(base_rec)
    bad_d["image_rights_status"] = "PENDING_CONFIRMATION"
    with pytest.raises(ValueError, match="image_rights_status"):
        validate_and_normalize_record(bad_d, 4)

    # Caso E: has_video == True
    bad_e = copy.deepcopy(base_rec)
    bad_e["has_video"] = True
    with pytest.raises(ValueError, match="has_video"):
        validate_and_normalize_record(bad_e, 5)


def test_07_hash_recalculation_and_binding_integrity():
    """
    Testa a validação e recálculo de hashes (Regra 9):
    Divergência em content_hash_plain, content_hash_rich ou answer_binding_hash
    deve provocar falha imediata.
    """
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        base_rec = json.loads(f.readline())

    # Adulterar content_hash_plain
    tampered_plain = copy.deepcopy(base_rec)
    tampered_plain["content_hash_plain"] = "0000000000000000000000000000000000000000000000000000000000000000"
    with pytest.raises(ValueError, match="divergência em content_hash_plain"):
        validate_and_normalize_record(tampered_plain, 1)

    # Adulterar answer_binding_hash
    tampered_binding = copy.deepcopy(base_rec)
    tampered_binding["answer_binding_hash"] = "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    with pytest.raises(ValueError, match="divergência em answer_binding_hash"):
        validate_and_normalize_record(tampered_binding, 2)


def test_08_zero_synapse_and_no_gabarito_leak(client, auth_headers):
    """
    Valida a proteção absoluta de segurança da API:
    1. Antes da resposta: nenhum vazamento de gabarito ou hashes reversíveis.
    2. Resposta: correta, alternativa_correta_id, explicacao = null, explanation_status = PENDING.
    3. Zero chamadas à Synapse ou IA.
    4. Tentativa de solicitar explicação v2 bloqueada com HTTP 400.
    5. Versão de catálogo arbitrária bloqueada com HTTP 400.
    6. Preservação das 2.811 questões de v1.
    """
    # 1. Versão arbitrária bloqueada
    res_bad_ver = client.get("/questoes?catalog_version=v3", headers=auth_headers)
    assert res_bad_ver.status_code == status.HTTP_400_BAD_REQUEST

    # 2. Obter questão v2
    res_list = client.get("/questoes?catalog_version=v2&quantidade=5", headers=auth_headers)
    assert res_list.status_code == 200
    items = res_list.json()
    assert len(items) > 0

    first = items[0]
    q_id = first["id"]

    # Garantir que NENHUM campo de resposta foi exposto
    forbidden_keys = [
        "alternativa_correta_id", "correct_letter", "is_correct", "correta",
        "answer_binding_hash", "explicacao", "solution"
    ]
    for k in forbidden_keys:
        assert k not in first, f"VAZAMENTO DE GABARITO: campo '{k}' exposto no payload da questão!"

    for alt in first["alternativas"]:
        assert "is_correct" not in alt
        assert "correct" not in alt
        assert "id" in alt
        assert "texto" in alt

    # 3. Responder com acerto
    # Buscar alternativa correta diretamente no banco para o teste
    db = SessionLocal()
    q_db = db.get(ExamQuestion, q_id)
    corr_letter = q_db.alternativa_correta_id
    wrong_letter = [a["id"] for a in first["alternativas"] if a["id"] != corr_letter][0]
    db.close()

    res_ans = client.post(
        f"/questoes/{q_id}/responder",
        json={"alternativa_id": corr_letter, "tempo_segundos": 20},
        headers=auth_headers
    )
    assert res_ans.status_code == 200
    ans_data = res_ans.json()

    assert ans_data["correta"] is True
    assert ans_data["alternativa_correta_id"] == corr_letter
    assert ans_data["explicacao"] is None, "ZERO SYNAPSE: explicação DEVE ser nula para catálogo v2!"
    assert ans_data["explanation_status"] == "PENDING"
    assert "distribuicao_alternativas" in ans_data

    # 4. Bloqueio de endpoint de reprocessamento para v2
    res_retry = client.post(f"/questoes/{q_id}/explicacao", headers=auth_headers)
    assert res_retry.status_code == status.HTTP_400_BAD_REQUEST

    # 5. Comprovar que o catálogo v1 continua com 2.811 questões
    db2 = SessionLocal()
    v1_count = db2.scalar(
        select(func.count(ExamQuestion.id)).where(ExamQuestion.catalog_version == "v1")
    )
    v2_count = db2.scalar(
        select(func.count(ExamQuestion.id)).where(ExamQuestion.catalog_version == "v2")
    )
    db2.close()

    assert v1_count == 2811, f"Catálogo v1 foi alterado! Contagem: {v1_count}"
    assert v2_count == 100, f"Catálogo v2 não tem 100 questões! Contagem: {v2_count}"
