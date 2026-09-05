"""Auditoria agregada e estritamente somente leitura do catálogo de questões."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any

from sqlalchemy import text

from database import engine

logger = logging.getLogger("medsync.question_catalog_audit")

AUDIT_ENV = "QUESTION_CATALOG_AUDIT_RUN_ID"
_FALSE_VALUES = {"", "0", "false", "no", "off"}

_QUERIES: tuple[tuple[str, str], ...] = (
    (
        "inventory",
        """
        SELECT catalog_version, status, COUNT(*) AS questions,
               MIN(ano) AS min_year, MAX(ano) AS max_year
        FROM exam_questions
        GROUP BY catalog_version, status
        ORDER BY catalog_version, status
        """,
    ),
    (
        "year_distribution",
        """
        SELECT ano AS year, COUNT(*) AS questions
        FROM exam_questions
        WHERE catalog_version = 'v2' AND status = 'publicada'
        GROUP BY ano
        ORDER BY ano DESC
        """,
    ),
    (
        "required_fields",
        """
        SELECT COUNT(*) AS total,
               COUNT(*) FILTER (WHERE source_id IS NULL OR BTRIM(source_id) = '') AS missing_source_id,
               COUNT(*) FILTER (WHERE ano IS NULL) AS missing_year,
               COUNT(*) FILTER (WHERE instituicao IS NULL OR BTRIM(instituicao) = '') AS missing_institution,
               COUNT(*) FILTER (WHERE especialidade IS NULL OR BTRIM(especialidade) = '') AS missing_specialty,
               COUNT(*) FILTER (WHERE assunto IS NULL OR BTRIM(assunto) = '') AS missing_subject,
               COUNT(*) FILTER (WHERE statement_plain IS NULL OR BTRIM(statement_plain) = '') AS missing_statement,
               COUNT(*) FILTER (WHERE alternativa_correta_id IS NULL OR BTRIM(alternativa_correta_id) = '') AS missing_correct_option,
               COUNT(*) FILTER (WHERE content_hash_plain IS NULL OR BTRIM(content_hash_plain) = '') AS missing_content_hash,
               COUNT(*) FILTER (WHERE answer_binding_hash IS NULL OR BTRIM(answer_binding_hash) = '') AS missing_answer_hash
        FROM exam_questions
        WHERE catalog_version = 'v2' AND status = 'publicada'
        """,
    ),
    (
        "answer_integrity",
        """
        SELECT
          COUNT(*) FILTER (WHERE jsonb_typeof(alternativas::jsonb) <> 'array') AS alternatives_not_array,
          COUNT(*) FILTER (
            WHERE jsonb_typeof(alternativas::jsonb) = 'array'
              AND jsonb_array_length(alternativas::jsonb) < 2
          ) AS fewer_than_two_options,
          COUNT(*) FILTER (
            WHERE jsonb_typeof(alternativas::jsonb) = 'array'
              AND NOT EXISTS (
                SELECT 1 FROM jsonb_array_elements(alternativas::jsonb) option
                WHERE option->>'id' = exam_questions.alternativa_correta_id
              )
          ) AS correct_option_not_found,
          COUNT(*) FILTER (
            WHERE jsonb_typeof(alternativas::jsonb) = 'array'
              AND EXISTS (
                SELECT 1 FROM jsonb_array_elements(alternativas::jsonb) option
                WHERE BTRIM(COALESCE(option->>'id', '')) = ''
                   OR BTRIM(COALESCE(option->>'texto', '')) = ''
              )
          ) AS blank_option_fields
        FROM exam_questions
        WHERE catalog_version = 'v2' AND status = 'publicada'
        """,
    ),
    (
        "duplicate_integrity",
        """
        SELECT
          COUNT(*) AS duplicated_hash_groups,
          COALESCE(SUM(group_size - 1), 0) AS excess_questions,
          COUNT(*) FILTER (WHERE answer_versions > 1) AS conflicting_answer_groups
        FROM (
          SELECT content_hash_plain, COUNT(*) AS group_size,
                 COUNT(DISTINCT answer_binding_hash) AS answer_versions
          FROM exam_questions
          WHERE catalog_version = 'v2' AND status = 'publicada'
            AND content_hash_plain IS NOT NULL
          GROUP BY content_hash_plain
          HAVING COUNT(*) > 1
        ) duplicates
        """,
    ),
    (
        "taxonomy_summary",
        """
        SELECT COUNT(DISTINCT BTRIM(especialidade)) AS specialties,
               COUNT(DISTINCT BTRIM(assunto)) AS subjects,
               COUNT(*) FILTER (WHERE LOWER(BTRIM(especialidade)) = LOWER(BTRIM(assunto))) AS same_specialty_and_subject
        FROM exam_questions
        WHERE catalog_version = 'v2' AND status = 'publicada'
        """,
    ),
    (
        "taxonomy_name_collisions",
        """
        SELECT subject_name AS name, COUNT(*) AS questions_using_name_as_subject
        FROM (
          SELECT BTRIM(assunto) AS subject_name
          FROM exam_questions
          WHERE catalog_version = 'v2' AND status = 'publicada'
        ) subjects
        WHERE LOWER(subject_name) IN (
          SELECT DISTINCT LOWER(BTRIM(especialidade))
          FROM exam_questions
          WHERE catalog_version = 'v2' AND status = 'publicada'
        )
        GROUP BY subject_name
        ORDER BY questions_using_name_as_subject DESC, subject_name
        """,
    ),
    (
        "specialty_distribution",
        """
        SELECT BTRIM(especialidade) AS specialty, COUNT(*) AS questions,
               COUNT(DISTINCT BTRIM(assunto)) AS subjects
        FROM exam_questions
        WHERE catalog_version = 'v2' AND status = 'publicada'
        GROUP BY BTRIM(especialidade)
        ORDER BY questions DESC, specialty
        """,
    ),
    (
        "hematology_subjects",
        """
        SELECT BTRIM(assunto) AS subject, COUNT(*) AS questions,
               COUNT(*) FILTER (WHERE tema IS NULL OR BTRIM(tema) = '') AS missing_theme,
               COUNT(*) FILTER (WHERE subtema IS NULL OR BTRIM(subtema) = '') AS missing_subtheme
        FROM exam_questions
        WHERE catalog_version = 'v2' AND status = 'publicada'
          AND LOWER(BTRIM(especialidade)) = 'hematologia'
        GROUP BY BTRIM(assunto)
        ORDER BY questions DESC, subject
        """,
    ),
)


def _json_value(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _emit_line(message: str) -> None:
    print(message, flush=True)


def run_question_catalog_audit(
    run_id: str,
    *,
    connect: Callable[[], Any] = engine.connect,
    emit: Callable[[str], None] = _emit_line,
) -> None:
    """Executa SELECTs agregados em uma transação marcada como somente leitura."""
    emit(f"QUESTION_CATALOG_AUDIT_START run_id={run_id}")
    try:
        with connect() as connection:
            transaction = connection.begin()
            try:
                if connection.dialect.name == "postgresql":
                    connection.execute(text("SET TRANSACTION READ ONLY"))
                    connection.execute(text("SET LOCAL statement_timeout = '180s'"))
                for section, sql in _QUERIES:
                    rows = connection.execute(text(sql)).mappings().all()
                    payload = [
                        {key: _json_value(value) for key, value in row.items()}
                        for row in rows
                    ]
                    emit(
                        "QUESTION_CATALOG_AUDIT_SECTION "
                        + json.dumps(
                            {"run_id": run_id, "section": section, "rows": payload},
                            ensure_ascii=False,
                            separators=(",", ":"),
                        )
                    )
            finally:
                transaction.rollback()
        emit(f"QUESTION_CATALOG_AUDIT_DONE run_id={run_id}")
    except Exception:
        logger.exception("QUESTION_CATALOG_AUDIT_FAILED run_id=%s", run_id)


def start_requested_audit() -> bool:
    """Inicia a auditoria uma vez por instância quando o gatilho está ativo."""
    run_id = os.getenv(AUDIT_ENV, "").strip()
    if run_id.lower() in _FALSE_VALUES:
        return False

    safe_id = re.sub(r"[^a-zA-Z0-9_.-]", "_", run_id)[:80]
    digest = hashlib.sha256(run_id.encode("utf-8")).hexdigest()[:12]
    lock_path = Path(f"/tmp/medsync-question-audit-{safe_id}-{digest}.lock")
    try:
        descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return False
    else:
        os.close(descriptor)

    threading.Thread(
        target=run_question_catalog_audit,
        args=(run_id,),
        name=f"question-catalog-audit-{digest}",
        daemon=True,
    ).start()
    return True
