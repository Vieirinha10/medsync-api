import json
from pathlib import Path
from types import SimpleNamespace

from services.question_visual_audit import (
    audit_batch,
    inspect_markup,
    load_batch_manifest,
)


class _Result:
    def __init__(self, rows):
        self.rows = rows

    def mappings(self):
        return self

    def all(self):
        return self.rows


class _Connection:
    dialect = SimpleNamespace(name="postgresql")

    def __init__(self, rows):
        self.rows = rows

    def execute(self, _statement, _parameters=None):
        return _Result(self.rows)


def _row(question_id, source_id, html, rights="PENDING"):
    return {
        "id": question_id,
        "source_id": source_id,
        "ano": 2014,
        "especialidade": "Clínica Médica",
        "assunto": "Cardiologia",
        "status": "publicada",
        "quality_status": "triada",
        "media_classification": "REQUIRES_IMAGE",
        "image_rights_status": rights,
        "statement_rich_html": html,
        "content_hash_plain": "p" * 64,
        "content_hash_rich": "r" * 64,
        "answer_binding_hash": "a" * 64,
    }


def test_batch_manifest_is_complete_and_checksum_protected():
    manifest = load_batch_manifest(Path("data/question_quality_p0_batch_001.json"))
    assert len(manifest["items"]) == 1_000
    assert len({item["id"] for item in manifest["items"]}) == 1_000


def test_inspect_markup_does_not_emit_full_urls():
    result = inspect_markup(
        '<p>Caso</p><img src="https://cdn.example.org/exam/a.png"><img src="/b.png">'
    )
    assert result == {
        "image_tags": 2,
        "source_kinds": {"https_url": 1, "relative_url": 1},
        "source_hosts": ["cdn.example.org"],
    }
    assert "a.png" not in json.dumps(result)


def test_visual_audit_classifies_missing_markup_and_documentation():
    manifest = {
        "items": [
            {"id": 1, "source_id": "s1", "score": 140},
            {"id": 2, "source_id": "s2", "score": 115},
        ]
    }
    result = audit_batch(
        _Connection(
            [
                _row(1, "s1", "<p>Imagem ausente</p>"),
                _row(
                    2,
                    "s2",
                    '<img src="https://cdn.example.org/exam.png">',
                    rights="EDITORIAL_EXAM_FAIR_USE",
                ),
            ]
        ),
        manifest,
    )
    assert result["summary"]["scanned"] == 2
    assert result["summary"]["database_mutations"] == 0
    assert result["summary"]["signal_counts"] == {
        "markup_and_rights_ready": 1,
        "missing_image_markup": 1,
        "rights_documentation_pending": 1,
    }
    assert result["details"][0]["signals"] == [
        "missing_image_markup",
        "rights_documentation_pending",
    ]
