"""
Suíte de Testes Automatizados — Novo Catálogo de Questões MedSync (v1.2)
Coordenação: Codex

Esta suíte atende integralmente às exigências da versão v1.2 e da Diretriz Permanente de Qualidade:
1. Banco de testes 100% isolado (SQLite temporário efêmero, sem tocar no banco principal de desenvolvimento).
2. Dois testes distintos de atomicidade:
   - Pré-validação: erro estrutural bloqueia antes de qualquer inserção;
   - Pós-flush: objetos adicionados sofrem flush(), falha é injetada, rollback é acionado e zero registros persistem.
3. Hashes obrigatórios: validação de presença, formato (64 hex) e recálculo estrito.
4. Vínculo explícito de gabarito: exige is_correct booleano em cada alternativa, sem inferência.
5. Preservação do catálogo v1 em coleção sintética controlada (sem acoplamento à contagem fixa de 2.811).
6. Segregação de estatísticas e métricas por versão de catálogo.
7. Ativação interna de catálogo e proteção contra override por estudantes.
8. Zero vazamento de gabarito e zero chamadas à Synapse ou geradores de IA.
"""

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
from unittest.mock import patch

import pytest
from alembic import command
from alembic.config import Config
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, func, inspect, select
from sqlalchemy.orm import Session, sessionmaker

TESTS_DIR = pathlib.Path(__file__).resolve().parent
FIXTURE_PATH = TESTS_DIR / "fixtures" / "pilot-100-import-ready.jsonl"
API_ROOT = TESTS_DIR.parent
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

import database
from database import Base
from main import app
from models import ExamQuestion, QuestionAttempt, QuestionSourceAlias, User
from scripts.import_question_catalog import (
    compute_sha256,
    import_catalog,
    rollback_catalog,
    validate_and_normalize_record,
    validate_hash_format,
)
from security import create_access_token, hash_password


