import json

import pytest
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    select,
)

from scripts.apply_question_quality_visual_quarantine import (
    WRITE_COLUMNS,
    execute,
    expected_state,
    validate_manifest,
)


@pytest.fixture
def manifest():
    with open(
        "data/question_quality_visual_quarantine_manifest.json", encoding="utf-8"
    ) as source:
        return json.load(source)


def build_database(manifest):
    engine = create_engine("sqlite://")
    table = Table(
        "exam_questions",
        MetaData(),
        Column("id", Integer, primary_key=True),
        Column("source_id", String),
        Column("catalog_version", String),
        Column("ano", Integer),
        Column("especialidade", String),
        Column("assunto", String),
        Column("status", String),
        Column("quality_status", String),
        Column("quality_flags", JSON),
        Column("quality_method", String),
        Column("quality_source_reference", Text),
        Column("quality_reviewed_at", DateTime(timezone=True)),
        Column("media_classification", String),
        Column("image_rights_status", String),
        Column("content_hash_plain", String),
        Column("content_hash_rich", String),
        Column("answer_binding_hash", String),
    )
    table.create(engine)
    with engine.begin() as connection:
        connection.execute(
            table.insert(), [expected_state(item) for item in manifest["items"]]
        )
    return engine, table


def test_visual_quarantine_dry_run_apply_idempotence_and_reverse(manifest):
    engine, table = build_database(manifest)
    assert execute(engine, table, manifest) == {
        "requested": 8,
        "changed": 8,
        "already_at_target": 0,
        "quarantined": 8,
        "committed": False,
        "reverse": False,
    }
    assert execute(engine, table, manifest, apply=True)["changed"] == 8
    assert execute(engine, table, manifest, apply=True)["changed"] == 0
    first_id = manifest["items"][0]["id"]
    with engine.connect() as connection:
        row = dict(
            connection.execute(select(table).where(table.c.id == first_id))
            .mappings()
            .one()
        )
    assert row["status"] == "revisao"
    assert row["quality_status"] == "revisao_necessaria"
    assert row["quality_flags"] == ["visual_source_required"]
    assert execute(engine, table, manifest, apply=True, reverse=True)["changed"] == 8


def test_visual_quarantine_stale_hash_rolls_back_everything(manifest):
    engine, table = build_database(manifest)
    ids = [item["id"] for item in manifest["items"]]
    with engine.begin() as connection:
        connection.execute(
            table.update()
            .where(table.c.id == ids[0])
            .values(content_hash_rich="unexpected")
        )
    with pytest.raises(ValueError, match=str(ids[0])):
        execute(engine, table, manifest, apply=True)
    with engine.connect() as connection:
        assert (
            connection.execute(
                select(table.c.status).where(table.c.id == ids[1])
            ).scalar_one()
            == "publicada"
        )


def test_visual_quarantine_never_mutates_content_answer_or_taxonomy(manifest):
    validate_manifest(manifest)
    assert WRITE_COLUMNS.isdisjoint(
        {
            "enunciado",
            "statement_plain",
            "statement_rich_html",
            "alternativas",
            "alternativa_correta_id",
            "content_hash_plain",
            "content_hash_rich",
            "answer_binding_hash",
            "especialidade",
            "assunto",
            "tema",
            "subtema",
            "media_classification",
            "image_rights_status",
        }
    )
