"""Aplica a realocação taxonômica revisada sem alterar conteúdo ou gabarito."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select, text, update

from scripts.apply_question_quality_funnel import (
    manifest_digest as base_manifest_digest,
)
from scripts.apply_question_quality_funnel import target_state as base_target_state

TAXONOMY_COLUMNS = {"especialidade", "assunto", "tema", "subtema"}
QUALITY_COLUMNS = {
    "status",
    "quality_status",
    "quality_flags",
    "quality_method",
    "quality_source_reference",
    "quality_reviewed_at",
}
WRITE_COLUMNS = TAXONOMY_COLUMNS | QUALITY_COLUMNS
GUARD_COLUMNS = {
    "id",
    "source_id",
    "catalog_version",
    "content_hash_plain",
    "content_hash_rich",
    "answer_binding_hash",
} | WRITE_COLUMNS
RELOCATION_FLAG = "taxonomy_relocation_pending"
NON_BLOCKING_FLAGS = {"taxonomy_reviewed_v1"}


def manifest_digest(items: list[dict[str, Any]]) -> str:
    raw = json.dumps(
        items, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def normalized(value: Any) -> Any:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat()
    return value


def matches(row: dict[str, Any], expected: dict[str, Any]) -> bool:
    return all(normalized(row.get(key)) == value for key, value in expected.items())


def validate_manifests(resolution: dict, base: dict) -> dict[int, dict]:
    items = resolution.get("items") or []
    if (
        resolution.get("schema_version") != 1
        or resolution.get("catalog_version") != "v2"
        or manifest_digest(items) != resolution.get("plan_sha256")
    ):
        raise ValueError("Invalid taxonomy resolution manifest")
    if len(items) != 19 or len({item.get("id") for item in items}) != 19:
        raise ValueError("Unexpected taxonomy resolution item count")
    if base_manifest_digest(base.get("items") or []) != base.get("plan_sha256"):
        raise ValueError("Base quality funnel checksum mismatch")
    if resolution.get("base_plan_sha256") != base.get("plan_sha256"):
        raise ValueError("Unexpected base quality funnel plan")

    base_by_id = {item["id"]: item for item in base["items"]}
    for item in items:
        question_id = item.get("id")
        taxonomy = item.get("taxonomy") or {}
        base_item = base_by_id.get(question_id)
        if (
            set(taxonomy) != TAXONOMY_COLUMNS
            or not all(
                isinstance(value, str) and value.strip() for value in taxonomy.values()
            )
            or not base_item
            or base_item.get("decision") != "propor_realocacao"
            or RELOCATION_FLAG not in base_item.get("set", {}).get("quality_flags", [])
        ):
            raise ValueError(f"Invalid taxonomy resolution for ID {question_id}")
    return base_by_id


def expected_state(item: dict, base_by_id: dict[int, dict]) -> dict[str, Any]:
    return base_target_state(base_by_id[item["id"]])


def target_state(
    item: dict,
    base_by_id: dict[int, dict],
    reviewed_at: str,
) -> dict[str, Any]:
    state = expected_state(item, base_by_id)
    flags = [flag for flag in state["quality_flags"] if flag != RELOCATION_FLAG]
    remains_blocked = any(flag not in NON_BLOCKING_FLAGS for flag in flags)
    state.update(item["taxonomy"])
    state.update(
        {
            "status": "revisao" if remains_blocked else "publicada",
            "quality_status": "revisao_necessaria" if remains_blocked else "triada",
            "quality_flags": flags,
            "quality_method": "taxonomy_resolution_v2",
            "quality_reviewed_at": reviewed_at,
        }
    )
    return state


def execute(
    engine,
    table,
    resolution: dict,
    base: dict,
    *,
    apply: bool = False,
    reverse: bool = False,
) -> dict[str, Any]:
    """Valida e bloqueia todas as linhas antes da primeira escrita."""
    base_by_id = validate_manifests(resolution, base)
    reviewed_at = resolution["created_at"]
    items = resolution["items"]
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
                raise ValueError("Missing taxonomy resolution records")

            operations = []
            stale = []
            for question_id in ids:
                item = by_id[question_id]
                before = expected_state(item, base_by_id)
                after = target_state(item, base_by_id, reviewed_at)
                source, destination = (after, before) if reverse else (before, after)
                if matches(rows[question_id], destination):
                    continue
                if not matches(rows[question_id], source):
                    differences = {
                        key: {
                            "expected": normalized(source.get(key)),
                            "current": normalized(rows[question_id].get(key)),
                        }
                        for key in source
                        if normalized(rows[question_id].get(key)) != source.get(key)
                    }
                    stale.append({"id": question_id, "differences": differences})
                    continue
                changes = {
                    key: destination[key]
                    for key in WRITE_COLUMNS
                    if source.get(key) != destination.get(key)
                }
                changes["quality_reviewed_at"] = datetime.fromisoformat(
                    destination["quality_reviewed_at"]
                )
                operations.append((question_id, changes, destination))

            if stale:
                raise ValueError(
                    "Stale or unexpected taxonomy states: "
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
                if not matches(actual, destination):
                    raise ValueError(
                        f"Post-write verification failed for ID {question_id}"
                    )

            if apply:
                transaction.commit()
            else:
                transaction.rollback()

            released = sum(
                target_state(item, base_by_id, reviewed_at)["status"] == "publicada"
                for item in items
            )
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
