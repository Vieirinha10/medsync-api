"""Aplica decisões clínicas conservadoras às questões em quarentena."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select, text, update

from scripts.apply_question_quality_funnel import (
    GUARD_COLUMNS,
)
from scripts.apply_question_quality_funnel import (
    manifest_digest as base_manifest_digest,
)
from scripts.apply_question_quality_funnel import target_state as base_target_state
from scripts.apply_question_quality_taxonomy_resolution import (
    manifest_digest as taxonomy_manifest_digest,
)
from scripts.apply_question_quality_taxonomy_resolution import (
    target_state as taxonomy_target_state,
)
from scripts.apply_question_quality_taxonomy_resolution import validate_manifests

WRITE_COLUMNS = {
    "status",
    "quality_status",
    "quality_flags",
    "quality_method",
    "quality_source_reference",
    "quality_reviewed_at",
}
VALID_DECISIONS = {"release_validated", "keep_quarantined"}
EXPECTED_ITEM_COUNT = 33
EXPECTED_RELEASE_COUNT = 6


def manifest_digest(items: list[dict[str, Any]]) -> str:
    raw = json.dumps(
        items, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def validate_manifest(clinical: dict, base: dict, taxonomy: dict) -> dict[int, dict]:
    items = clinical.get("items") or []
    if (
        clinical.get("schema_version") != 1
        or clinical.get("catalog_version") != "v2"
        or manifest_digest(items) != clinical.get("plan_sha256")
    ):
        raise ValueError("Invalid clinical review manifest")
    if len(items) != EXPECTED_ITEM_COUNT or len(
        {item.get("id") for item in items}
    ) != len(items):
        raise ValueError("Unexpected clinical review item count")
    if base_manifest_digest(base.get("items") or []) != base.get("plan_sha256"):
        raise ValueError("Base quality funnel checksum mismatch")
    if taxonomy_manifest_digest(taxonomy.get("items") or []) != taxonomy.get(
        "plan_sha256"
    ):
        raise ValueError("Taxonomy resolution checksum mismatch")
    if clinical.get("base_plan_sha256") != base.get("plan_sha256"):
        raise ValueError("Unexpected base quality funnel plan")
    if clinical.get("taxonomy_plan_sha256") != taxonomy.get("plan_sha256"):
        raise ValueError("Unexpected taxonomy resolution plan")

    base_by_id = {item["id"]: item for item in base["items"]}
    validate_manifests(taxonomy, base)
    release_count = 0
    for item in items:
        question_id = item.get("id")
        if (
            question_id not in base_by_id
            or item.get("decision") not in VALID_DECISIONS
            or not isinstance(item.get("rationale"), str)
            or not item["rationale"].strip()
            or not isinstance(item.get("sources"), list)
            or not all(
                isinstance(source, str) and source.startswith("https://")
                for source in item["sources"]
            )
        ):
            raise ValueError(f"Invalid clinical decision for ID {question_id}")
        if item["decision"] == "release_validated":
            release_count += 1
            if not item["sources"]:
                raise ValueError(f"Validated release lacks source for ID {question_id}")
    if release_count != EXPECTED_RELEASE_COUNT:
        raise ValueError("Unexpected clinical release count")
    return base_by_id


def expected_state(
    item: dict, base_by_id: dict[int, dict], taxonomy: dict, base: dict
) -> dict[str, Any]:
    taxonomy_by_id = {entry["id"]: entry for entry in taxonomy["items"]}
    if item["id"] in taxonomy_by_id:
        return taxonomy_target_state(
            taxonomy_by_id[item["id"]],
            validate_manifests(taxonomy, base),
            taxonomy["created_at"],
        )
    return base_target_state(base_by_id[item["id"]])


def target_state(
    item: dict, expected: dict[str, Any], reviewed_at: str
) -> dict[str, Any]:
    state = dict(expected)
    if item["decision"] == "release_validated":
        state.update(
            {
                "status": "publicada",
                "quality_status": "validada_com_fonte",
                "quality_flags": ["clinical_reviewed_v1"],
                "quality_method": "clinical_review_v1",
                "quality_source_reference": " | ".join(item["sources"]),
                "quality_reviewed_at": reviewed_at,
            }
        )
    return state


def execute(
    engine,
    table,
    clinical: dict,
    base: dict,
    taxonomy: dict,
    *,
    apply: bool = False,
    reverse: bool = False,
) -> dict[str, Any]:
    """Trava e valida as 33 linhas antes da primeira escrita."""
    base_by_id = validate_manifest(clinical, base, taxonomy)
    items = clinical["items"]
    by_id = {item["id"]: item for item in items}
    ids = sorted(by_id)
    columns = [table.c[name] for name in sorted(GUARD_COLUMNS)]

    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            if connection.dialect.name == "postgresql":
                connection.execute(text("SET LOCAL lock_timeout = '5s'"))
                connection.execute(text("SET LOCAL statement_timeout = '180s'"))
            rows = {
                row["id"]: dict(row)
                for row in connection.execute(
                    select(*columns)
                    .where(table.c.id.in_(ids))
                    .order_by(table.c.id)
                    .with_for_update()
                ).mappings()
            }
            if set(rows) != set(ids):
                raise ValueError("Missing clinical review records")

            operations = []
            stale = []
            for question_id in ids:
                item = by_id[question_id]
                before = expected_state(item, base_by_id, taxonomy, base)
                after = target_state(item, before, clinical["created_at"])
                source, destination = (after, before) if reverse else (before, after)
                if _matches(rows[question_id], destination):
                    continue
                if not _matches(rows[question_id], source):
                    stale.append(
                        {
                            "id": question_id,
                            "differences": {
                                key: {
                                    "expected": _normalized(source.get(key)),
                                    "current": _normalized(rows[question_id].get(key)),
                                }
                                for key in source
                                if _normalized(rows[question_id].get(key))
                                != source.get(key)
                            },
                        }
                    )
                    continue
                changes = {
                    key: destination[key]
                    for key in WRITE_COLUMNS
                    if source.get(key) != destination.get(key)
                }
                if changes:
                    if changes.get("quality_reviewed_at"):
                        changes["quality_reviewed_at"] = datetime.fromisoformat(
                            changes["quality_reviewed_at"]
                        )
                    operations.append((question_id, changes, destination))

            if stale:
                raise ValueError(
                    "Stale or unexpected clinical states: "
                    + json.dumps(stale, ensure_ascii=False, sort_keys=True)
                )

            for question_id, changes, _ in operations:
                result = connection.execute(
                    update(table).where(table.c.id == question_id).values(**changes)
                )
                if result.rowcount != 1:
                    raise ValueError(
                        f"Unexpected updated row count for ID {question_id}"
                    )
            for question_id, _, destination in operations:
                actual = dict(
                    connection.execute(
                        select(*columns).where(table.c.id == question_id)
                    )
                    .mappings()
                    .one()
                )
                if not _matches(actual, destination):
                    raise ValueError(
                        f"Post-write verification failed for ID {question_id}"
                    )

            if apply:
                transaction.commit()
            else:
                transaction.rollback()

            released = sum(item["decision"] == "release_validated" for item in items)
            return {
                "requested": len(ids),
                "changed": len(operations),
                "already_at_target": len(ids) - len(operations),
                "released": released,
                "remaining_in_review": len(ids) - released,
                "committed": apply,
                "reverse": reverse,
            }
        except BaseException:
            if transaction.is_active:
                transaction.rollback()
            raise


def _normalized(value: Any) -> Any:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat()
    return value


def _matches(row: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(_normalized(row.get(key)) == value for key, value in expected.items())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--reverse", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    clinical = json.loads(args.manifest.read_text(encoding="utf-8"))
    if args.sha256 != clinical.get("plan_sha256"):
        raise ValueError("Plan acknowledgement mismatch")
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

    from database import engine
    from models import ExamQuestion

    print(
        json.dumps(
            execute(
                engine,
                ExamQuestion.__table__,
                clinical,
                base,
                taxonomy,
                apply=args.apply,
                reverse=args.reverse,
            ),
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
