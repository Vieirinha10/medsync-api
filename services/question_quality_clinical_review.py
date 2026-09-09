"""Executor de inicialização, desabilitado por padrão, da revisão clínica."""

import json
import os
from pathlib import Path


def run_requested_clinical_review() -> None:
    mode = os.getenv("QUESTION_QUALITY_CLINICAL_REVIEW_MODE", "")
    if mode not in {"dry-run", "apply"}:
        return

    from database import engine
    from models import ExamQuestion
    from scripts.apply_question_quality_clinical_review import execute

    root = Path(__file__).resolve().parents[1]
    clinical = json.loads(
        (root / "data/question_quality_clinical_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    base = json.loads(
        (root / "data/question_quality_funnel_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    taxonomy = json.loads(
        (root / "data/question_quality_taxonomy_resolution_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    acknowledged = os.getenv("QUESTION_QUALITY_CLINICAL_REVIEW_PLAN_SHA256")
    if acknowledged != clinical["plan_sha256"]:
        raise ValueError("Clinical review plan acknowledgement missing")

    result = execute(
        engine,
        ExamQuestion.__table__,
        clinical,
        base,
        taxonomy,
        apply=mode == "apply",
    )
    if mode == "apply":
        from routers.questions import invalidate_catalog_metadata_cache

        invalidate_catalog_metadata_cache("v2")
    print(
        "QUESTION_QUALITY_CLINICAL_REVIEW_DONE "
        + json.dumps(
            {"mode": mode, "plan_sha256": clinical["plan_sha256"], **result},
            sort_keys=True,
        ),
        flush=True,
    )
