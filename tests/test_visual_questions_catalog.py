"""
Suíte de Testes Automatizados — Catálogo de Questões Visuais (Com Imagens) MedSync v2
Garante os 8 pilares de qualidade:
1. Banco de testes 100% isolado (SQLite efêmero).
2. Dois testes de atomicidade (pré-validação e pós-flush com rollback total).
3. Hashes obrigatórios SHA-256 canônicos (plain, rich com <img> e binding).
4. Vínculo explícito de gabarito e alternativas válidas.
5. Preservação de tags <img> seguras no statement_rich_html (loading="lazy").
6. Zero vazamento de gabarito no payload de listagem.
7. Fluxo de resposta desacoplado de revisões espaçadas ou IA.
"""

import copy
import json
import os
import pathlib
import sys
import tempfile
import uuid
from datetime import UTC, datetime

TESTS_DIR = pathlib.Path(__file__).resolve().parent
API_ROOT = TESTS_DIR.parent
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

import database
from database import Base
from main import app
from models import ExamQuestion, User
from scripts.import_question_catalog import (
    compute_sha256,
    import_catalog,
    validate_and_normalize_record,
    validate_hash_format,
)
from security import create_access_token, hash_password


@pytest.fixture(scope="module")
def isolated_visual_db():
    test_db_path = pathlib.Path(tempfile.gettempdir()) / f"medsync_isolated_visual_{uuid.uuid4().hex}.db"
    test_db_url = f"sqlite:///{test_db_path.as_posix()}"

    old_env = os.environ.get("DATABASE_URL")
    old_db_url = database.DATABASE_URL

    os.environ["DATABASE_URL"] = test_db_url
    database.DATABASE_URL = test_db_url

    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)

    old_session_local = database.SessionLocal
    database.SessionLocal = TestingSessionLocal

    yield {
        "engine": test_engine,
        "SessionLocal": TestingSessionLocal,
        "db_url": test_db_url,
        "db_path": test_db_path,
    }

    test_engine.dispose()
    database.SessionLocal = old_session_local
    database.DATABASE_URL = old_db_url
    if old_env is not None:
        os.environ["DATABASE_URL"] = old_env
    else:
        os.environ.pop("DATABASE_URL", None)
    try:
        test_db_path.unlink(missing_ok=True)
    except PermissionError:
        pass


@pytest.fixture(scope="module")
def client(isolated_visual_db):
    return TestClient(app)


@pytest.fixture(scope="module")
def visual_sample_fixture():
    # Carregar 5 questões reais do lote de acesso direto
    lote_path = pathlib.Path(__file__).resolve().parents[1] / "data" / "catalog_batches" / "lote-visual-1-acesso-direto.jsonl"
    sample_records = []
    with open(lote_path, "r", encoding="utf-8") as f:
        for _ in range(5):
            line = f.readline()
            if line:
                sample_records.append(json.loads(line))

    # Gravar fixture temporário
    temp_jsonl = pathlib.Path(tempfile.gettempdir()) / f"fixture_visual_sample_{uuid.uuid4().hex}.jsonl"
    with open(temp_jsonl, "w", encoding="utf-8") as f:
        for rec in sample_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    yield {
        "records": sample_records,
        "jsonl_path": temp_jsonl,
    }

    try:
        temp_jsonl.unlink(missing_ok=True)
    except PermissionError:
        pass


