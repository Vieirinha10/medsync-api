import os
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alembic.config import Config
from alembic import command

try:
    command.upgrade(Config("alembic.ini"), "head")
except Exception:
    pass

from database import Base, SessionLocal, engine
from main import app
from models import ExamQuestion, QuestionAttempt, User
from scripts.import_question_catalog import import_catalog, rollback_catalog

client = TestClient(app)

SAMPLE_JSONL = Path(
    r"C:\Users\rgust\Documents\medsync-question-full-catalog-audit-v1.1\samples\pilot-100-import-ready.jsonl"
)


def _get_auth_headers(email: str = "pilot-tester@example.com") -> dict:
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email.lower()))
        if not user:
            reg = client.post(
                "/usuarios/registrar",
                json={
                    "nome": "Pilot Tester",
                    "email": email,
                    "periodo_curso": 8,
                    "faculdade": "UFCE",
                    "password": "senha-segura-123",
                    "aceite_termos": True,
                },
            )
            assert reg.status_code == 201
            user = db.scalar(select(User).where(User.email == email.lower()))
            user.email_verified_at = datetime.now(UTC)
            user.email_verification_token_hash = None
            db.commit()

    login = client.post(
        "/usuarios/login",
        json={"email": email, "password": "senha-segura-123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestQuestionCatalogV2Pilot:
    def test_01_dry_run_and_import_exact_count(self):
        with SessionLocal() as db:
            # 1. Dry-run
            dry_report = import_catalog(
                db=db,
                jsonl_path=SAMPLE_JSONL,
                catalog_version="v2",
                dry_run=True,
            )
            assert dry_report["status"] == "DRY_RUN_PASSED"
            assert dry_report["total_validated"] == 100

            # 2. Importação Real
            rep = import_catalog(
                db=db,
                jsonl_path=SAMPLE_JSONL,
                catalog_version="v2",
                dry_run=False,
            )
            assert rep["status"] == "IMPORT_SUCCESSFUL"

            total_v2 = db.scalar(
                select(func.count(ExamQuestion.id)).where(ExamQuestion.catalog_version == "v2")
            )
            assert total_v2 == 100, f"Esperava 100 questões v2, encontrou {total_v2}"

            source_ids = db.scalars(
                select(ExamQuestion.source_id).where(ExamQuestion.catalog_version == "v2")
            ).all()
            assert len(source_ids) == 100
            assert len(set(source_ids)) == 100

    def test_02_idempotency_second_run(self):
        with SessionLocal() as db:
            rep = import_catalog(
                db=db,
                jsonl_path=SAMPLE_JSONL,
                catalog_version="v2",
                dry_run=False,
            )
            assert rep["status"] == "IMPORT_SUCCESSFUL"

            total_v2 = db.scalar(
                select(func.count(ExamQuestion.id)).where(ExamQuestion.catalog_version == "v2")
            )
            assert total_v2 == 100, f"Esperava continuar 100 após re-importação, encontrou {total_v2}"

    def test_03_get_questions_no_answer_leak(self):
        headers = _get_auth_headers("pilot-test-get@example.com")
        res = client.get("/questoes?catalog_version=v2&quantidade=10", headers=headers)
        assert res.status_code == 200
        items = res.json()
        assert len(items) == 10

        for q in items:
            assert q["catalog_version"] == "v2"
            assert "alternativa_correta_id" not in q
            assert "correct_letter" not in q
            assert "explicacao" not in q
            assert "answer_binding_hash" not in q
            for alt in q["alternativas"]:
                assert "is_correct" not in alt
                assert "correta" not in alt

    def test_04_answer_correct_and_incorrect_zero_synapse(self, monkeypatch):
        synapse_called = []

        def fake_generate(q):
            synapse_called.append(q.id)
            raise RuntimeError("SYNAPSE_WAS_CALLED_ERROR")

        monkeypatch.setattr("routers.questions.generate_question_explanation", fake_generate)

        headers = _get_auth_headers("pilot-test-ans@example.com")
        res = client.get("/questoes?catalog_version=v2&quantidade=2", headers=headers)
        items = res.json()
        q1 = items[0]
        q2 = items[1]

        with SessionLocal() as db:
            db_q1 = db.get(ExamQuestion, q1["id"])
            real_correct = db_q1.alternativa_correta_id
            db_q2 = db.get(ExamQuestion, q2["id"])
            wrong_alt = [a["id"] for a in db_q2.alternativas if a["id"] != db_q2.alternativa_correta_id][0]

        # Resposta Correta
        ans1 = client.post(
            f"/questoes/{q1['id']}/responder",
            headers=headers,
            json={"alternativa_id": real_correct, "tempo_segundos": 15},
        )
        assert ans1.status_code == 200
        data1 = ans1.json()
        assert data1["correta"] is True
        assert data1["alternativa_correta_id"] == real_correct
        assert data1["explicacao"] is None
        assert data1["explanation_status"] == "PENDING"
        assert len(synapse_called) == 0, "Synapse NÃO deveria ser chamada!"

        # Resposta Incorreta
        ans2 = client.post(
            f"/questoes/{q2['id']}/responder",
            headers=headers,
            json={"alternativa_id": wrong_alt, "tempo_segundos": 20},
        )
        assert ans2.status_code == 200
        data2 = ans2.json()
        assert data2["correta"] is False
        assert data2["explicacao"] is None
        assert data2["explanation_status"] == "PENDING"
        assert len(synapse_called) == 0, "Synapse NÃO deveria ser chamada!"

    def test_05_invalid_alternative_and_nonexistent_question(self):
        headers = _get_auth_headers("pilot-test-err@example.com")
        res = client.get("/questoes?catalog_version=v2&quantidade=1", headers=headers)
        q = res.json()[0]

        bad_ans = client.post(
            f"/questoes/{q['id']}/responder",
            headers=headers,
            json={"alternativa_id": "Z"},
        )
        assert bad_ans.status_code == 422

        bad_q = client.post(
            "/questoes/99999999/responder",
            headers=headers,
            json={"alternativa_id": "A"},
        )
        assert bad_q.status_code == 404

    def test_06_retry_explanation_blocked_for_v2(self):
        headers = _get_auth_headers("pilot-test-retry@example.com")
        res = client.get("/questoes?catalog_version=v2&quantidade=1", headers=headers)
        q = res.json()[0]

        retry = client.post(f"/questoes/{q['id']}/explicacao", headers=headers)
        assert retry.status_code == 400
        assert "preparação" in retry.json()["detail"].lower()

    def test_07_specialty_filter_and_random_rank(self):
        headers = _get_auth_headers("pilot-test-filter@example.com")
        res = client.get(
            "/questoes?catalog_version=v2&especialidade=Cirurgia&quantidade=5",
            headers=headers,
        )
        assert res.status_code == 200
        items = res.json()
        for item in items:
            assert item["especialidade"] == "Cirurgia"

    def test_08_rollback_and_catalog_v1_integrity(self):
        with SessionLocal() as db:
            count_v1_before = db.scalar(
                select(func.count(ExamQuestion.id)).where(ExamQuestion.catalog_version == "v1")
            )
            rollback_catalog(db, "v2")

            count_v2_after = db.scalar(
                select(func.count(ExamQuestion.id)).where(ExamQuestion.catalog_version == "v2")
            )
            assert count_v2_after == 0

            count_v1_after = db.scalar(
                select(func.count(ExamQuestion.id)).where(ExamQuestion.catalog_version == "v1")
            )
            assert count_v1_after == count_v1_before

            # Reimportar
            import_catalog(
                db=db,
                jsonl_path=SAMPLE_JSONL,
                catalog_version="v2",
                dry_run=False,
            )
            count_v2_reimported = db.scalar(
                select(func.count(ExamQuestion.id)).where(ExamQuestion.catalog_version == "v2")
            )
            assert count_v2_reimported == 100
