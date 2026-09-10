"""Gera o relatório consolidado e somente leitura da taxonomia em sombra."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from typing import Any

from sqlalchemy import select

from database import SessionLocal
from models import ContentTaxonomyClassification, TaxonomyClassificationRun
from services.content_taxonomy_classifier import normalized_text

GENERIC_LABELS = frozenset(
    {
        "geral",
        "outros",
        "outros conteudos",
        "conteudos gerais",
        "miscelanea",
        "revisao e temas diversos",
    }
)


def build_report(taxonomy_version: str, *, minimum_subject_size: int) -> dict[str, Any]:
    with SessionLocal() as db:
        rows = list(
            db.scalars(
                select(ContentTaxonomyClassification).where(
                    ContentTaxonomyClassification.taxonomy_version
                    == taxonomy_version
                )
            ).all()
        )
        runs = list(
            db.scalars(
                select(TaxonomyClassificationRun).where(
                    TaxonomyClassificationRun.taxonomy_version == taxonomy_version
                )
            ).all()
        )

    statuses = Counter(row.status for row in rows)
    content_types = Counter(row.content_type for row in rows)
    specialties = Counter(row.specialty_code for row in rows)
    themes = Counter(row.theme_code for row in rows)
    subjects = Counter(row.subject_code for row in rows)
    subject_formats: dict[str, set[str]] = defaultdict(set)
    labels_by_code: dict[str, set[str]] = defaultdict(set)
    repeated_levels: list[dict[str, str]] = []
    generic_items: list[dict[str, str]] = []

    for row in rows:
        subject_formats[row.subject_code].add(row.content_type)
        labels_by_code[row.specialty_code].add(row.specialty_label)
        labels_by_code[row.theme_code].add(row.theme_label)
        labels_by_code[row.subject_code].add(row.subject_label)
        if len(
            {
                normalized_text(row.specialty_label),
                normalized_text(row.theme_label),
                normalized_text(row.subject_label),
            }
        ) != 3:
            repeated_levels.append(
                {"content_type": row.content_type, "content_id": row.content_id}
            )
        if normalized_text(row.subject_label) in GENERIC_LABELS:
            generic_items.append(
                {"content_type": row.content_type, "content_id": row.content_id}
            )

    small_subjects = [
        {"subject_code": code, "items": count}
        for code, count in sorted(subjects.items(), key=lambda item: (item[1], item[0]))
        if count < minimum_subject_size
    ]
    label_collisions = [
        {"code": code, "labels": sorted(labels)}
        for code, labels in labels_by_code.items()
        if len(labels) > 1
    ]
    linked_subjects = sum(len(formats) > 1 for formats in subject_formats.values())
    verified = statuses.get("verificada", 0)

    return {
        "taxonomy_version": taxonomy_version,
        "totals": {
            "classifications": len(rows),
            "specialties": len(specialties),
            "themes": len(themes),
            "subjects": len(subjects),
            "verified": verified,
            "review_required": statuses.get("revisao_necessaria", 0),
            "automatic_verification_rate": round(verified / len(rows), 4)
            if rows
            else 0,
        },
        "by_status": dict(sorted(statuses.items())),
        "by_content_type": dict(sorted(content_types.items())),
        "quality_gates": {
            "repeated_hierarchy_levels": len(repeated_levels),
            "generic_subject_items": len(generic_items),
            "label_collisions": len(label_collisions),
            "subjects_below_minimum_size": len(small_subjects),
            "subjects_linking_multiple_formats": linked_subjects,
        },
        "details": {
            "repeated_hierarchy_levels": repeated_levels[:100],
            "generic_subject_items": generic_items[:100],
            "label_collisions": label_collisions[:100],
            "small_subjects": small_subjects[:500],
        },
        "runs": [
            {
                "run_id": run.id,
                "content_type": run.content_type,
                "status": run.status,
                "processed": run.processed_count,
                "verified": run.verified_count,
                "review_required": run.review_count,
                "failed": run.failed_count,
                "cursor": run.cursor_after_id,
            }
            for run in runs
        ],
        "database_mutations": 0,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--taxonomy-version", default="semantic-v1")
    parser.add_argument("--minimum-subject-size", type=int, default=10)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(
        json.dumps(
            build_report(
                args.taxonomy_version,
                minimum_subject_size=args.minimum_subject_size,
            ),
            ensure_ascii=False,
            indent=2,
        )
    )
