"""Executor desabilitado por padrão da quarentena visual P0."""

import json
import os
from pathlib import Path


def run_requested_visual_quarantine() -> None:
    mode = os.getenv("QUESTION_QUALITY_VISUAL_QUARANTINE_MODE", "")
    if mode not in {"dry-run", "apply"}:
        return

    from database import engine
    from models import ExamQuestion
    from scripts.apply_question_quality_visual_quarantine import execute

    root = Path(__file__).resolve().parents[1]
    manifest = json.loads(
        (root / "data/question_quality_visual_quarantine_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    if (
        os.getenv("QUESTION_QUALITY_VISUAL_QUARANTINE_PLAN_SHA256")
        != manifest["plan_sha256"]
    ):
        raise ValueError("Visual quarantine plan acknowledgement missing")
    result = execute(engine, ExamQuestion.__table__, manifest, apply=mode == "apply")
    if mode == "apply":
        from routers.questions import invalidate_catalog_metadata_cache

        invalidate_catalog_metadata_cache("v2")
    print(
        "QUESTION_QUALITY_VISUAL_QUARANTINE_DONE "
        + json.dumps(
            {"mode": mode, "plan_sha256": manifest["plan_sha256"], **result},
            sort_keys=True,
        ),
        flush=True,
    )
