"""Priorização determinística do catálogo; não equivale a revisão clínica."""

from __future__ import annotations

import heapq
import re
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from typing import Any

CURRENT_CATALOG_START_YEAR = 2020
CLASSIC_REVIEW_START_YEAR = 2016

FLAG_WEIGHTS = {
    "conflicting_answer_key": 90,
    "truncated_statement": 90,
    "official_source_required": 70,
    "visual_source_required": 60,
    "editorial_review_pending": 55,
    "taxonomy_classification_pending": 50,
    "taxonomy_relocation_pending": 45,
}

DOCUMENTED_IMAGE_RIGHTS = {
    "VERIFIED",
    "LICENSED",
    "OWNED",
    "EDITORIAL_EXAM_FAIR_USE",
}

_TIME_SENSITIVE_PATTERN = re.compile(
    r"\b(?:diretriz|guideline|protocolo|recomenda(?:ção|ções)|calendário|"
    r"notificação compulsória|legislação|lei|portaria|dose|tratamento|"
    r"rastreamento|profilaxia)\b",
    re.IGNORECASE,
)


def year_bucket(year: int | None) -> str:
    if year is None:
        return "sem_ano"
    if year >= CURRENT_CATALOG_START_YEAR:
        return "atual_2020_2026"
    if year >= CLASSIC_REVIEW_START_YEAR:
        return "classica_2016_2019"
    return "arquivo_pre_2016"


def prioritize_question(
    row: Mapping[str, Any],
    *,
    text_integrity_flagged: bool = False,
    attempts: int = 0,
    open_reports: int = 0,
) -> dict[str, Any]:
    """Classifica risco operacional sem inferir mérito médico ou gabarito."""
    question_id = int(row["id"])
    year = row.get("ano")
    year = int(year) if year is not None else None
    status = str(row.get("status") or "")
    quality_status = str(row.get("quality_status") or "importada")
    flags = sorted({str(value) for value in (row.get("quality_flags") or [])})
    bucket = year_bucket(year)

    if quality_status == "anulada":
        return {
            "id": question_id,
            "source_id": row.get("source_id"),
            "ano": year,
            "especialidade": row.get("especialidade"),
            "assunto": row.get("assunto"),
            "score": 0,
            "tier": "excluida",
            "action": "manter_exclusao",
            "reasons": ["officially_annulled"],
            "attempts": attempts,
            "open_reports": open_reports,
            "year_bucket": bucket,
        }

    score = 0
    reasons: list[str] = []
    held = status != "publicada" or quality_status in {
        "importada",
        "revisao_necessaria",
    }
    if held:
        score += 80
        reasons.append("publication_or_quality_hold")

    for flag in flags:
        weight = FLAG_WEIGHTS.get(flag)
        if weight:
            score += weight
            reasons.append(flag)

    if text_integrity_flagged:
        score += 60
        reasons.append("text_integrity_signal")

    media = str(row.get("media_classification") or "")
    rights = str(row.get("image_rights_status") or "")
    if media == "REQUIRES_IMAGE" and rights not in DOCUMENTED_IMAGE_RIGHTS:
        score += 60
        reasons.append("image_rights_review")

    if bucket == "classica_2016_2019":
        score += 35
        reasons.append("classic_requires_technical_review")
    elif bucket == "arquivo_pre_2016":
        score += 55
        reasons.append("pre_2016_archive_candidate")
    elif bucket == "sem_ano":
        score += 70
        reasons.append("missing_year")

    text_value = " ".join(
        str(row.get(field) or "")
        for field in ("enunciado", "statement_plain", "assunto", "tema", "subtema")
    )
    if _TIME_SENSITIVE_PATTERN.search(text_value):
        score += 25
        reasons.append("time_sensitive_content")

    if open_reports:
        score += min(100, 70 + (open_reports - 1) * 10)
        reasons.append("open_student_report")
    if attempts >= 100:
        score += 20
        reasons.append("high_student_exposure")
    elif attempts >= 20:
        score += 10
        reasons.append("moderate_student_exposure")

    if held:
        action = "resolver_quarentena"
    elif open_reports or text_integrity_flagged:
        action = "revisar_integridade"
    elif "image_rights_review" in reasons:
        action = "revisar_documentacao_visual"
    elif bucket == "arquivo_pre_2016":
        action = "avaliar_arquivamento"
    elif bucket == "classica_2016_2019":
        action = "revisar_classica"
    elif "time_sensitive_content" in reasons:
        action = "revisar_atualidade_cientifica"
    else:
        action = "manter_catalogo_atual"

    if score >= 80:
        tier = "p0_critica"
    elif score >= 55:
        tier = "p1_alta"
    elif score >= 30:
        tier = "p2_media"
    else:
        tier = "p3_rotina"

    return {
        "id": question_id,
        "source_id": row.get("source_id"),
        "ano": year,
        "especialidade": row.get("especialidade"),
        "assunto": row.get("assunto"),
        "score": score,
        "tier": tier,
        "action": action,
        "reasons": reasons or ["structural_baseline_only"],
        "attempts": attempts,
        "open_reports": open_reports,
        "year_bucket": bucket,
    }


