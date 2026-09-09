"""Auditoria determinística de marcação e documentação visual de um lote."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from sqlalchemy import bindparam, text


class _ImageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sources: list[str | None] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "img":
            self.sources.append(dict(attrs).get("src"))


def manifest_digest(items: list[dict[str, Any]]) -> str:
    raw = json.dumps(
        items, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(raw).hexdigest()


def load_batch_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    items = manifest.get("items") or []
    if (
        manifest.get("schema_version") != 1
        or manifest.get("catalog_version") != "v2"
        or manifest.get("scope") != "first_1000_priority_queue_items"
        or len(items) != 1_000
        or len({item.get("id") for item in items}) != 1_000
        or manifest_digest(items) != manifest.get("plan_sha256")
    ):
        raise ValueError("Invalid P0 visual audit manifest")
    if any(
        not isinstance(item.get("id"), int)
        or not item.get("source_id")
        or not isinstance(item.get("score"), int)
        for item in items
    ):
        raise ValueError("Invalid P0 visual audit item")
    return manifest


def inspect_markup(html: str | None) -> dict[str, Any]:
    parser = _ImageParser()
    parser.feed(html or "")
    source_kinds: Counter[str] = Counter()
    hosts: set[str] = set()
    for raw_source in parser.sources:
        source = (raw_source or "").strip()
        if not source:
            source_kinds["missing_src"] += 1
        elif source.startswith("data:"):
            source_kinds["data_uri"] += 1
        else:
            parsed = urlparse(source)
            if parsed.scheme in {"http", "https"}:
                source_kinds[f"{parsed.scheme}_url"] += 1
                if parsed.hostname:
                    hosts.add(parsed.hostname.lower())
            else:
                source_kinds["relative_url"] += 1
    return {
        "image_tags": len(parser.sources),
        "source_kinds": dict(sorted(source_kinds.items())),
        "source_hosts": sorted(hosts),
    }


_BATCH_SQL = text("""
SELECT id, source_id, ano, especialidade, assunto, status, quality_status,
       media_classification, image_rights_status, statement_rich_html,
       content_hash_plain, content_hash_rich, answer_binding_hash
FROM exam_questions
WHERE catalog_version = 'v2' AND id IN :ids
ORDER BY id
""").bindparams(bindparam("ids", expanding=True))


def audit_batch(connection: Any, manifest: dict[str, Any]) -> dict[str, Any]:
    expected = {item["id"]: item for item in manifest["items"]}
    rows = connection.execute(_BATCH_SQL, {"ids": sorted(expected)}).mappings().all()
    if len(rows) != len(expected) or {row["id"] for row in rows} != set(expected):
        raise ValueError("Missing P0 visual audit records")

    details = []
    signal_counts: Counter[str] = Counter()
    rights_counts: Counter[str] = Counter()
    host_counts: Counter[str] = Counter()
    for row in rows:
        if str(row["source_id"]) != str(expected[row["id"]]["source_id"]):
            raise ValueError(f"Unexpected source ID for question {row['id']}")
        markup = inspect_markup(row["statement_rich_html"])
        signals = []
        if row["media_classification"] == "REQUIRES_IMAGE" and not markup["image_tags"]:
            signals.append("missing_image_markup")
        if markup["source_kinds"].get("missing_src"):
            signals.append("image_tag_missing_src")
        if markup["source_kinds"].get("http_url"):
            signals.append("non_tls_image_url")
        if markup["source_kinds"].get("data_uri"):
            signals.append("inline_image_data")
        if markup["source_kinds"].get("relative_url"):
            signals.append("relative_image_url")
        if row["media_classification"] == "REQUIRES_IMAGE" and row[
            "image_rights_status"
        ] not in {"VERIFIED", "LICENSED", "OWNED", "EDITORIAL_EXAM_FAIR_USE"}:
            signals.append("rights_documentation_pending")

        signal_counts.update(signals or ["markup_and_rights_ready"])
        rights_counts[str(row["image_rights_status"] or "EMPTY")] += 1
        host_counts.update(markup["source_hosts"])
        details.append(
            {
                "id": row["id"],
                "source_id": row["source_id"],
                "ano": row["ano"],
                "especialidade": row["especialidade"],
                "assunto": row["assunto"],
                "status": row["status"],
                "quality_status": row["quality_status"],
                "media_classification": row["media_classification"],
                "image_rights_status": row["image_rights_status"],
                "priority_score": expected[row["id"]]["score"],
                **markup,
                "signals": signals,
                "content_hash_plain": row["content_hash_plain"],
                "content_hash_rich": row["content_hash_rich"],
                "answer_binding_hash": row["answer_binding_hash"],
            }
        )

    return {
        "summary": {
            "requested": len(expected),
            "scanned": len(rows),
            "database_mutations": 0,
            "signal_counts": dict(sorted(signal_counts.items())),
            "rights_counts": dict(sorted(rights_counts.items())),
            "host_counts": dict(sorted(host_counts.items())),
        },
        "details": details,
    }