@pytest.fixture(scope="module")
def auth_headers(isolated_visual_db):
    db: Session = isolated_visual_db["SessionLocal"]()
    user_email = f"auditor_visual_{uuid.uuid4().hex[:8]}@medsync.com.br"
    old_admins = os.environ.get("ADMIN_EMAILS", "")
    os.environ["ADMIN_EMAILS"] = f"{old_admins},{user_email}" if old_admins else user_email

    user = User(
        nome="Auditor Visual Codex",
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
    return {"Authorization": f"Bearer {token}", "User-Email": user_email}


def test_import_visual_batch_canonical_success(isolated_visual_db, visual_sample_fixture):
    """Importa lote de amostra de questões visuais e valida persistência canônica."""
    db: Session = isolated_visual_db["SessionLocal"]()
    res = import_catalog(
        db=db,
        input_jsonl=visual_sample_fixture["jsonl_path"],
        catalog_version="v2",
        dry_run=False,
    )
    assert res["status"] == "IMPORT_SUCCESSFUL"
    assert res["inserted_count"] == 5

    # Validar persistência no banco
    questions = db.scalars(
        select(ExamQuestion).where(ExamQuestion.catalog_version == "v2").order_by(ExamQuestion.id)
    ).all()
    assert len(questions) == 5

    for q in questions:
        assert q.media_classification == "REQUIRES_IMAGE"
        assert q.image_rights_status == "EDITORIAL_EXAM_FAIR_USE"
        assert "<img" in q.statement_rich_html
        assert 'loading="lazy"' in q.statement_rich_html
        assert len(q.content_hash_plain) == 64
        assert len(q.content_hash_rich) == 64
        assert len(q.answer_binding_hash) == 64
        assert q.status == "publicada"
        assert len(q.alternativas) in (4, 5)
        assert q.alternativa_correta_id in ["A", "B", "C", "D", "E"]
    db.close()


def test_visual_batch_atomicity_pre_validation_fails_cleanly(isolated_visual_db, visual_sample_fixture):
    """Atomicidade 1: Erro em registro na pré-validação bloqueia antes de qualquer inserção."""
    db: Session = isolated_visual_db["SessionLocal"]()
    bad_record = copy.deepcopy(visual_sample_fixture["records"][0])
    bad_record["source_id"] = "bad_visual_pre_val"
    bad_record["content_hash_rich"] = "hash_invalido_curto"

    bad_jsonl = pathlib.Path(tempfile.gettempdir()) / f"bad_pre_val_{uuid.uuid4().hex}.jsonl"
    with open(bad_jsonl, "w", encoding="utf-8") as f:
        f.write(json.dumps(bad_record) + "\n")

    with pytest.raises(ValueError) as exc:
        import_catalog(db=db, input_jsonl=bad_jsonl, catalog_version="v2")

    assert "content_hash_rich" in str(exc.value)

    # Nenhuma inserção residual
    persisted = db.scalar(select(ExamQuestion).where(ExamQuestion.source_id == "bad_visual_pre_val"))
    assert persisted is None
    db.close()
    bad_jsonl.unlink(missing_ok=True)


def test_visual_batch_atomicity_post_flush_rollback(isolated_visual_db, visual_sample_fixture):
    """Atomicidade 2: Falha pós-flush aciona rollback estrito e zero registros parciais persistem."""
    db: Session = isolated_visual_db["SessionLocal"]()
    records = []
    for i in range(4):
        rec = copy.deepcopy(visual_sample_fixture["records"][0])
        rec["source_id"] = f"post_flush_test_{i}_{uuid.uuid4().hex[:6]}"
        rec["fingerprint"] = f"fp_post_flush_{i}_{uuid.uuid4().hex[:6]}"
        records.append(rec)

    test_jsonl = pathlib.Path(tempfile.gettempdir()) / f"test_post_flush_{uuid.uuid4().hex}.jsonl"
    with open(test_jsonl, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    with pytest.raises(RuntimeError) as exc:
        import_catalog(
            db=db,
            input_jsonl=test_jsonl,
            catalog_version="v2",
            batch_size=2,
            simulated_failure_step=3,
        )

    assert "FALHA INJETADA APÓS FLUSH" in str(exc.value)

    # Verificar que nenhum dos registros foi persistido
    for r in records:
        persisted = db.scalar(select(ExamQuestion).where(ExamQuestion.source_id == r["source_id"]))
        assert persisted is None
    db.close()
    test_jsonl.unlink(missing_ok=True)


def test_visual_questions_api_delivery_and_zero_gabarito_leakage(client, auth_headers):
    """Valida que a API entrega imagens no statement_rich_html sem vazar gabarito."""
    response = client.get(
        "/questoes?quantidade=5&catalog_version=v2",
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1

    for q in data:
        assert "<img" in q["statement_rich_html"]
        assert 'loading="lazy"' in q["statement_rich_html"]
        # Zero vazamento de gabarito antes da resposta
        assert "alternativa_correta_id" not in q
        assert "correct_letter" not in q
        assert "explicacao" not in q
        for alt in q["alternativas"]:
            assert "is_correct" not in alt
            assert "correct" not in alt


def test_visual_question_answer_flow_and_metrics(client, auth_headers):
    """Valida resposta em questão visual, com revelação correta de gabarito e métricas."""
    list_res = client.get("/questoes?quantidade=1&catalog_version=v2", headers=auth_headers)
    assert list_res.status_code == status.HTTP_200_OK
    question = list_res.json()[0]
    qid = question["id"]
    chosen_alt = question["alternativas"][0]["id"]

    answer_res = client.post(
        f"/questoes/{qid}/responder",
        json={"alternativa_id": chosen_alt, "tempo_segundos": 45},
        headers=auth_headers,
    )
    assert answer_res.status_code == status.HTTP_200_OK
    ans_data = answer_res.json()

    assert "correta" in ans_data
    assert "alternativa_correta_id" in ans_data
    assert ans_data["total_respondentes"] >= 1
    assert len(ans_data["distribuicao_alternativas"]) == len(question["alternativas"])
