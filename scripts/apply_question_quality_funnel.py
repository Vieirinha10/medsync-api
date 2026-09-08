"""Aplica o funil editorial revisado com travas, atomicidade e dry-run padrão."""

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select, text, update

GUARD_COLUMNS = {
    "id",
    "source_id",
    "catalog_version",
    "status",
    "especialidade",
    "assunto",
    "tema",
    "subtema",
    "content_hash_plain",
    "content_hash_rich",
    "answer_binding_hash",
    "quality_status",
    "quality_flags",
    "quality_method",
    "quality_source_reference",
    "quality_reviewed_at",
}
WRITE_COLUMNS = {
    "status",
    "subtema",
    "quality_status",
    "quality_flags",
    "quality_method",
    "quality_source_reference",
    "quality_reviewed_at",
}
INITIAL_QUALITY = {
    "quality_status": "triada",
    "quality_flags": [],
    "quality_method": "structural_catalog_audit_v1",
    "quality_source_reference": None,
    "quality_reviewed_at": None,
}


def manifest_digest(items: list[dict]) -> str:
    raw = json.dumps(
        items, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def normalized(value):
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.astimezone(UTC).isoformat()
    return value


def matches(row: dict, expected: dict) -> bool:
    return all(normalized(row.get(key)) == value for key, value in expected.items())


def expected_state(item: dict) -> dict:
    return {
        "id": item["id"],
        "source_id": item["source_id"],
        "catalog_version": "v2",
        "status": "publicada",
        **item["expected_taxonomy"],
        **item["expected_hashes"],
        **INITIAL_QUALITY,
    }


def target_state(item: dict) -> dict:
    state = expected_state(item)
    state.update(item["set"])
    return state


def validate_manifest(manifest: dict) -> None:
    items = manifest.get("items") or []
    if manifest.get("schema_version") != 1 or manifest.get("catalog_version") != "v2":
        raise ValueError("Unsupported quality funnel manifest")
    if manifest_digest(items) != manifest.get("plan_sha256"):
        raise ValueError("Quality funnel manifest checksum mismatch")
    if len(items) != 209 or len({item["id"] for item in items}) != len(items):
        raise ValueError("Unexpected item count or duplicate IDs")
    for item in items:
        if not item.get("source_id") or set(item["set"]) - WRITE_COLUMNS:
            raise ValueError(f"Invalid writes for ID {item.get('id')}")
        if item["set"].get("status", "publicada") not in {"publicada", "revisao"}:
            raise ValueError(f"Invalid publication status for ID {item['id']}")
        if item["set"]["quality_status"] not in {
            "triada",
            "revisao_necessaria",
            "anulada",
        }:
            raise ValueError(f"Invalid quality status for ID {item['id']}")
        if "alternativa_correta_id" in item["set"] or "alternativas" in item["set"]:
            raise ValueError(f"Answer mutation forbidden for ID {item['id']}")


def execute(
    engine, table, manifest: dict, *, apply: bool = False, reverse: bool = False
):
    """Bloqueia e valida todas as linhas antes de realizar qualquer alteração."""
    validate_manifest(manifest)
    items = manifest["items"]
    by_id = {item["id"]: item for item in items}
    ids = sorted(by_id)
    columns = [table.c[name] for name in sorted(GUARD_COLUMNS)]

    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            if connection.dialect.name == "postgresql":
                connection.execute(text("SET LOCAL lock_timeout = '5s'"))
                connection.execute(text("SET LOCAL statement_timeout = '180s'"))
            rows = {}
            for offset in range(0, len(ids), 100):
                statement = (
                    select(*columns)
                    .where(table.c.id.in_(ids[offset : offset + 100]))
                    .order_by(table.c.id)
                    .with_for_update()
                )
                rows.update(
                    {
                        row["id"]: dict(row)
                        for row in connection.execute(statement).mappings()
                    }
                )
            if set(rows) != set(ids):
                raise ValueError("Missing records; no changes applied")

            operations = []
            for question_id in ids:
                item = by_id[question_id]
                expected = expected_state(item)
                target = target_state(item)
                source, destination = (
                    (target, expected) if reverse else (expected, target)
                )
                if matches(rows[question_id], destination):
                    continue
                if not matches(rows[question_id], source):
                    raise ValueError(f"Stale or unexpected state for ID {question_id}")
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
            return {
                "requested": len(ids),
                "changed": len(operations),
                "already_at_target": len(ids) - len(operations),
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