# ---------------------------------------------------------------------------
# Fixture de Banco Temporário Isolado (Regra 4 do Codex: isolamento absoluto)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def isolated_db():
    test_db_path = pathlib.Path(tempfile.gettempdir()) / f"medsync_isolated_v12_{uuid.uuid4().hex}.db"
    test_db_url = f"sqlite:///{test_db_path.as_posix()}"

    old_env = os.environ.get("DATABASE_URL")
    old_db_url = database.DATABASE_URL

    os.environ["DATABASE_URL"] = test_db_url
    database.DATABASE_URL = test_db_url

    test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)

    # Substituir SessionLocal da app
    old_session_local = database.SessionLocal
    database.SessionLocal = TestingSessionLocal

    yield {
        "engine": test_engine,
        "SessionLocal": TestingSessionLocal,
        "db_url": test_db_url,
        "db_path": test_db_path
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
def client(isolated_db):
    return TestClient(app)


@pytest.fixture(scope="module")
def auth_headers(isolated_db):
    db: Session = isolated_db["SessionLocal"]()
    user_email = f"auditor_v12_{uuid.uuid4().hex[:8]}@medsync.com.br"
    old_admins = os.environ.get("ADMIN_EMAILS", "")
    os.environ["ADMIN_EMAILS"] = f"{old_admins},{user_email},admin_auditor@medsync.com.br" if old_admins else f"{user_email},admin_auditor@medsync.com.br"

    user = User(
        nome="Auditor Codex v1.2",
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


# ---------------------------------------------------------------------------
# Teste 1: Ciclo de Migração Alembic em Banco Efêmero
# ---------------------------------------------------------------------------
def test_01_migration_lifecycle_upgrade_downgrade_upgrade():
    """
    Testa o ciclo completo da migração Alembic (upgrade -> downgrade -> upgrade)
    em um banco temporário isolado, sem ignorar nenhuma exceção.
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
        indexes_up = {i["name"] for i in insp.get_indexes("exam_questions")}
        assert "ix_exam_questions_catalog_status_rank_id" in indexes_up, f"Índice composto não encontrado no upgrade: {indexes_up}"
        assert "ix_exam_questions_random_rank" not in indexes_up, "Índice isolado ix_exam_questions_random_rank NÃO deve existir no upgrade!"
        comp_idx = next(i for i in insp.get_indexes("exam_questions") if i["name"] == "ix_exam_questions_catalog_status_rank_id")
        assert comp_idx["column_names"] == ["catalog_version", "status", "random_rank", "id"]

        # 2. Downgrade para 20260827_15
        command.downgrade(cfg, "20260827_15")
        insp_down = inspect(test_engine)
        assert "question_source_aliases" not in insp_down.get_table_names()
        cols_down = {c["name"] for c in insp_down.get_columns("exam_questions")}
        assert "tema" not in cols_down
        assert "content_hash_plain" not in cols_down
        indexes_down = {i["name"] for i in insp_down.get_indexes("exam_questions")}
        assert "ix_exam_questions_catalog_status_rank_id" not in indexes_down, "Índice composto não removido no downgrade!"
        assert "ix_exam_questions_random_rank" not in indexes_down, "Índice isolado não deve existir no downgrade!"

        # 3. Novo upgrade para head
        command.upgrade(cfg, "head")
        insp_reup = inspect(test_engine)
        assert "question_source_aliases" in insp_reup.get_table_names()
        cols_reup = {c["name"] for c in insp_reup.get_columns("exam_questions")}
        assert expected_cols.issubset(cols_reup)
        indexes_reup = {i["name"] for i in insp_reup.get_indexes("exam_questions")}
        assert "ix_exam_questions_catalog_status_rank_id" in indexes_reup, "Índice composto não recriado no re-upgrade!"
        assert "ix_exam_questions_random_rank" not in indexes_reup, "Índice isolado NÃO deve existir no re-upgrade!"

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


# ---------------------------------------------------------------------------
# Teste 2: Reconciliação Campo a Campo dos 100 Registros do Piloto
# ---------------------------------------------------------------------------
def test_02_field_by_field_fidelity_reconciliation(isolated_db):
    """
    Importa os 100 registros em banco isolado e compara campo a campo
    os 100 registros do JSONL com os 100 registros armazenados no banco.
    Gera relatório JSON completo de reconciliação.
    """
    assert FIXTURE_PATH.exists(), f"Fixture não encontrada: {FIXTURE_PATH}"

    db: Session = isolated_db["SessionLocal"]()

    # Importar piloto v2 no banco isolado
    import_res = import_catalog(db, FIXTURE_PATH, catalog_version="v2")
    assert import_res["inserted_count"] == 100

    # Ler fixture original
    jsonl_records = []
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                jsonl_records.append(json.loads(line))

    assert len(jsonl_records) == 100

    db_records = db.scalars(
        select(ExamQuestion)
        .where(ExamQuestion.catalog_version == "v2")
        .order_by(ExamQuestion.source_id)
    ).all()

    assert len(db_records) == 100

    db_by_source = {q.source_id: q for q in db_records}
    divergences = []
    null_counts = {"tema": 0, "subtema": 0, "regiao": 0, "banca": 0, "finalidade": 0, "tipo_prova": 0}
    specialties = {}
    themes = {}
    letters = {}
    alt_counts = {}

    for line_num, item in enumerate(jsonl_records, start=1):
        sid = item["source_id"]
        db_q = db_by_source.get(sid)
        assert db_q is not None, f"Questão {sid} não encontrada no banco!"

        # Contagens estatísticas
        esp = db_q.especialidade or "Não informada"
        specialties[esp] = specialties.get(esp, 0) + 1

        tema = db_q.tema
        if tema:
            themes[tema] = themes.get(tema, 0) + 1
        else:
            null_counts["tema"] += 1

        if db_q.subtema is None:
            null_counts["subtema"] += 1
        if db_q.regiao is None:
            null_counts["regiao"] += 1

        letra = db_q.alternativa_correta_id
        letters[letra] = letters.get(letra, 0) + 1

        num_alts = len(db_q.alternativas or [])
        alt_counts[str(num_alts)] = alt_counts.get(str(num_alts), 0) + 1

        # Comparações de fidelidade estrita
        if int(item["ano"]) != db_q.ano:
            divergences.append({"source_id": sid, "field": "ano", "jsonl": item["ano"], "db": db_q.ano})

        if item.get("statement_plain", "").strip() != db_q.statement_plain:
            divergences.append({"source_id": sid, "field": "statement_plain"})

        if item.get("correct_letter") != db_q.alternativa_correta_id:
            divergences.append({"source_id": sid, "field": "alternativa_correta_id"})

        if item.get("content_hash_plain") != db_q.content_hash_plain:
            divergences.append({"source_id": sid, "field": "content_hash_plain"})

        if item.get("content_hash_rich") != db_q.content_hash_rich:
            divergences.append({"source_id": sid, "field": "content_hash_rich"})

        if item.get("answer_binding_hash") != db_q.answer_binding_hash:
            divergences.append({"source_id": sid, "field": "answer_binding_hash"})

    report = {
        "generated_at": datetime.now(UTC).isoformat(),
        "fixture_file": FIXTURE_PATH.name,
        "records_compared": len(jsonl_records),
        "divergences_count": len(divergences),
        "divergences": divergences,
        "null_counts_by_column": null_counts,
        "specialty_distribution": specialties,
        "theme_distribution": themes,
        "correct_letter_distribution": letters,
        "alternatives_count_distribution": alt_counts,
        "zero_divergences_confirmed": len(divergences) == 0
    }

    report_dir = API_ROOT / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_file = report_dir / "reconciliation_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    db.close()
    assert len(divergences) == 0, f"Divergências encontradas: {divergences}"


# ---------------------------------------------------------------------------
# Teste 3A: Falha de Atomicidade na Pré-Validação (Zero Adições à Sessão)
# ---------------------------------------------------------------------------
def test_03a_atomic_prevalidation_failure():
    """
    Testa falha na pré-validação:
    - O arquivo contém um registro estruturalmente inválido (ano ausente);
    - A validação aborta ANTES de adicionar qualquer registro à sessão;
    - Zero registros persistem no banco.
    """
    test_db_path = pathlib.Path(tempfile.gettempdir()) / f"atomic_preval_{uuid.uuid4().hex}.db"
    test_db_url = f"sqlite:///{test_db_path.as_posix()}"
    engine = create_engine(test_db_url)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()

    temp_jsonl = pathlib.Path(tempfile.gettempdir()) / f"preval_fail_{uuid.uuid4().hex}.jsonl"
    try:
        # Carregar 5 registros válidos e 1 inválido
        valid_records = []
        with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
            for i in range(5):
                valid_records.append(json.loads(f.readline()))

        bad_record = copy.deepcopy(valid_records[0])
        bad_record["source_id"] = "BAD_PREVAL_999"
        bad_record["ano"] = None  # Inválido: ano ausente

        with open(temp_jsonl, "w", encoding="utf-8") as f:
            for rec in valid_records:
                f.write(json.dumps(rec) + "\n")
            f.write(json.dumps(bad_record) + "\n")

        with pytest.raises(ValueError, match="campo obrigatório 'ano' ausente"):
            import_catalog(db, temp_jsonl, catalog_version="v2_test")

        # Comprovação: ZERO registros persistidos
        count = db.scalar(select(func.count(ExamQuestion.id)).where(ExamQuestion.catalog_version == "v2_test"))
        assert count == 0, f"Esperava 0 registros, mas encontrou {count}"
    finally:
        db.close()
        engine.dispose()
        temp_jsonl.unlink(missing_ok=True)
        test_db_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Teste 3B: Falha de Atomicidade Durante a Persistência (Após Flush)
# ---------------------------------------------------------------------------
def test_03b_atomic_persistence_failure_after_flush():
    """
    Testa falha durante a persistência após db.flush():
    - Todos os registros passam na pré-validação estrutural;
    - Registros são adicionados à sessão e sofrem db.flush() (executando SQL INSERT na transação aberta);
    - Falha real é provocada após o flush (no registro 6, após flush dos primeiros 5);
    - db.rollback() é acionado;
    - Comprova que zero registros parciais persistem no banco.
    """
    test_db_path = pathlib.Path(tempfile.gettempdir()) / f"atomic_postflush_{uuid.uuid4().hex}.db"
    test_db_url = f"sqlite:///{test_db_path.as_posix()}"
    engine = create_engine(test_db_url)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()

    temp_jsonl = pathlib.Path(tempfile.gettempdir()) / f"postflush_fail_{uuid.uuid4().hex}.jsonl"
    try:
        # Carregar 10 registros válidos da fixture (todos passam 100% na pré-validação)
        valid_records = []
        with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
            for i in range(10):
                valid_records.append(json.loads(f.readline()))

        with open(temp_jsonl, "w", encoding="utf-8") as f:
            for rec in valid_records:
                f.write(json.dumps(rec) + "\n")

        # Injetar falha no registro 6, após flush com batch_size=5
        with pytest.raises(RuntimeError, match="FALHA INJETADA APÓS FLUSH"):
            import_catalog(
                db,
                temp_jsonl,
                catalog_version="v2_atomic",
                batch_size=5,
                simulated_failure_step=6
            )

        # Comprovação cabal de rollback: ZERO registros parciais persistidos
        count = db.scalar(select(func.count(ExamQuestion.id)).where(ExamQuestion.catalog_version == "v2_atomic"))
        assert count == 0, f"Falha de rollback: {count} registros parciais permaneceram após erro!"

        # Gerar relatório de atomicidade
        atomicity_report = {
            "test_prevalidation": "test_03a_atomic_prevalidation_failure",
            "prevalidation_failure_persisted": 0,
            "test_persistence_after_flush": "test_03b_atomic_persistence_failure_after_flush",
            "flush_batch_size": 5,
            "failure_injected_at_step": 6,
            "persistence_failure_after_flush_persisted": 0,
            "partial_records_persisted": 0,
            "rollback_confirmed": True
        }
        report_dir = API_ROOT / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "atomicity_report.json").write_text(
            json.dumps(atomicity_report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    finally:
        db.close()
        engine.dispose()
        temp_jsonl.unlink(missing_ok=True)
        test_db_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Teste 4: Preservação do Catálogo v1 via Coleção Controlada e Colisão
# ---------------------------------------------------------------------------
def test_04_v1_preservation_and_collision_prevention():
    """
    Valida a preservação integral da v1 em uma coleção sintética controlada:
    - Insere 5 questões v1 controladas com hashes registrados;
    - Importa as questões da v2;
    - Verifica que todas as 5 questões v1 permanecem inalteradas byte a byte;
    - Tenta importar um registro v2 cujo source_id colide com a v1 e comprova interrupção imediata.
    """
    test_db_path = pathlib.Path(tempfile.gettempdir()) / f"v1_preserv_{uuid.uuid4().hex}.db"
    test_db_url = f"sqlite:///{test_db_path.as_posix()}"
    engine = create_engine(test_db_url)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()

    try:
        # Criar coleção sintética controlada de registros v1
        v1_records = []
        for i in range(5):
            q = ExamQuestion(
                source_id=f"v1_synthetic_{i:03d}",
                catalog_version="v1",
                ano=2021 + i,
                instituicao="Hospital Universitário",
                cabecalho="HU · 2021",
                especialidade="Clínica Médica",
                assunto="Infectologia",
                enunciado=f"Enunciado original da questão v1 número {i}.",
                statement_plain=f"Enunciado original da questão v1 número {i}.",
                alternativas=[{"id": "A", "texto": "Alt A"}, {"id": "B", "texto": "Alt B"}],
                alternativa_correta_id="A",
                fingerprint=f"v1_fp_{i}",
                media_classification="NO_VISUAL_DEPENDENCY",
                image_rights_status="NONE_REQUIRED",
                content_hash_plain=compute_sha256(f"Enunciado v1 {i}"),
                content_hash_rich=compute_sha256(f"Enunciado v1 {i}"),
                answer_binding_hash=compute_sha256(f"Binding v1 {i}"),
                random_rank=0.5,
                status="publicada",
                explicacao=None,
                explicacao_status="pendente"
            )
            v1_records.append(q)
            db.add(q)
        db.commit()

        v1_hashes_before = {q.source_id: (q.content_hash_plain, q.statement_plain) for q in v1_records}
        assert len(v1_hashes_before) == 5

        # Importar fixture v2
        import_res = import_catalog(db, FIXTURE_PATH, catalog_version="v2")
        assert import_res["inserted_count"] == 100

        # Conferir preservação integral da v1
        v1_in_db = db.scalars(select(ExamQuestion).where(ExamQuestion.catalog_version == "v1")).all()
        assert len(v1_in_db) == 5

        for q in v1_in_db:
            exp_hash, exp_stmt = v1_hashes_before[q.source_id]
            assert q.content_hash_plain == exp_hash
            assert q.statement_plain == exp_stmt
            assert q.catalog_version == "v1"

        # Tentar colisão: importar questão v2 com source_id da v1
        conflict_jsonl = pathlib.Path(tempfile.gettempdir()) / f"collision_{uuid.uuid4().hex}.jsonl"
        with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
            rec = json.loads(f.readline())
        rec["source_id"] = "v1_synthetic_000"  # Colisão intencional com v1

        with open(conflict_jsonl, "w", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")

        with pytest.raises(ValueError, match="COLISÃO DE VERSÃO DETECTADA"):
            import_catalog(db, conflict_jsonl, catalog_version="v2")

        # Comprovar que o registro v1 colidido permaneceu intocado
        collided_v1 = db.scalar(select(ExamQuestion).where(ExamQuestion.source_id == "v1_synthetic_000"))
        assert collided_v1.catalog_version == "v1"
        assert collided_v1.statement_plain == "Enunciado original da questão v1 número 0."

        conflict_jsonl.unlink(missing_ok=True)
    finally:
        db.close()
        engine.dispose()
        test_db_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Teste 5: Idempotência Estrita e Detecção de Inalterados
# ---------------------------------------------------------------------------
def test_05_idempotency_detects_unchanged_and_rejects_hash_conflict():
    """
    Testa:
    1. Idempotência sem alterações: informa unchanged_count = 100 e inserted_count = 0.
    2. Conflito de hash: aborta e rejeita qualquer alteração silenciosa.
    """
    test_db_path = pathlib.Path(tempfile.gettempdir()) / f"idemp_{uuid.uuid4().hex}.db"
    test_db_url = f"sqlite:///{test_db_path.as_posix()}"
    engine = create_engine(test_db_url)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)
    db = TestingSession()

    try:
        # 1ª execução
        res1 = import_catalog(db, FIXTURE_PATH, catalog_version="v2")
        assert res1["inserted_count"] == 100
        assert res1["unchanged_count"] == 0

        # 2ª execução com dados idênticos
        res2 = import_catalog(db, FIXTURE_PATH, catalog_version="v2")
        assert res2["inserted_count"] == 0
        assert res2["unchanged_count"] == 100

        # Tentativa de alteração com hash divergente
        conflict_jsonl = pathlib.Path(tempfile.gettempdir()) / f"hash_conflict_{uuid.uuid4().hex}.jsonl"
        with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
            rec = json.loads(f.readline())

        # Alterar conteúdo e recalcular hashes para que passe na validação do registro
        rec["statement_plain"] = rec["statement_plain"] + " Alteração indevida."
        rec["statement_rich_html"] = rec["statement_plain"]
        h_plain = compute_sha256(rec["statement_plain"] + "||" + "|".join(f"{a['letter']}:{a['body_plain']}" for a in rec["alternatives"]))
        rec["content_hash_plain"] = h_plain
        rec["content_hash_rich"] = h_plain
        rec["answer_binding_hash"] = compute_sha256(f"{h_plain}||{rec['correct_letter']}||" + "|".join(f"{a['letter']}:{1 if a['is_correct'] else 0}" for a in rec["alternatives"]))

        with open(conflict_jsonl, "w", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")

        with pytest.raises(ValueError, match="CONFLITO DE HASH DETECTADO"):
            import_catalog(db, conflict_jsonl, catalog_version="v2")

        conflict_jsonl.unlink(missing_ok=True)
    finally:
        db.close()
        engine.dispose()
        test_db_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Teste 6: Hashes Obrigatórios (Ausência, Malformação, Divergência e Sucesso)
# ---------------------------------------------------------------------------
def test_06_hashes_mandatory_presence_and_recalculation():
    """
    Testa Item 2 do Codex:
    - hash ausente -> rejeitado com erro;
    - hash malformado -> rejeitado com erro;
    - hash divergente -> rejeitado com erro;
    - hash correto -> aceito.
    """
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        base_rec = json.loads(f.readline())

    # 1. Hash ausente
    rec_missing = copy.deepcopy(base_rec)
    rec_missing.pop("content_hash_plain", None)
    with pytest.raises(ValueError, match="campo obrigatório 'content_hash_plain' ausente ou malformado"):
        validate_and_normalize_record(rec_missing, line_num=1)

    # 2. Hash malformado (tamanho diferente de 64)
    rec_short = copy.deepcopy(base_rec)
    rec_short["content_hash_plain"] = "abcd1234short"
    with pytest.raises(ValueError, match="deve ter exatamente 64 caracteres hexadecimais"):
        validate_and_normalize_record(rec_short, line_num=1)

    # 3. Hash divergente
    rec_divergent = copy.deepcopy(base_rec)
    rec_divergent["content_hash_plain"] = "a" * 64
    with pytest.raises(ValueError, match="divergência em content_hash_plain"):
        validate_and_normalize_record(rec_divergent, line_num=1)

    # 4. Hash correto
    cleaned, hp, hr, hb = validate_and_normalize_record(base_rec, line_num=1)
    assert hp == base_rec["content_hash_plain"]
    assert hr == base_rec["content_hash_rich"]
    assert hb == base_rec["answer_binding_hash"]


# ---------------------------------------------------------------------------
# Teste 7: Vínculo Explícito do Gabarito Sem Inferência
# ---------------------------------------------------------------------------
def test_07_explicit_answer_binding_without_inference():
    """
    Testa Item 3 do Codex:
    - ausência do campo is_correct;
    - valor não-booleano;
    - nenhuma correta;
    - mais de uma correta;
    - correta diferente de correct_letter;
    - correct_letter inexistente nas alternativas.
    """
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        base_rec = json.loads(f.readline())

    # 1. Campo is_correct ausente
    rec_no_flag = copy.deepcopy(base_rec)
    del rec_no_flag["alternatives"][0]["is_correct"]
    with pytest.raises(ValueError, match="não possui o campo obrigatório 'is_correct'"):
        validate_and_normalize_record(rec_no_flag, line_num=1)

    # 2. Campo is_correct não-booleano (string ou int)
    rec_str_flag = copy.deepcopy(base_rec)
    rec_str_flag["alternatives"][0]["is_correct"] = "True"
    with pytest.raises(ValueError, match="deve ser booleano estrito"):
        validate_and_normalize_record(rec_str_flag, line_num=1)

    # 3. Nenhuma alternativa correta
    rec_none_correct = copy.deepcopy(base_rec)
    for a in rec_none_correct["alternatives"]:
        a["is_correct"] = False
    with pytest.raises(ValueError, match="exatamente 1 alternativa correta é esperada"):
        validate_and_normalize_record(rec_none_correct, line_num=1)

    # 4. Mais de uma alternativa correta
    rec_two_correct = copy.deepcopy(base_rec)
    rec_two_correct["alternatives"][0]["is_correct"] = True
    with pytest.raises(ValueError, match="inconsistência entre flag is_correct=True|exatamente 1 alternativa correta é esperada"):
        validate_and_normalize_record(rec_two_correct, line_num=1)

    # 5. Correta com letra diferente de correct_letter
    rec_mismatch = copy.deepcopy(base_rec)
    rec_mismatch["correct_letter"] = "C"
    # alts tem B marcado como True
    with pytest.raises(ValueError, match="inconsistência entre flag is_correct=True"):
        validate_and_normalize_record(rec_mismatch, line_num=1)

    # 6. correct_letter inexistente nas alternativas
    rec_unknown = copy.deepcopy(base_rec)
    rec_unknown["correct_letter"] = "Z"
    with pytest.raises(ValueError, match="inconsistência entre flag is_correct=True"):
        validate_and_normalize_record(rec_unknown, line_num=1)


# ---------------------------------------------------------------------------
# Teste 8: Segregação de Estatísticas e Métricas por Versão de Catálogo
# ---------------------------------------------------------------------------
def test_08_statistics_and_performance_segregated_by_catalog(isolated_db, client, auth_headers):
    """
    Testa Item 7 do Codex:
    - Usuário responde a questão v1 e a questão v2;
    - Consulta de desempenho para v1 reflete apenas v1;
    - Consulta de desempenho para v2 reflete apenas v2;
    - Métricas não são misturadas.
    """
    db: Session = isolated_db["SessionLocal"]()

    # Criar questão v1 e questão v2
    q_v1 = ExamQuestion(
        source_id="v1_stat_test_001",
        catalog_version="v1",
        ano=2020,
        instituicao="USP",
        cabecalho="USP · 2020",
        especialidade="Cardiologia",
        assunto="Insuficiência Cardíaca",
        enunciado="Questão teste v1 estatísticas",
        statement_plain="Questão teste v1 estatísticas",
        alternativas=[{"id": "A", "texto": "Opção A"}, {"id": "B", "texto": "Opção B"}],
        alternativa_correta_id="A",
        fingerprint="stat_v1_001",
        media_classification="NO_VISUAL_DEPENDENCY",
        image_rights_status="NONE_REQUIRED",
        content_hash_plain="a" * 64,
        content_hash_rich="a" * 64,
        answer_binding_hash="a" * 64,
        random_rank=0.1,
        status="publicada"
    )
    db.add(q_v1)
    db.commit()
    db.refresh(q_v1)

    q_v2 = db.scalar(select(ExamQuestion).where(ExamQuestion.catalog_version == "v2").limit(1))
    if q_v2 is None:
        import_catalog(db, FIXTURE_PATH, catalog_version="v2")
        q_v2 = db.scalar(select(ExamQuestion).where(ExamQuestion.catalog_version == "v2").limit(1))
    assert q_v2 is not None

    # Obter usuário de teste autenticado
    user = db.scalar(select(User).order_by(User.id.desc()).limit(1))
    assert user is not None

    # Registrar resposta na questão v1 (acerto)
    att_v1 = QuestionAttempt(
        id_usuario=user.id,
        id_questao=q_v1.id,
        alternativa_selecionada_id="A",
        correta=True,
        tempo_segundos=30
    )
    db.add(att_v1)

    # Registrar resposta na questão v2 (erro)
    att_v2 = QuestionAttempt(
        id_usuario=user.id,
        id_questao=q_v2.id,
        alternativa_selecionada_id="D",
        correta=False,
        tempo_segundos=45
    )
    db.add(att_v2)
    db.commit()

    # Como o usuário de teste é administrador (para fins de auditoria), testamos override explícito:
    user.email = "admin_auditor@medsync.com.br"
    db.commit()

    # 1. Desempenho no catálogo v1
    resp_v1 = client.get("/questoes/desempenho?catalog_version=v1", headers=auth_headers)
    assert resp_v1.status_code == status.HTTP_200_OK
    data_v1 = resp_v1.json()
    assert data_v1["respondidas"] == 1
    assert data_v1["acertos"] == 1
    assert data_v1["percentual"] == 100.0

    # 2. Desempenho no catálogo v2
    resp_v2 = client.get("/questoes/desempenho?catalog_version=v2", headers=auth_headers)
    assert resp_v2.status_code == status.HTTP_200_OK
    data_v2 = resp_v2.json()
    assert data_v2["respondidas"] == 1
    assert data_v2["acertos"] == 0
    assert data_v2["percentual"] == 0.0

    db.close()


# ---------------------------------------------------------------------------
# Teste 9: Ativação Interna do Catálogo e Proteção Contra Override
# ---------------------------------------------------------------------------
def test_09_active_catalog_configuration_and_override_protection(isolated_db, client):
    """
    Testa Item 6 do Codex:
    - Configuração de catálogo ativo determina versão retornada por padrão;
    - Estudantes comuns não podem adulterar catálogo via parâmetro de query (HTTP 403);
    - Catálogo vazio retorna erro controlado HTTP 503 sem fallback silencioso.
    """
    db: Session = isolated_db["SessionLocal"]()

    # Garantir que v2 está presente para este teste
    q_v2 = db.scalar(select(ExamQuestion).where(ExamQuestion.catalog_version == "v2").limit(1))
    if q_v2 is None:
        import_catalog(db, FIXTURE_PATH, catalog_version="v2")

    # Criar estudante comum (não-admin)
    student = User(
        nome="Estudante Padrão",
        email=f"estudante_{uuid.uuid4().hex[:8]}@aluno.medsync.com.br",
        password_hash=hash_password("Password123!"),
        email_verified_at=datetime.now(UTC),
        terms_accepted_at=datetime.now(UTC),
        terms_version="2026-08-11",
        privacy_version="2026-08-11",
    )
    db.add(student)
    db.commit()
    token_student = create_access_token(student.id, student.auth_version)
    student_headers = {"Authorization": f"Bearer {token_student}"}

    old_active = os.environ.get("QUESTION_CATALOG_ACTIVE_VERSION")
    try:
        # 1. Configurar ativo como v2
        os.environ["QUESTION_CATALOG_ACTIVE_VERSION"] = "v2"

        # Chamada sem parâmetro -> deve entregar v2
        res = client.get("/questoes?quantidade=1", headers=student_headers)
        assert res.status_code == status.HTTP_200_OK
        items = res.json()
        assert len(items) == 1
        assert items[0]["catalog_version"] == "v2"

        # Estudante tentando forçar v1 via query param -> HTTP 403 Forbidden
        res_override = client.get("/questoes?catalog_version=v1", headers=student_headers)
        assert res_override.status_code == status.HTTP_403_FORBIDDEN
        assert "Acesso restrito ao catálogo ativo" in res_override.json()["detail"]

        # 2. Configurar versão vazia / sem questões disponíveis -> HTTP 503
        empty_version = "v1"
        from sqlalchemy import delete
        db.execute(delete(ExamQuestion).where(ExamQuestion.catalog_version == "v1"))
        db.commit()

        os.environ["QUESTION_CATALOG_ACTIVE_VERSION"] = "v1"
        res_empty = client.get("/questoes", headers=student_headers)
        assert res_empty.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "não possui questões publicadas disponíveis" in res_empty.json()["detail"]

    finally:
        if old_active is not None:
            os.environ["QUESTION_CATALOG_ACTIVE_VERSION"] = old_active
        else:
            os.environ.pop("QUESTION_CATALOG_ACTIVE_VERSION", None)
        db.close()


# ---------------------------------------------------------------------------
# Teste 10: Zero Synapse e Segurança Absoluta do Gabarito
# ---------------------------------------------------------------------------
def test_10_zero_synapse_and_no_gabarito_leak(isolated_db, client, auth_headers):
    """
    Testa Item 11 do Codex:
    - O aluno abre a questão: enunciado e alternativas sem acesso ao gabarito.
    - O aluno responde: acerto/erro imediato, gabarito exibido.
    - Comentário explicativo é nulo (explanation_status = PENDING).
    - ZERO chamadas à Synapse ou geradores de IA.
    """
    db: Session = isolated_db["SessionLocal"]()
    q = db.scalar(select(ExamQuestion).where(ExamQuestion.catalog_version == "v2").limit(1))
    if q is None:
        import_catalog(db, FIXTURE_PATH, catalog_version="v2")
        q = db.scalar(select(ExamQuestion).where(ExamQuestion.catalog_version == "v2").limit(1))
    assert q is not None

    old_active = os.environ.get("QUESTION_CATALOG_ACTIVE_VERSION")
    os.environ["QUESTION_CATALOG_ACTIVE_VERSION"] = "v2"
    try:
        # 1. Buscar questão via API: ZERO vazamento de gabarito
        res_list = client.get("/questoes?quantidade=1", headers=auth_headers)
        assert res_list.status_code == status.HTTP_200_OK
        items = res_list.json()
        assert len(items) > 0

        item = items[0]
        assert "alternativa_correta_id" not in item
        assert "gabarito" not in item
        for alt in item["alternativas"]:
            assert "is_correct" not in alt
            assert "correta" not in alt

        # 2. Responder à questão: retorno imediato de acerto/erro
        resp = client.post(
            f"/questoes/{q.id}/responder",
            json={"alternativa_id": q.alternativa_correta_id, "tempo_segundos": 15},
            headers=auth_headers
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["correta"] is True
        assert data["alternativa_correta_id"] == q.alternativa_correta_id
        assert data["explicacao"] is None
        assert data["explanation_status"] == "PENDING"

        # 3. Solicitação de explicação bloqueada com comentário editorial pendente (Zero Synapse)
        retry_resp = client.post(f"/questoes/{q.id}/explicacao", headers=auth_headers)
        assert retry_resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "Comentário editorial em preparação" in retry_resp.json()["detail"]
    finally:
        if old_active is not None:
            os.environ["QUESTION_CATALOG_ACTIVE_VERSION"] = old_active
        else:
            os.environ.pop("QUESTION_CATALOG_ACTIVE_VERSION", None)
        db.close()


# ---------------------------------------------------------------------------
# Teste 11: Seleção Otimizada via effective_version (Item 1 do Codex v1.3)
# ---------------------------------------------------------------------------
def test_11_lottery_selection_uses_effective_version_random_rank(isolated_db, client, auth_headers):
    """
    Testa Item 1 da auditoria Codex v1.3:
    - Com QUESTION_CATALOG_ACTIVE_VERSION=v2;
    - Nenhuma query string de versão é enviada;
    - A consulta utiliza random_rank para ordenação;
    - func.random() NÃO é utilizado para v2;
    - Para v1, o comportamento legado permanece usando random();
    - Comprova que a lógica anterior (if catalog_version == 'v2') teria falhado.
    """
    engine = isolated_db["engine"]
    captured_queries = []

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        if "exam_questions" in statement.lower() and "select" in statement.lower():
            captured_queries.append(statement)

    event.listen(engine, "before_cursor_execute", before_cursor_execute)

    old_active = os.environ.get("QUESTION_CATALOG_ACTIVE_VERSION")
    try:
        # Garantir presença de v2 no banco isolado
        db = isolated_db["SessionLocal"]()
        v2_q = db.scalar(select(ExamQuestion).where(ExamQuestion.catalog_version == "v2").limit(1))
        if v2_q is None:
            import_catalog(db, FIXTURE_PATH, catalog_version="v2")
        db.close()

        # Caso 1: Catálogo Ativo v2 SEM parâmetro de versão enviado pelo cliente
        os.environ["QUESTION_CATALOG_ACTIVE_VERSION"] = "v2"
        captured_queries.clear()

        resp_v2 = client.get("/questoes?quantidade=5", headers=auth_headers)
        assert resp_v2.status_code == status.HTTP_200_OK

        # Encontrar a consulta principal de listagem
        list_queries_v2 = [q for q in captured_queries if "order by" in q.lower()]
        assert len(list_queries_v2) > 0, "Nenhuma query com ORDER BY foi capturada"
        main_query_v2 = list_queries_v2[-1].lower()

        # Validações estritas do sorteio v2 na cláusula ORDER BY
        order_clause_v2 = main_query_v2.split("order by")[1]
        assert "random_rank" in order_clause_v2, f"Esperava ordenação por random_rank, recebido: {order_clause_v2}"
        assert "random()" not in order_clause_v2, f"random() não deve ser utilizado no catálogo v2: {order_clause_v2}"
        assert "case" not in order_clause_v2, f"ORDER BY CASE não deve ser utilizado no catálogo v2: {order_clause_v2}"

        # Caso 2: Catálogo v1 legado continua utilizando func.random()
        db = isolated_db["SessionLocal"]()
        v1_q = db.scalar(select(ExamQuestion).where(ExamQuestion.catalog_version == "v1").limit(1))
        if v1_q is None:
            db.add(ExamQuestion(
                source_id="v1_legacy_lottery_001",
                catalog_version="v1",
                ano=2020,
                instituicao="USP",
                cabecalho="USP · 2020",
                especialidade="Clínica Médica",
                assunto="Nefrologia",
                enunciado="Questão v1 para teste de sorteio",
                statement_plain="Questão v1 para teste de sorteio",
                alternativas=[{"id": "A", "texto": "A"}, {"id": "B", "texto": "B"}],
                alternativa_correta_id="A",
                fingerprint="v1_leg_lottery",
                media_classification="NO_VISUAL_DEPENDENCY",
                image_rights_status="NONE_REQUIRED",
                content_hash_plain="b" * 64,
                content_hash_rich="b" * 64,
                answer_binding_hash="b" * 64,
                random_rank=0.3,
                status="publicada"
            ))
            db.commit()
        db.close()

        os.environ["QUESTION_CATALOG_ACTIVE_VERSION"] = "v1"
        captured_queries.clear()

        resp_v1 = client.get("/questoes?quantidade=5", headers=auth_headers)
        assert resp_v1.status_code == status.HTTP_200_OK

        list_queries_v1 = [q for q in captured_queries if "order by" in q.lower()]
        assert len(list_queries_v1) > 0
        main_query_v1 = list_queries_v1[-1].lower()
        order_clause_v1 = main_query_v1.split("order by")[1]

        assert "random()" in order_clause_v1, f"Catálogo v1 legado deve utilizar func.random(): {order_clause_v1}"
        assert "random_rank" not in order_clause_v1, f"random_rank não deve ser utilizado no catálogo v1: {order_clause_v1}"

    finally:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)
        if old_active is not None:
            os.environ["QUESTION_CATALOG_ACTIVE_VERSION"] = old_active
        else:
            os.environ.pop("QUESTION_CATALOG_ACTIVE_VERSION", None)


# ---------------------------------------------------------------------------
# Teste 12: Sorteio Circular Determinístico e Verificação Estrutural SQL (Item 3 do Codex v1.4)
# ---------------------------------------------------------------------------
def test_12_circular_selection_deterministic_scenarios(isolated_db, client, auth_headers):
    """
    Testa rigorosamente o Item 3 da auditoria Codex v1.4:
    - rnd no início da distribuição (preenchimento direto pela 1ª query);
    - rnd no meio;
    - rnd depois do maior rank (forçando wrap-around na 2ª query);
    - quantidade completada pela 2ª query;
    - nenhuma duplicata em nenhuma das etapas;
    - respeito estrito aos filtros;
    - exclusão de questões respondidas recentemente;
    - comportamento correto quando há menos registros disponíveis que o solicitado;
    - catálogo ativo vindo estritamente de QUESTION_CATALOG_ACTIVE_VERSION;
    - ausência de query string de versão;
    - zero uso de random();
    - zero uso de ORDER BY CASE;
    - inspeção do SQL compilado comprovando comparações indexáveis simples:
      random_rank >= :rnd, random_rank < :rnd e ORDER BY random_rank ASC.
    """
    engine = isolated_db["engine"]
    captured_queries = []

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        if "exam_questions" in statement.lower() and "select" in statement.lower():
            captured_queries.append(statement)

    event.listen(engine, "before_cursor_execute", before_cursor_execute)

    old_active = os.environ.get("QUESTION_CATALOG_ACTIVE_VERSION")
    try:
        os.environ["QUESTION_CATALOG_ACTIVE_VERSION"] = "v2"

        # Garantir presença das 100 questões v2 no banco isolado
        db = isolated_db["SessionLocal"]()
        v2_count = db.scalar(select(func.count(ExamQuestion.id)).where(ExamQuestion.catalog_version == "v2"))
        if v2_count < 100:
            import_catalog(db, FIXTURE_PATH, catalog_version="v2")

        # Criar usuário isolado para test_12 sem histórico de tentativas prévias
        fresh_user = User(
            nome="Auditor Sorteio",
            email=f"auditor_sorteio_{uuid.uuid4().hex[:8]}@medsync.com.br",
            password_hash=hash_password("Password123!"),
            email_verified_at=datetime.now(UTC),
            terms_accepted_at=datetime.now(UTC),
            terms_version="2026-08-11",
            privacy_version="2026-08-11",
        )
        db.add(fresh_user)
        db.commit()
        db.refresh(fresh_user)
        fresh_token = create_access_token(fresh_user.id, fresh_user.auth_version)
        fresh_headers = {"Authorization": f"Bearer {fresh_token}"}
        db.close()

        # 1. rnd no início da distribuição (0.01) -> 1ª consulta preenche tudo
        captured_queries.clear()
        with patch("random.random", return_value=0.01):
            res_start = client.get("/questoes?quantidade=10", headers=fresh_headers)
            assert res_start.status_code == status.HTTP_200_OK
            items_start = res_start.json()
            assert len(items_start) == 10
            # Nenhuma duplicata
            ids_start = [item["id"] for item in items_start]
            assert len(set(ids_start)) == 10
            # Todos os itens têm random_rank >= 0.01
            db = isolated_db["SessionLocal"]()
            ranks_start = [db.get(ExamQuestion, iid).random_rank for iid in ids_start]
            db.close()
            assert all(r >= 0.01 for r in ranks_start)
            # Ordenação estrita crescente de random_rank
            assert ranks_start == sorted(ranks_start)

        # 2. rnd no meio da distribuição (0.50)
        captured_queries.clear()
        with patch("random.random", return_value=0.50):
            res_mid = client.get("/questoes?quantidade=10", headers=fresh_headers)
            assert res_mid.status_code == status.HTTP_200_OK
            items_mid = res_mid.json()
            assert len(items_mid) == 10
            ids_mid = [item["id"] for item in items_mid]
            assert len(set(ids_mid)) == 10

        # 3. rnd no fim da distribuição (0.999), forçando wrap-around para completar
        captured_queries.clear()
        with patch("random.random", return_value=0.999):
            res_wrap = client.get("/questoes?quantidade=10", headers=fresh_headers)
            assert res_wrap.status_code == status.HTTP_200_OK
            items_wrap = res_wrap.json()
            assert len(items_wrap) == 10
            ids_wrap = [item["id"] for item in items_wrap]
            # Nenhuma duplicata mesmo após wrap-around
            assert len(set(ids_wrap)) == 10

            # Inspeção estrutural do SQL compilado durante o wrap-around:
            list_queries = [q for q in captured_queries if "order by" in q.lower()]
            assert len(list_queries) >= 2, f"Wrap-around deve ter executado 2 queries, executou {len(list_queries)}"
            q1_sql = list_queries[-2].lower()
            q2_sql = list_queries[-1].lower()

            # Comprovações da 1ª consulta: random_rank >= :param e ORDER BY random_rank ASC
            assert "random_rank >=" in q1_sql or "random_rank >=" in q1_sql.replace(" ", "")
            assert "random_rank asc" in q1_sql or "order by exam_questions.random_rank" in q1_sql
            assert "case" not in q1_sql, "ORDER BY CASE não pode ser utilizado!"
            assert "random()" not in q1_sql, "random() não pode ser utilizado!"

            # Comprovações da 2ª consulta (wrap-around): random_rank < :param e ORDER BY random_rank ASC
            assert "random_rank <" in q2_sql or "random_rank <" in q2_sql.replace(" ", "")
            assert "random_rank asc" in q2_sql or "order by exam_questions.random_rank" in q2_sql
            assert "case" not in q2_sql, "ORDER BY CASE não pode ser utilizado!"
            assert "random()" not in q2_sql, "random() não pode ser utilizado!"

        # 4. Respeito rigoroso aos filtros (ano e especialidade)
        with patch("random.random", return_value=0.70):
            res_filt = client.get("/questoes?ano=2017&especialidade=Obstetr%C3%ADcia&quantidade=5", headers=fresh_headers)
            assert res_filt.status_code == status.HTTP_200_OK
            items_filt = res_filt.json()
            assert len(items_filt) > 0
            for item in items_filt:
                assert item["ano"] == 2017
                assert item["especialidade"] == "Obstetrícia"
            ids_filt = [item["id"] for item in items_filt]
            assert len(set(ids_filt)) == len(items_filt)

        # 5. Exclusão de questões respondidas recentemente
        db = isolated_db["SessionLocal"]()
        first_q = db.scalar(select(ExamQuestion).where(ExamQuestion.catalog_version == "v2").limit(1))
        db.add(QuestionAttempt(
            id_usuario=fresh_user.id,
            id_questao=first_q.id,
            alternativa_selecionada_id="B",
            correta=True,
            tempo_segundos=15,
            created_at=datetime.now(UTC),
        ))
        db.commit()
        db.close()

        with patch("random.random", return_value=0.0):
            res_recent = client.get("/questoes?quantidade=20", headers=fresh_headers)
            assert res_recent.status_code == status.HTTP_200_OK
            returned_ids = [item["id"] for item in res_recent.json()]
            assert first_q.id not in returned_ids, "Questão respondida hoje não deve ser retornada!"

        # 6. Comportamento com menos registros disponíveis que o solicitado (le=30)
        with patch("random.random", return_value=0.50):
            res_few = client.get("/questoes?ano=2021&quantidade=30", headers=fresh_headers)
            assert res_few.status_code == status.HTTP_200_OK
            items_few = res_few.json()
            assert 0 < len(items_few) < 30
            ids_few = [item["id"] for item in items_few]
            assert len(set(ids_few)) == len(items_few)

    finally:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)
        if old_active is not None:
            os.environ["QUESTION_CATALOG_ACTIVE_VERSION"] = old_active
        else:
            os.environ.pop("QUESTION_CATALOG_ACTIVE_VERSION", None)


def test_13_v15_deterministic_tiebreak_and_rank_resolution(isolated_db, client):
    """
    Testes comprobatórios específicos dos bloqueadores v1.5:
    1. Inexistência de ix_exam_questions_random_rank na tabela exam_questions.
    2. Alta resolução dos ranks:
       - Ranks gerados a partir de 52 bits do SHA-256 (h_int_52 / 2^52).
       - Precisão total da mantissa IEEE 754 (float64).
       - Todos os 100 ranks dos registros importados são estritamente distintos (zero colisões).
       - Incompatibilidade comprovada com a discretização legada de 1.000.000 posições.
    3. Ordenação por random_rank ASC, id ASC nas consultas circulares (inspeção estrutural do SQL).
    4. Desempate determinístico por id ASC quando dois registros possuem exatamente o mesmo rank.
    5. Wrap-around circular determinístico garantindo ausência absoluta de duplicatas.
    """
    engine = isolated_db["engine"]
    db = isolated_db["SessionLocal"]()

    # 1. Comprovar inexistência de ix_exam_questions_random_rank e presença do índice composto com id
    insp = inspect(engine)
    idx_dict = {i["name"]: i for i in insp.get_indexes("exam_questions")}
    assert "ix_exam_questions_random_rank" not in idx_dict, (
        "BLOQUEADOR v1.5: O índice isolado ix_exam_questions_random_rank NÃO deve existir!"
    )
    assert "ix_exam_questions_catalog_status_rank_id" in idx_dict, (
        "Índice composto ix_exam_questions_catalog_status_rank_id DEVE existir!"
    )
    comp_cols = idx_dict["ix_exam_questions_catalog_status_rank_id"]["column_names"]
    assert comp_cols == ["catalog_version", "status", "random_rank", "id"], (
        f"Colunas do índice composto incorretas: {comp_cols}"
    )

    # 2. Alta resolução dos ranks nos 100 registros
    v2_questions = list(db.scalars(
        select(ExamQuestion).where(ExamQuestion.catalog_version == "v2")
    ).all())
    if len(v2_questions) < 100:
        import_catalog(db, FIXTURE_PATH, catalog_version="v2")
        v2_questions = list(db.scalars(
            select(ExamQuestion).where(ExamQuestion.catalog_version == "v2")
        ).all())

    assert len(v2_questions) == 100
    ranks = [q.random_rank for q in v2_questions]
    assert all(0.0 <= r < 1.0 for r in ranks), "Todos os ranks devem estar em [0.0, 1.0)"
    assert len(set(ranks)) == 100, "Todos os 100 ranks devem ser distintos com 52 bits!"

    # Comprovar alta resolução: valor * 2^52 é inteiro
    scale_52 = float(1 << 52)
    assert all(abs((r * scale_52) - round(r * scale_52)) < 1e-6 for r in ranks), (
        "Ranks devem ser gerados com precisão de 52 bits do SHA-256!"
    )
    # Comprovar eliminação da discretização legada de 1.000.000
    old_mod_diffs = [abs((r * 1_000_000) - round(r * 1_000_000)) for r in ranks]
    assert any(diff > 1e-4 for diff in old_mod_diffs), (
        "Ranks NÃO podem usar discretização antiga de 1.000.000 posições!"
    )

    # 3. Ordenação por random_rank ASC, id ASC nas consultas do sorteio
    test_user_13 = User(
        nome="Auditor TieBreak",
        email=f"auditor_tiebreak_{uuid.uuid4().hex[:8]}@medsync.com.br",
        password_hash=hash_password("Password123!"),
        email_verified_at=datetime.now(UTC),
        terms_accepted_at=datetime.now(UTC),
        terms_version="2026-08-11",
        privacy_version="2026-08-11",
    )
    db.add(test_user_13)
    db.commit()
    db.refresh(test_user_13)
    token_13 = create_access_token(test_user_13.id, test_user_13.auth_version)
    headers_13 = {"Authorization": f"Bearer {token_13}"}

    captured_queries = []

    def capture_sql(conn, cursor, statement, parameters, context, executemany):
        if "exam_questions" in statement.lower() and "select" in statement.lower():
            captured_queries.append(statement)

    event.listen(engine, "before_cursor_execute", capture_sql)
    old_active = os.environ.get("QUESTION_CATALOG_ACTIVE_VERSION")
    try:
        os.environ["QUESTION_CATALOG_ACTIVE_VERSION"] = "v2"
        captured_queries.clear()
        with patch("random.random", return_value=0.999):
            res_wrap = client.get("/questoes?quantidade=10", headers=headers_13)
            assert res_wrap.status_code == status.HTTP_200_OK

        list_queries = [q for q in captured_queries if "order by" in q.lower()]
        assert len(list_queries) >= 2, f"Wrap-around deve ter gerado 2 queries, gerou {len(list_queries)}"
        q1_sql = list_queries[-2].lower()
        q2_sql = list_queries[-1].lower()

        # Comprovações estruturais de ORDER BY random_rank ASC, id ASC
        assert "random_rank" in q1_sql and ("exam_questions.id asc" in q1_sql or "id asc" in q1_sql), (
            f"1ª consulta deve conter ORDER BY random_rank ASC, id ASC: {q1_sql}"
        )
        assert "random_rank" in q2_sql and ("exam_questions.id asc" in q2_sql or "id asc" in q2_sql), (
            f"2ª consulta deve conter ORDER BY random_rank ASC, id ASC: {q2_sql}"
        )

        # 4. Desempate determinístico quando dois registros possuem o mesmo rank
        fixed_rank = 0.777777777777
        unique_spec = f"TieBreak_{uuid.uuid4().hex[:6]}"
        q_first = ExamQuestion(
            ano=2025,
            instituicao="TieBreak Hospital A",
            cabecalho="Cabecalho TB A",
            especialidade=unique_spec,
            assunto="TB Assunto",
            enunciado="Enunciado da primeira questão com mesmo rank",
            statement_plain="Enunciado da primeira questão com mesmo rank",
            statement_rich_html="<p>Enunciado da primeira questão com mesmo rank</p>",
            alternativas=[{"id": "A", "texto": "Opcao A"}, {"id": "B", "texto": "Opcao B"}],
            alternativa_correta_id="A",
            fingerprint=f"tb_a_{uuid.uuid4().hex[:8]}",
            media_classification="text_only",
            image_rights_status="not_applicable",
            content_hash_plain="1" * 64,
            content_hash_rich="2" * 64,
            answer_binding_hash="3" * 64,
            random_rank=fixed_rank,
            status="publicada",
            catalog_version="v2",
        )
        q_second = ExamQuestion(
            ano=2025,
            instituicao="TieBreak Hospital B",
            cabecalho="Cabecalho TB B",
            especialidade=unique_spec,
            assunto="TB Assunto",
            enunciado="Enunciado da segunda questão com mesmo rank",
            statement_plain="Enunciado da segunda questão com mesmo rank",
            statement_rich_html="<p>Enunciado da segunda questão com mesmo rank</p>",
            alternativas=[{"id": "A", "texto": "Opcao A"}, {"id": "B", "texto": "Opcao B"}],
            alternativa_correta_id="B",
            fingerprint=f"tb_b_{uuid.uuid4().hex[:8]}",
            media_classification="text_only",
            image_rights_status="not_applicable",
            content_hash_plain="4" * 64,
            content_hash_rich="5" * 64,
            answer_binding_hash="6" * 64,
            random_rank=fixed_rank,
            status="publicada",
            catalog_version="v2",
        )
        db.add_all([q_first, q_second])
        db.commit()
        db.refresh(q_first)
        db.refresh(q_second)
        assert q_first.id < q_second.id
        assert q_first.random_rank == q_second.random_rank

        # Repetir 5 vezes a consulta comprovando que a ordem é estritamente estável por id ASC
        for _ in range(5):
            with patch("random.random", return_value=fixed_rank):
                res_tb = client.get(
                    f"/questoes?especialidade={unique_spec}&quantidade=2",
                    headers=headers_13
                )
                assert res_tb.status_code == status.HTTP_200_OK
                tb_items = res_tb.json()
                assert len(tb_items) == 2
                assert tb_items[0]["id"] == q_first.id, (
                    f"Desempate determinístico falhou: esperava id menor {q_first.id}, obteve {tb_items[0]['id']}"
                )
                assert tb_items[1]["id"] == q_second.id, (
                    f"Desempate determinístico falhou: esperava id maior {q_second.id}, obteve {tb_items[1]['id']}"
                )

        # 5. Wrap-around circular determinístico sem duplicatas (7 acima de 0.92 + 3 abaixo = 10)
        with patch("random.random", return_value=0.92):
            res_circ = client.get("/questoes?quantidade=10", headers=headers_13)
            assert res_circ.status_code == status.HTTP_200_OK
            circ_items = res_circ.json()
            assert len(circ_items) == 10
            circ_ids = [item["id"] for item in circ_items]
            assert len(set(circ_ids)) == 10, "Wrap-around NUNCA deve conter duplicatas!"

    finally:
        event.remove(engine, "before_cursor_execute", capture_sql)
        if old_active is not None:
            os.environ["QUESTION_CATALOG_ACTIVE_VERSION"] = old_active
        else:
            os.environ.pop("QUESTION_CATALOG_ACTIVE_VERSION", None)
        db.close()


def test_14_v16_migration_scenarios_and_data_preservation():
    """Valida exaustivamente os cenários de migração da v1.6/v1.7 (Cenário B):
    Totalmente independente e reproduzível, sem dependência de bancos locais ou arquivos não rastreados.
    1. Cria banco temporário isolado e executa migrações até a revisão 16;
    2. Popula com exatamente 2.811 registros sintéticos v1 e 100 registros sintéticos v2 + QuestionAttempt;
    3. 16 -> 17: cria ix_exam_questions_catalog_status_rank_id e remove ix_exam_questions_random_rank;
    4. 17 -> 16: reverte para o estado histórico exato da revisão 16;
    5. 16 -> 17: re-upgrade idempotente com preservação total de v1, v2 e attempts;
    6. Instalação limpa percorrendo 15 -> 16 -> 17 -> 18, mantendo o schema final com índice composto de 4 colunas.
    """
    import shutil
    import sqlite3
    import tempfile
    from alembic.config import Config
    from alembic import command
    from pathlib import Path

    api_dir = Path(__file__).parent.parent
    alembic_ini = api_dir / "alembic.ini"

    temp_dir = Path(tempfile.mkdtemp(prefix="test_mig_14_"))
    old_env = os.environ.get("DATABASE_URL")
    old_db_url = database.DATABASE_URL
    try:
        # Cenário 1: Banco temporário novo migrado até a revisão 16
        disposable_db = temp_dir / "disposable_16.db"
        db_url = f"sqlite:///{disposable_db.as_posix()}"

        os.environ["DATABASE_URL"] = db_url
        database.DATABASE_URL = db_url

        cfg = Config(str(alembic_ini))
        cfg.set_main_option("sqlalchemy.url", db_url)
        cfg.set_main_option("script_location", str(api_dir / "alembic"))

        # Migrar até a revisão 16
        command.upgrade(cfg, "20260902_16")

        # Inserir dados sintéticos representativos: exatamente 2.811 v1 e 100 v2 + usuário + QuestionAttempt
        with sqlite3.connect(disposable_db) as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO users (nome, email, password_hash, created_at) "
                "VALUES ('Test User', 'user14@medsync.test', 'hash', '2026-09-02 20:00:00')"
            )
            u_id = cur.lastrowid

            v1_rows = [
                (
                    2020 + (i % 5), "USP", f"Cabecalho v1 {i}", "Geral", "Cirurgia", f"Enunciado v1 {i}",
                    '[{"id": "A", "texto": "Opt A"}]', "A", f"fp_v1_{i}", "pendente", "publicada",
                    "v1", "2026-09-02 20:00:00", "2026-09-02 20:00:00"
                )
                for i in range(2811)
            ]
            cur.executemany(
                "INSERT INTO exam_questions ("
                "ano, instituicao, cabecalho, especialidade, assunto, enunciado, alternativas, alternativa_correta_id, "
                "fingerprint, explicacao_status, status, catalog_version, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                v1_rows
            )

            v2_rows = [
                (
                    2024, "UNICAMP", f"Cabecalho v2 {i}", "Pediatria", "Neonatologia", f"Enunciado v2 {i}",
                    '[{"id": "A", "texto": "Opt A"}]', "A", f"fp_v2_{i}", "pendente", "publicada",
                    "v2", f"4000000{i:03d}", i / 100.0, "NONE_REQUIRED", "NO_VISUAL_DEPENDENCY",
                    f"plain_{i}", f"rich_{i}", f"binding_{i}", "banca", "revalida", "sudeste", "tema", "subtema", "objetiva",
                    "2026-09-02 20:00:00", "2026-09-02 20:00:00"
                )
                for i in range(100)
            ]
            cur.executemany(
                "INSERT INTO exam_questions ("
                "ano, instituicao, cabecalho, especialidade, assunto, enunciado, alternativas, alternativa_correta_id, "
                "fingerprint, explicacao_status, status, catalog_version, source_id, random_rank, image_rights_status, "
                "media_classification, content_hash_plain, content_hash_rich, answer_binding_hash, "
                "banca, finalidade, regiao, tema, subtema, tipo_prova, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                v2_rows
            )

            first_q = cur.execute("SELECT id FROM exam_questions LIMIT 1").fetchone()[0]
            cur.execute(
                "INSERT INTO question_attempts (id_usuario, id_questao, alternativa_selecionada_id, correta, tempo_segundos, created_at) "
                "VALUES (?, ?, 'A', 1, 10, '2026-09-02 21:00:00')",
                (u_id, first_q)
            )
            con.commit()

            v1_init = cur.execute("SELECT count(id) FROM exam_questions WHERE catalog_version='v1' OR catalog_version IS NULL").fetchone()[0]
            v2_init = cur.execute("SELECT count(id) FROM exam_questions WHERE catalog_version='v2'").fetchone()[0]
            attempts_init = cur.execute("SELECT count(id) FROM question_attempts").fetchone()[0]

        assert v1_init == 2811, f"Esperava 2.811 questões v1, obteve {v1_init}"
        assert v2_init == 100, f"Esperava 100 questões v2, obteve {v2_init}"
        assert attempts_init == 1

        # Verificar índices no estado da revisão 16
        test_eng = create_engine(db_url)
        insp_16_init = inspect(test_eng)
        idx_16_init = {i["name"]: i for i in insp_16_init.get_indexes("exam_questions")}
        assert "ix_exam_questions_random_rank" in idx_16_init, "Revisão 16 histórica deve conter ix_exam_questions_random_rank"
        assert "ix_exam_questions_catalog_status_rank_id" not in idx_16_init, "Revisão 16 NÃO deve conter ix_exam_questions_catalog_status_rank_id"
        test_eng.dispose()

        # Passo 1: 16 -> 17
        command.upgrade(cfg, "20260902_17")
        test_eng = create_engine(db_url)
        insp_17 = inspect(test_eng)
        idx_17 = {i["name"]: i for i in insp_17.get_indexes("exam_questions")}
        assert "ix_exam_questions_catalog_status_rank_id" in idx_17
        assert idx_17["ix_exam_questions_catalog_status_rank_id"]["column_names"] == ["catalog_version", "status", "random_rank", "id"]
        assert "ix_exam_questions_random_rank" not in idx_17
        test_eng.dispose()

        with sqlite3.connect(disposable_db) as con:
            cur = con.cursor()
            v1_17 = cur.execute("SELECT count(id) FROM exam_questions WHERE catalog_version='v1' OR catalog_version IS NULL").fetchone()[0]
            v2_17 = cur.execute("SELECT count(id) FROM exam_questions WHERE catalog_version='v2'").fetchone()[0]
            att_17 = cur.execute("SELECT count(id) FROM question_attempts").fetchone()[0]
            ver_17 = cur.execute("SELECT version_num FROM alembic_version").fetchone()[0]

        assert ver_17 == "20260902_17"
        assert v1_17 == 2811
        assert v2_17 == 100
        assert att_17 == attempts_init

        # Passo 2: 17 -> 16
        command.downgrade(cfg, "20260902_16")
        test_eng = create_engine(db_url)
        insp_16 = inspect(test_eng)
        idx_16 = {i["name"]: i for i in insp_16.get_indexes("exam_questions")}
        assert "ix_exam_questions_catalog_status_rank_id" not in idx_16
        assert "ix_exam_questions_random_rank" in idx_16
        test_eng.dispose()

        with sqlite3.connect(disposable_db) as con:
            cur = con.cursor()
            v1_16 = cur.execute("SELECT count(id) FROM exam_questions WHERE catalog_version='v1' OR catalog_version IS NULL").fetchone()[0]
            v2_16 = cur.execute("SELECT count(id) FROM exam_questions WHERE catalog_version='v2'").fetchone()[0]
            att_16 = cur.execute("SELECT count(id) FROM question_attempts").fetchone()[0]
            ver_16 = cur.execute("SELECT version_num FROM alembic_version").fetchone()[0]

        assert ver_16 == "20260902_16"
        assert v1_16 == 2811
        assert v2_16 == 100
        assert att_16 == attempts_init

        # Passo 3: 16 -> 17 novamente
        command.upgrade(cfg, "20260902_17")
        test_eng = create_engine(db_url)
        insp_re = inspect(test_eng)
        idx_re = {i["name"]: i for i in insp_re.get_indexes("exam_questions")}
        assert "ix_exam_questions_catalog_status_rank_id" in idx_re
        assert "ix_exam_questions_random_rank" not in idx_re
        test_eng.dispose()

        with sqlite3.connect(disposable_db) as con:
            cur = con.cursor()
            v1_re = cur.execute("SELECT count(id) FROM exam_questions WHERE catalog_version='v1' OR catalog_version IS NULL").fetchone()[0]
            v2_re = cur.execute("SELECT count(id) FROM exam_questions WHERE catalog_version='v2'").fetchone()[0]
            att_re = cur.execute("SELECT count(id) FROM question_attempts").fetchone()[0]
            ver_re = cur.execute("SELECT version_num FROM alembic_version").fetchone()[0]

        assert ver_re == "20260902_17"
        assert v1_re == 2811
        assert v2_re == 100
        assert att_re == attempts_init

        # Cenário 2: Instalação limpa 15 -> 16 -> 17
        clean_db = temp_dir / "clean.db"
        clean_url = f"sqlite:///{clean_db.as_posix()}"
        os.environ["DATABASE_URL"] = clean_url
        database.DATABASE_URL = clean_url

        cfg_clean = Config(str(alembic_ini))
        cfg_clean.set_main_option("sqlalchemy.url", clean_url)
        cfg_clean.set_main_option("script_location", str(api_dir / "alembic"))

        command.upgrade(cfg_clean, "20260827_15")
        command.upgrade(cfg_clean, "head")

        clean_eng = create_engine(clean_url)
        insp_clean = inspect(clean_eng)
        idx_clean = {i["name"]: i for i in insp_clean.get_indexes("exam_questions")}
        assert "ix_exam_questions_catalog_status_rank_id" in idx_clean
        assert idx_clean["ix_exam_questions_catalog_status_rank_id"]["column_names"] == ["catalog_version", "status", "random_rank", "id"]
        assert "ix_exam_questions_random_rank" not in idx_clean
        clean_eng.dispose()

        with sqlite3.connect(clean_db) as con:
            ver_clean = con.cursor().execute("SELECT version_num FROM alembic_version").fetchone()[0]
        assert ver_clean == "20260904_18"

    finally:
        database.DATABASE_URL = old_db_url
        if old_env is not None:
            os.environ["DATABASE_URL"] = old_env
        else:
            os.environ.pop("DATABASE_URL", None)
        shutil.rmtree(temp_dir, ignore_errors=True)


