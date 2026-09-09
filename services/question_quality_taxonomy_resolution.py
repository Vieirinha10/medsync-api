"""Executor desabilitado por padrão para a realocação taxonômica revisada."""

import json
import os
from pathlib import Path


def run_requested_taxonomy_resolution() -> None:
    mode = os.getenv("QUESTION_QUALITY_TAXONOMY_RESOLUTION_MODE", "")
    if mode not in {"dry-run", "apply"}:
        return

    from database import engine
    from models import ExamQuestion
    from scripts.apply_question_quality_taxonomy_resolution import execute

    root = Path(__file__).resolve().parents[1]
    resolution = json.loads(
        (
            root / "data" / "question_quality_taxonomy_resolution_manifest.json"
        ).read_text(encoding="utf-8")
    )
    base = json.loads(
        (root / "data" / "question_quality_funnel_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    acknowledged = os.getenv("QUESTION_QUALITY_TAXONOMY_RESOLUTION_PLAN_SHA256")
    if acknowledged != resolution["plan_sha256"]:
        raise ValueError("Taxonomy resolution plan acknowledgement missing")

    result = execute(
        engine,
        ExamQuestion.__table__,
        resolution,
        base,
        apply=mode == "apply",
    )
    if mode == "apply":
        from routers.questions import invalidate_catalog_metadata_cache

        invalidate_catalog_metadata_cache("v2")
    print(
        "QUESTION_QUALITY_TAXONOMY_RESOLUTION_DONE "
        + json.dumps(
            {"mode": mode, "plan_sha256": resolution["plan_sha256"], **result},
            sort_keys=True,
        ),
        flush=True,
    )
