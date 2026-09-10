"""Auditoria agregada e estritamente somente leitura do catálogo de questões."""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import re
import threading
import zlib
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import text

from database import engine

logger = logging.getLogger("medsync.question_catalog_audit")

AUDIT_ENV = "QUESTION_CATALOG_AUDIT_RUN_ID"
AUDIT_MODE_ENV = "QUESTION_CATALOG_AUDIT_MODE"
_FALSE_VALUES = {"", "0", "false", "no", "off"}
_SUPPORTED_MODES = {
    "full",
    "critical_details",
    "pilot_export",
    "text_integrity",
    "quality_snapshot",
    "quality_priority",
    "quality_hold_snapshot",
    "quality_visual_audit",
    "taxonomy_inventory",
}

_TAXONOMY_INVENTORY_SQL = """
SELECT BTRIM(especialidade) AS macro_area,
       COALESCE(NULLIF(BTRIM(tema), ''), NULLIF(BTRIM(assunto), '')) AS specialty,
       NULLIF(BTRIM(subtema), '') AS source_subject,
       COUNT(*) AS questions
FROM exam_questions
WHERE catalog_version = 'v2'
  AND status = 'publicada'
  AND quality_status IN ('triada', 'validada', 'validada_com_fonte')
GROUP BY BTRIM(especialidade),
         COALESCE(NULLIF(BTRIM(tema), ''), NULLIF(BTRIM(assunto), '')),
         NULLIF(BTRIM(subtema), '')
ORDER BY macro_area, specialty, source_subject NULLS FIRST
"""

_QUALITY_PRIORITY_SQL = """
SELECT id, source_id, ano, especialidade, assunto, tema, subtema,
       status, quality_status, quality_flags, media_classification,
       image_rights_status, enunciado, statement_plain
FROM exam_questions
WHERE catalog_version = 'v2' AND id > :last_id
ORDER BY id
LIMIT 1000
"""

_ATTEMPT_COUNTS_SQL = """
SELECT id_questao AS question_id, COUNT(*) AS total
FROM question_attempts GROUP BY id_questao
"""

_OPEN_REPORT_COUNTS_SQL = """
SELECT id_questao AS question_id, COUNT(*) AS total
FROM question_reports WHERE status <> 'resolvido' GROUP BY id_questao
"""


