"""Executor de inicialização explicitamente habilitado para o funil de qualidade."""

import json
import os
from pathlib import Path


def run_requested_quality_funnel() -> None:
    mode = os.getenv("QUESTION_QUALITY_FUNNEL_MODE", "")
    if mode not in {"dry-run", "apply"}:
        return

    from database import engine
    from models import ExamQuestion
    from scripts.apply_question_quality_funnel import execute

    path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "question_quality_funnel_manifest.json"
    )
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if os.getenv("QUESTION_QUALITY_FUNNEL_PLAN_SHA256") != manifest["plan_sha256"]:
        raise ValueError("Quality funnel plan acknowledgement missing")

    result = execute(
        engine,
        ExamQuestion.__table__,
        manifest,
        apply=mode == "apply",
    )
    if mode == "apply":
        from routers.questions import invalidate_catalog_metadata_cache

        invalidate_catalog_metadata_cache("v2")
    print(
        "QUESTION_QUALITY_FUNNEL_DONE "
        + json.dumps(
            {"mode": mode, "plan_sha256": manifest["plan_sha256"], **result},
            sort_keys=True,
        ),
        flush=True,
    )
