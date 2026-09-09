"""Coloca em quarentena questões P0 dependentes de imagem sem marcação visual."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select, text, update

WRITE_COLUMNS = {
    "status",
    "quality_status",
    "quality_flags",
    "quality_method",
    "quality_source_reference",
    "quality_reviewed_at",
}
EXPECTED_COUNT = 8


def manifest_digest(items: list[dict[str, Any]]) -> str:
    raw = json.dumps(
        items, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def validate_manifest(manifest: dict[str, Any]) -> None:
    items = manifest.get("items") or []
    if (
        manifest.get("schema_version") != 1
        or manifest.get("catalog_version") != "v2"
        or manifest_digest(items) != manifest.get("plan_sha256")
        or len(items) != EXPECTED_COUNT
        or len({item.get("id") for item in items}) != EXPECTED_COUNT
    ):
        raise ValueError("Invalid visual quarantine manifest")
    for item in items:
        if (
            not item.get("source_id")
            or item.get("decision") != "quarantine_missing_visual"
            or set(item.get("expected") or {})
            != {
                "ano",
                "especialidade",
                "assunto",
                "status",
                "quality_status",
                "quality_flags",
                "quality_method",
                "quality_source_reference",
                "quality_reviewed_at",
                "media_classification",
                "image_rights_status",
                "content_hash_plain",
                "content_hash_rich",
                "answer_binding_hash",
            }
        ):
            raise ValueError(f"Invalid visual quarantine item {item.get('id')}")


def expected_state(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item["id"],
        "source_id": item["source_id"],
        "catalog_version": "v2",
        **item["expected"],
    }


def target_state(
    item: dict[str, Any], reviewed_at: str, source_run_id: str
) -> dict[str, Any]:
    state = expected_state(item)
    state.update(
        {
            "status": "revisao",
            "quality_status": "revisao_necessaria",
            "quality_flags": ["visual_source_required"],
            "quality_method": "visual_asset_audit_v1",
            "quality_source_reference": source_run_id,
            "quality_reviewed_at": reviewed_at,
        }
    )
    return state


def _normalized(value: Any) -> Any:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat()
    return value


def _matches(row: dict[str, Any], state: dict[str, Any]) -> bool:
    return all(_normalized(row.get(key)) == value for key, value in state.items())


def execute(
    engine,
    table,
    manifest: dict[str, Any],
    *,
    apply: bool = False,
    reverse: bool = False,
) -> dict[str, Any]:
    """Valida e trava todas as linhas antes de alterar metadados de qualidade."""
    validate_manifest(manifest)
    items = manifest["items"]
    by_id = {item["id"]: item for item in items}
    ids = sorted(by_id)
    guard_columns = (
        {"id", "source_id", "catalog_version"}
        | set(items[0]["expected"])
        | WRITE_COLUMNS
    )
    columns = [table.c[name] for name in sorted(guard_columns)]

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
                raise ValueError("Missing visual quarantine records")

            operations = []
            stale = []
            for question_id in ids:
                item = by_id[question_id]
                before = expected_state(item)
                after = target_state(
                    item, manifest["created_at"], manifest["source_run_id"]
                )
                source, destination = (after, before) if reverse else (before, after)
                if _matches(rows[question_id], destination):
                    continue
                if not _matches(rows[question_id], source):
                    stale.append(question_id)
                    continue
                changes = {
                    key: destination[key]
                    for key in WRITE_COLUMNS
                    if source.get(key) != destination.get(key)
                }
                if changes.get("quality_reviewed_at"):
                    changes["quality_reviewed_at"] = datetime.fromisoformat(
                        changes["quality_reviewed_at"]
                    )
                operations.append((question_id, changes, destination))

            if stale:
                raise ValueError(f"Stale visual quarantine states: {stale}")
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
            return {
                "requested": len(ids),
                "changed": len(operations),
                "already_at_target": len(ids) - len(operations),
                "quarantined": len(ids),
                "committed": apply,
                "reverse": reverse,
            }
        except BaseException:
            if transaction.is_active:
                transaction.rollback()
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--reverse", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if args.sha256 != manifest.get("plan_sha256"):
        raise ValueError("Plan acknowledgement mismatch")

    from database import engine
    from models import ExamQuestion

    print(
        json.dumps(
            execute(
                engine,
                ExamQuestion.__table__,
                manifest,
                apply=args.apply,
                reverse=args.reverse,
            ),
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