def _load_quality_flagged_ids() -> set[int]:
    path = (
        Path(__file__).resolve().parents[1] / "data/question_quality_flagged_ids.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    ids = payload.get("ids") or []
    if (
        payload.get("complete") is not True
        or payload.get("scope") != "v2_publicada"
        or not payload.get("source_run_id")
        or not isinstance(payload.get("scanned"), int)
        or payload["scanned"] <= 0
        or len(ids) != len(set(ids))
        or any(not isinstance(question_id, int) for question_id in ids)
    ):
        raise ValueError("Unexpected text-integrity ID manifest")
    return set(ids)


def _audit_quality_priority(connection: Any, run_id: str, emit: Callable) -> None:
    """Escaneia o catálogo sem emitir enunciados ou alterar qualquer registro."""
    from services.question_quality_priority import summarize_priorities

    attempts = {
        int(row["question_id"]): int(row["total"])
        for row in connection.execute(text(_ATTEMPT_COUNTS_SQL)).mappings().all()
    }
    reports = {
        int(row["question_id"]): int(row["total"])
        for row in connection.execute(text(_OPEN_REPORT_COUNTS_SQL)).mappings().all()
    }

    def iter_rows():
        last_id = 0
        scanned = 0
        while True:
            page = (
                connection.execute(text(_QUALITY_PRIORITY_SQL), {"last_id": last_id})
                .mappings()
                .all()
            )
            if not page:
                return
            for row in page:
                yield dict(row)
            scanned += len(page)
            last_id = int(page[-1]["id"])
            if scanned % 10_000 == 0:
                emit(
                    f"QUESTION_CATALOG_AUDIT_PROGRESS run_id={run_id} "
                    f"section=quality_priority scanned={scanned} last_id={last_id}"
                )

    top_limit = max(
        50,
        min(int(os.getenv("QUESTION_QUALITY_PRIORITY_TOP_LIMIT", "500")), 2_000),
    )
    result = summarize_priorities(
        iter_rows(),
        flagged_ids=_load_quality_flagged_ids(),
        attempts_by_id=attempts,
        reports_by_id=reports,
        top_limit=top_limit,
    )
    summary = {
        key: value
        for key, value in result.items()
        if key not in {"specialties", "priority_queue"}
    }
    _emit_section(run_id, "quality_priority_summary", [summary], emit)
    _emit_section(run_id, "quality_priority_specialties", result["specialties"], emit)
    _emit_section(
        run_id,
        "quality_priority_queue",
        result["priority_queue"],
        emit,
        chunk_size=25,
    )


def _audit_text_integrity(connection: Any, run_id: str, emit: Callable) -> None:
    """Bounded keyset scan. Emits IDs/signals, never full question content."""
    from collections import Counter

    from scripts.question_quality_review import inspect_row

    counts = Counter()
    scanned = flagged = last_id = 0
    while True:
        rows = (
            connection.execute(
                text("""
            SELECT id, source_id, statement_plain, statement_rich_html,
                   alternativas, alternativa_correta_id, content_hash_plain,
                   content_hash_rich, answer_binding_hash
            FROM exam_questions
            WHERE catalog_version = 'v2' AND status = 'publicada' AND id > :last_id
            ORDER BY id LIMIT 1000
        """),
                {"last_id": last_id},
            )
            .mappings()
            .all()
        )
        if not rows:
            break
        signals = []
        for row in rows:
            issues = inspect_row(dict(row))
            scanned += 1
            if issues:
                flagged += 1
                counts.update(issues)
                signals.append({"id": row["id"], "issues": issues})
        last_id = rows[-1]["id"]
        _emit_section(run_id, "text_integrity_signals", signals, emit, chunk_size=20)
        _emit_section(
            run_id,
            "text_integrity_progress",
            [{"scanned": scanned, "flagged": flagged, "last_id": last_id}],
            emit,
        )
    _emit_section(
        run_id,
        "text_integrity_summary",
        [
            {
                "scanned": scanned,
                "flagged": flagged,
                "signals": dict(counts),
                "scope": "v2_publicada",
                "complete": True,
            }
        ],
        emit,
    )


def _audit_pilot_export(connection: Any, run_id: str, emit: Callable) -> None:
    """Exporta apenas os oito conflitos e 100 registros de cada estrato."""
    columns = """id, source_id, ano, instituicao, banca, especialidade,
        assunto, tema, subtema, statement_plain, statement_rich_html,
        alternativas, alternativa_correta_id, content_hash_plain,
        content_hash_rich, answer_binding_hash, media_classification,
        image_rights_status"""
    queries = [
        (
            "conflicts",
            f"""SELECT {columns} FROM exam_questions
        WHERE catalog_version = 'v2' AND id IN
        (487699,487760,513939,519572,487698,487705,501940,502025)
        ORDER BY id""",
        )
    ]
    for name, condition in [("unclassified", "IS NULL"), ("classified", "IS NOT NULL")]:
        queries.append(
            (
                name,
                f"""SELECT {columns} FROM exam_questions
            WHERE catalog_version = 'v2' AND status = 'publicada'
              AND especialidade = 'Clínica Médica' AND tema = 'Hematologia'
              AND NULLIF(BTRIM(subtema), '') {condition}
            ORDER BY MD5(id::text || 'medsync-hema-pilot-v1'), id LIMIT 100""",
            )
        )
    counts = {}
    for cohort, sql in queries:
        rows = connection.execute(text(sql)).mappings().all()
        counts[cohort] = len(rows)
        for row in rows:
            payload = json.dumps(dict(row), ensure_ascii=True, sort_keys=True)
            digest = hashlib.sha256(payload.encode()).hexdigest()
            parts = [payload[i : i + 1500] for i in range(0, len(payload), 1500)]
            for index, part in enumerate(parts):
                emit(
                    "QUESTION_PILOT_EXPORT "
                    + json.dumps(
                        {
                            "run_id": run_id,
                            "cohort": cohort,
                            "id": row["id"],
                            "part": index,
                            "parts": len(parts),
                            "sha256": digest,
                            "payload": part,
                        },
                        separators=(",", ":"),
                    )
                )
    _emit_section(run_id, "pilot_export_counts", [counts], emit)


def _audit_quality_hold_snapshot(connection: Any, run_id: str, emit: Callable) -> None:
    """Exporta somente as questões v2 ainda bloqueadas para revisão editorial."""
    rows = (
        connection.execute(
            text("""
            SELECT id, source_id, ano, instituicao, banca, especialidade,
                   assunto, tema, subtema, status, quality_status, quality_flags,
                   quality_method, quality_source_reference, statement_plain,
                   statement_rich_html, alternativas, alternativa_correta_id,
                   content_hash_plain, content_hash_rich, answer_binding_hash,
                   media_classification, image_rights_status, updated_at
            FROM exam_questions
            WHERE catalog_version = 'v2'
              AND quality_status = 'revisao_necessaria'
            ORDER BY id
            LIMIT 100
            """)
        )
        .mappings()
        .all()
    )
    for row in rows:
        payload = json.dumps(
            dict(row),
            ensure_ascii=False,
            sort_keys=True,
            default=str,
            separators=(",", ":"),
        ).encode()
        encoded = base64.b64encode(zlib.compress(payload)).decode()
        chunks = [
            encoded[index : index + 1500] for index in range(0, len(encoded), 1500)
        ]
        digest = hashlib.sha256(payload).hexdigest()
        for index, chunk in enumerate(chunks):
            emit(
                "QUESTION_QUALITY_HOLD_SNAPSHOT "
                + json.dumps(
                    {
                        "run_id": run_id,
                        "id": row["id"],
                        "part": index,
                        "parts": len(chunks),
                        "sha256": digest,
                        "encoding": "zlib-base64",
                        "payload": chunk,
                    },
                    separators=(",", ":"),
                )
            )
    emit(
        "QUESTION_QUALITY_HOLD_SNAPSHOT_DONE "
        + json.dumps(
            {"run_id": run_id, "exported": len(rows), "bounded_limit": 100},
            separators=(",", ":"),
        )
    )


def _audit_quality_visual(connection: Any, run_id: str, emit: Callable) -> None:
    """Audita marcação visual do primeiro lote P0 sem emitir o conteúdo."""
    from services.question_visual_audit import audit_batch, load_batch_manifest

    path = (
        Path(__file__).resolve().parents[1] / "data/question_quality_p0_batch_001.json"
    )
    result = audit_batch(connection, load_batch_manifest(path))
    _emit_section(run_id, "quality_visual_summary", [result["summary"]], emit)
    _emit_section(
        run_id,
        "quality_visual_details",
        result["details"],
        emit,
        chunk_size=25,
    )


def _audit_taxonomy_inventory(connection: Any, run_id: str, emit: Callable) -> None:
    """Exporta somente combinações taxonômicas agregadas, nunca questões."""
    rows = connection.execute(text(_TAXONOMY_INVENTORY_SQL)).mappings().all()
    payload = json.dumps(
        [
            {key: _json_value(value) for key, value in row.items()}
            for row in rows
        ],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode()
    encoded = base64.b64encode(zlib.compress(payload, level=9)).decode()
    chunks = [encoded[index : index + 2500] for index in range(0, len(encoded), 2500)]
    digest = hashlib.sha256(payload).hexdigest()
    for index, chunk in enumerate(chunks, start=1):
        emit(
            "QUESTION_TAXONOMY_INVENTORY "
            + json.dumps(
                {
                    "run_id": run_id,
                    "chunk": index,
                    "chunks": len(chunks),
                    "sha256": digest,
                    "encoding": "zlib-base64",
                    "payload": chunk,
                },
                separators=(",", ":"),
            )
        )
    emit(
        "QUESTION_TAXONOMY_INVENTORY_DONE "
        + json.dumps(
            {
                "run_id": run_id,
                "combinations": len(rows),
                "chunks": len(chunks),
                "sha256": digest,
            },
            separators=(",", ":"),
        )
    )
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
        SELECT COALESCE(NULLIF(BTRIM(subtema), ''), 'Geral') AS subject,
               COUNT(*) AS questions,
               COUNT(*) FILTER (WHERE tema IS NULL OR BTRIM(tema) = '') AS missing_theme,
               COUNT(*) FILTER (WHERE subtema IS NULL OR BTRIM(subtema) = '') AS missing_subtheme
        FROM exam_questions
        WHERE catalog_version = 'v2' AND status = 'publicada'
          AND LOWER(BTRIM(especialidade)) = 'clínica médica'
          AND LOWER(BTRIM(tema)) = 'hematologia'
        GROUP BY COALESCE(NULLIF(BTRIM(subtema), ''), 'Geral')
        ORDER BY questions DESC, subject
        """,
    ),
)

_ANSWER_INTEGRITY_BATCH_SQL = """
SELECT
  COUNT(*) FILTER (WHERE json_typeof(alternativas) IS DISTINCT FROM 'array') AS alternatives_not_array,
  COUNT(*) FILTER (
    WHERE json_typeof(alternativas) = 'array'
      AND json_array_length(alternativas) < 2
  ) AS fewer_than_two_options,
  COUNT(*) FILTER (
    WHERE json_typeof(alternativas) = 'array'
      AND NOT EXISTS (
        SELECT 1 FROM json_array_elements(alternativas) option
        WHERE option->>'id' = exam_questions.alternativa_correta_id
      )
  ) AS correct_option_not_found,
  COUNT(*) FILTER (
    WHERE json_typeof(alternativas) = 'array'
      AND EXISTS (
        SELECT 1 FROM json_array_elements(alternativas) option
        WHERE BTRIM(COALESCE(option->>'id', '')) = ''
           OR COALESCE(
             NULLIF(BTRIM(option->>'texto'), ''),
             NULLIF(BTRIM(option->>'body_plain'), ''),
             NULLIF(BTRIM(option->>'body'), ''),
             NULLIF(BTRIM(option->>'html'), ''),
             NULLIF(BTRIM(option->>'body_rich_html'), ''),
             ''
           ) = ''
      )
  ) AS blank_option_fields
FROM exam_questions
WHERE catalog_version = 'v2' AND status = 'publicada'
  AND id BETWEEN :start_id AND :end_id
"""

_CONFLICTING_DUPLICATES_SQL = """
WITH conflict_hashes AS (
  SELECT content_hash_plain, COUNT(*) AS group_size,
         COUNT(DISTINCT answer_binding_hash) AS answer_versions
  FROM exam_questions
  WHERE catalog_version = 'v2' AND status = 'publicada'
    AND content_hash_plain IS NOT NULL
  GROUP BY content_hash_plain
  HAVING COUNT(*) > 1 AND COUNT(DISTINCT answer_binding_hash) > 1
)
SELECT conflicts.content_hash_plain, conflicts.group_size,
       conflicts.answer_versions, questions.id, questions.source_id,
       questions.ano AS year, questions.instituicao AS institution,
       questions.banca AS examining_board,
       questions.alternativa_correta_id AS correct_option_id,
       questions.answer_binding_hash
FROM conflict_hashes conflicts
JOIN exam_questions questions
  ON questions.content_hash_plain = conflicts.content_hash_plain
WHERE questions.catalog_version = 'v2' AND questions.status = 'publicada'
ORDER BY conflicts.content_hash_plain, questions.id
"""

_BLANK_OPTION_DETAILS_BATCH_SQL = """
SELECT questions.id, questions.source_id, questions.ano AS year,
       questions.instituicao AS institution,
       questions.especialidade AS specialty, questions.assunto AS subject,
       questions.tema AS theme, questions.subtema AS subtheme,
       questions.alternativa_correta_id AS correct_option_id,
       ARRAY_AGG(options.position ORDER BY options.position) FILTER (
         WHERE BTRIM(COALESCE(options.value->>'id', '')) = ''
       ) AS blank_id_positions,
       ARRAY_AGG(options.position ORDER BY options.position) FILTER (
         WHERE COALESCE(
           NULLIF(BTRIM(options.value->>'texto'), ''),
           NULLIF(BTRIM(options.value->>'body_plain'), ''),
           NULLIF(BTRIM(options.value->>'body'), ''),
           NULLIF(BTRIM(options.value->>'html'), ''),
           NULLIF(BTRIM(options.value->>'body_rich_html'), ''),
           ''
         ) = ''
       ) AS blank_text_positions,
       BOOL_OR(
         options.value->>'id' = questions.alternativa_correta_id
         AND COALESCE(
           NULLIF(BTRIM(options.value->>'texto'), ''),
           NULLIF(BTRIM(options.value->>'body_plain'), ''),
           NULLIF(BTRIM(options.value->>'body'), ''),
           NULLIF(BTRIM(options.value->>'html'), ''),
           NULLIF(BTRIM(options.value->>'body_rich_html'), ''),
           ''
         ) = ''
       ) AS correct_option_blank
FROM exam_questions questions
CROSS JOIN LATERAL json_array_elements(questions.alternativas)
  WITH ORDINALITY AS options(value, position)
WHERE questions.catalog_version = 'v2' AND questions.status = 'publicada'
  AND questions.id BETWEEN :start_id AND :end_id
GROUP BY questions.id
HAVING BOOL_OR(
  BTRIM(COALESCE(options.value->>'id', '')) = ''
  OR COALESCE(
    NULLIF(BTRIM(options.value->>'texto'), ''),
    NULLIF(BTRIM(options.value->>'body_plain'), ''),
    NULLIF(BTRIM(options.value->>'body'), ''),
    NULLIF(BTRIM(options.value->>'html'), ''),
    NULLIF(BTRIM(options.value->>'body_rich_html'), ''),
    ''
  ) = ''
)
ORDER BY questions.id
"""


def _json_value(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    return value


def _emit_line(message: str) -> None:
    print(message, flush=True)


def _emit_section(
    run_id: str,
    section: str,
    rows: list[dict[str, Any]],
    emit: Callable[[str], None],
    *,
    chunk_size: int = 50,
) -> None:
    chunks = [
        rows[index : index + chunk_size] for index in range(0, len(rows), chunk_size)
    ]
    if not chunks:
        chunks = [[]]
    for index, chunk in enumerate(chunks, start=1):
        emit(
            "QUESTION_CATALOG_AUDIT_SECTION "
            + json.dumps(
                {
                    "run_id": run_id,
                    "section": section,
                    "chunk": index,
                    "chunks": len(chunks),
                    "rows": chunk,
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )


def _catalog_id_bounds(connection: Any) -> tuple[int | None, int | None]:
    bounds = (
        connection.execute(
            text(
                """
            SELECT MIN(id) AS min_id, MAX(id) AS max_id
            FROM exam_questions
            WHERE catalog_version = 'v2' AND status = 'publicada'
            """
            )
        )
        .mappings()
        .one()
    )
    return bounds["min_id"], bounds["max_id"]


def _batch_size() -> int:
    return max(
        1_000,
        min(int(os.getenv("QUESTION_CATALOG_AUDIT_BATCH_SIZE", "10000")), 25_000),
    )


def _audit_answer_integrity(connection: Any, run_id: str, emit: Callable) -> None:
    min_id, max_id = _catalog_id_bounds(connection)
    totals = {
        "alternatives_not_array": 0,
        "fewer_than_two_options": 0,
        "correct_option_not_found": 0,
        "blank_option_fields": 0,
    }
    if min_id is not None and max_id is not None:
        batch_size = _batch_size()
        batch_number = 0
        for start_id in range(int(min_id), int(max_id) + 1, batch_size):
            batch_number += 1
            row = (
                connection.execute(
                    text(_ANSWER_INTEGRITY_BATCH_SQL),
                    {"start_id": start_id, "end_id": start_id + batch_size - 1},
                )
                .mappings()
                .one()
            )
            for key in totals:
                totals[key] += int(row[key] or 0)
            if batch_number % 5 == 0:
                emit(
                    f"QUESTION_CATALOG_AUDIT_PROGRESS run_id={run_id} "
                    f"section=answer_integrity batches={batch_number}"
                )

    _emit_section(run_id, "answer_integrity", [totals], emit)


def _audit_critical_details(connection: Any, run_id: str, emit: Callable) -> None:
    conflict_rows = (
        connection.execute(text(_CONFLICTING_DUPLICATES_SQL)).mappings().all()
    )
    conflicts = [
        {key: _json_value(value) for key, value in row.items()} for row in conflict_rows
    ]
    _emit_section(
        run_id, "conflicting_duplicate_details", conflicts, emit, chunk_size=20
    )

    min_id, max_id = _catalog_id_bounds(connection)
    blank_questions: list[dict[str, Any]] = []
    if min_id is not None and max_id is not None:
        batch_size = _batch_size()
        batch_number = 0
        for start_id in range(int(min_id), int(max_id) + 1, batch_size):
            batch_number += 1
            rows = (
                connection.execute(
                    text(_BLANK_OPTION_DETAILS_BATCH_SQL),
                    {"start_id": start_id, "end_id": start_id + batch_size - 1},
                )
                .mappings()
                .all()
            )
            blank_questions.extend(
                {key: _json_value(value) for key, value in row.items()} for row in rows
            )
            if batch_number % 5 == 0:
                emit(
                    f"QUESTION_CATALOG_AUDIT_PROGRESS run_id={run_id} "
                    f"section=blank_option_details batches={batch_number}"
                )

    summary = {
        "questions_with_blank_options": len(blank_questions),
        "questions_with_blank_ids": sum(
            bool(row["blank_id_positions"]) for row in blank_questions
        ),
        "questions_with_blank_text": sum(
            bool(row["blank_text_positions"]) for row in blank_questions
        ),
        "questions_with_blank_correct_option": sum(
            bool(row["correct_option_blank"]) for row in blank_questions
        ),
    }
    _emit_section(run_id, "blank_option_summary", [summary], emit)
    _emit_section(
        run_id,
        "blank_option_details",
        blank_questions,
        emit,
        chunk_size=25,
    )


def run_question_catalog_audit(
    run_id: str,
    *,
    mode: str = "full",
    connect: Callable[[], Any] = engine.connect,
    emit: Callable[[str], None] = _emit_line,
) -> None:
    """Executa SELECTs agregados em uma transação marcada como somente leitura."""
    if mode not in _SUPPORTED_MODES:
        emit(f"QUESTION_CATALOG_AUDIT_REFUSED run_id={run_id} unsupported_mode={mode}")
        return
    emit(f"QUESTION_CATALOG_AUDIT_START run_id={run_id} mode={mode}")
    try:
        with connect() as connection:
            transaction = connection.begin()
            try:
                if connection.dialect.name == "postgresql":
                    if mode in {
                        "text_integrity",
                        "quality_snapshot",
                        "quality_priority",
                        "quality_hold_snapshot",
                        "quality_visual_audit",
                        "taxonomy_inventory",
                    }:
                        connection.execute(
                            text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
                        )
                    connection.execute(text("SET TRANSACTION READ ONLY"))
                    connection.execute(text("SET LOCAL statement_timeout = '180s'"))
                if mode == "quality_priority":
                    _audit_quality_priority(connection, run_id, emit)
                elif mode == "taxonomy_inventory":
                    _audit_taxonomy_inventory(connection, run_id, emit)
                elif mode == "quality_visual_audit":
                    _audit_quality_visual(connection, run_id, emit)
                elif mode == "quality_hold_snapshot":
                    _audit_quality_hold_snapshot(connection, run_id, emit)
                elif mode == "quality_snapshot":
                    from scripts.export_question_quality_snapshot import export_snapshot

                    export_snapshot(connection, run_id, emit)
                elif mode == "text_integrity":
                    _audit_text_integrity(connection, run_id, emit)
                elif mode == "pilot_export":
                    _audit_pilot_export(connection, run_id, emit)
                elif mode == "critical_details":
                    _audit_critical_details(connection, run_id, emit)
                else:
                    for section, sql in _QUERIES:
                        rows = connection.execute(text(sql)).mappings().all()
                        payload = [
                            {key: _json_value(value) for key, value in row.items()}
                            for row in rows
                        ]
                        _emit_section(run_id, section, payload, emit)
                    _audit_answer_integrity(connection, run_id, emit)
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

    mode = os.getenv(AUDIT_MODE_ENV, "full").strip().lower()
    safe_id = re.sub(r"[^a-zA-Z0-9_.-]", "_", f"{run_id}-{mode}")[:80]
    digest = hashlib.sha256(f"{run_id}:{mode}".encode()).hexdigest()[:12]
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
        kwargs={"mode": mode},
        name=f"question-catalog-audit-{digest}",
        daemon=True,
    ).start()
    return True