def summarize_priorities(
    rows: Iterable[Mapping[str, Any]],
    *,
    flagged_ids: set[int] | None = None,
    attempts_by_id: Mapping[int, int] | None = None,
    reports_by_id: Mapping[int, int] | None = None,
    top_limit: int = 500,
) -> dict[str, Any]:
    """Agrega o catálogo inteiro e retém uma fila limitada e reproduzível."""
    flagged_ids = flagged_ids or set()
    attempts_by_id = attempts_by_id or {}
    reports_by_id = reports_by_id or {}
    tier_counts: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    year_counts: Counter[str] = Counter()
    specialty_counts: dict[str, Counter[str]] = defaultdict(Counter)
    top: list[tuple[int, int, int, dict[str, Any]]] = []
    scanned = 0

    for row in rows:
        question_id = int(row["id"])
        item = prioritize_question(
            row,
            text_integrity_flagged=question_id in flagged_ids,
            attempts=int(attempts_by_id.get(question_id, 0)),
            open_reports=int(reports_by_id.get(question_id, 0)),
        )
        scanned += 1
        tier_counts[item["tier"]] += 1
        action_counts[item["action"]] += 1
        year_counts[item["year_bucket"]] += 1
        reason_counts.update(item["reasons"])
        specialty = str(item["especialidade"] or "Sem especialidade")
        specialty_counts[specialty][item["tier"]] += 1

        if item["tier"] in {"p0_critica", "p1_alta", "p2_media"} and top_limit:
            key = (item["score"], item["ano"] or -1, -item["id"])
            entry = (*key, item)
            if len(top) < top_limit:
                heapq.heappush(top, entry)
            elif key > top[0][:3]:
                heapq.heapreplace(top, entry)

    priority_queue = [entry[3] for entry in sorted(top, reverse=True)]
    specialties = [
        {"especialidade": specialty, "total": sum(counts.values()), **dict(counts)}
        for specialty, counts in sorted(
            specialty_counts.items(),
            key=lambda pair: (-pair[1]["p0_critica"], -pair[1]["p1_alta"], pair[0]),
        )
    ]
    return {
        "schema_version": 1,
        "policy": {
            "current_catalog": "2020-2026",
            "classic_review": "2016-2019",
            "archive_candidate": "before_2016",
            "scientific_validation_inferred": False,
            "database_mutations": 0,
        },
        "scanned": scanned,
        "tiers": dict(tier_counts),
        "actions": dict(action_counts),
        "year_buckets": dict(year_counts),
        "reasons": dict(reason_counts),
        "specialties": specialties,
        "priority_queue": priority_queue,
    }
