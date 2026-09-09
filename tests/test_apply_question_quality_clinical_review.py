import json
from datetime import datetime

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

from scripts.apply_question_quality_clinical_review import (
    WRITE_COLUMNS,
    execute,
    expected_state,
    validate_manifest,
)


@pytest.fixture
def manifests():
    with open(
        "data/question_quality_clinical_manifest.json", encoding="utf-8"
    ) as source:
        clinical = json.load(source)
    with open("data/question_quality_funnel_manifest.json", encoding="utf-8") as source:
        base = json.load(source)
    with open(
        "data/question_quality_taxonomy_resolution_manifest.json", encoding="utf-8"
    ) as source:
        taxonomy = json.load(source)
    return clinical, base, taxonomy


def build_database(clinical, base, taxonomy):
    engine = create_engine("sqlite://")
    table = Table(
        "exam_questions",
        MetaData(),
        Column("id", Integer, primary_key=True),
        Column("source_id", String),
        Column("catalog_version", String),
        Column("status", String),
        Column("especialidade", String),
        Column("assunto", String),
        Column("tema", String),
        Column("subtema", String),
        Column("content_hash_plain", String),
        Column("content_hash_rich", String),
        Column("answer_binding_hash", String),
        Column("quality_status", String),
        Column("quality_flags", JSON),
        Column("quality_method", String),
        Column("quality_source_reference", Text),
        Column("quality_reviewed_at", DateTime(timezone=True)),
    )
    table.create(engine)
    base_by_id = validate_manifest(clinical, base, taxonomy)
    rows = []
    for item in clinical["items"]:
        state = expected_state(item, base_by_id, taxonomy, base)
        if state["quality_reviewed_at"]:
            state["quality_reviewed_at"] = datetime.fromisoformat(
                state["quality_reviewed_at"]
            )
        rows.append(state)
    with engine.begin() as connection:
        connection.execute(table.insert(), rows)
    return engine, table


def test_clinical_review_dry_run_apply_idempotence_and_reverse(manifests):
    clinical, base, taxonomy = manifests
    engine, table = build_database(clinical, base, taxonomy)
    assert execute(engine, table, clinical, base, taxonomy) == {
        "requested": 33,
        "changed": 6,
        "already_at_target": 27,
        "released": 6,
        "remaining_in_review": 27,
        "committed": False,
        "reverse": False,
    }
    assert execute(engine, table, clinical, base, taxonomy, apply=True)["changed"] == 6
    assert execute(engine, table, clinical, base, taxonomy, apply=True)["changed"] == 0
    release_id = next(
        item["id"]
        for item in clinical["items"]
        if item["decision"] == "release_validated"
    )
    with engine.connect() as connection:
        row = dict(
            connection.execute(select(table).where(table.c.id == release_id))
            .mappings()
            .one()
        )
    assert row["status"] == "publicada"
    assert row["quality_status"] == "validada_com_fonte"
    assert row["quality_flags"] == ["clinical_reviewed_v1"]
    assert (
        execute(engine, table, clinical, base, taxonomy, apply=True, reverse=True)[
            "changed"
        ]
        == 6
    )


def test_clinical_review_stale_guard_rolls_back_everything(manifests):
    clinical, base, taxonomy = manifests
    engine, table = build_database(clinical, base, taxonomy)
    ids = [
        item["id"]
        for item in clinical["items"]
        if item["decision"] == "release_validated"
    ]
    with engine.begin() as connection:
        connection.execute(
            table.update()
            .where(table.c.id == ids[0])
            .values(answer_binding_hash="unexpected")
        )
    with pytest.raises(ValueError, match=str(ids[0])):
        execute(engine, table, clinical, base, taxonomy, apply=True)
    with engine.connect() as connection:
        assert (
            connection.execute(
                select(table.c.status).where(table.c.id == ids[1])
            ).scalar_one()
            == "revisao"
        )


def test_clinical_review_never_mutates_content_answer_or_taxonomy(manifests):
    clinical, base, taxonomy = manifests
    validate_manifest(clinical, base, taxonomy)
    assert WRITE_COLUMNS.isdisjoint(
        {
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
        }
    )


def test_manifest_releases_only_sourced_validated_items(manifests):
    clinical, base, taxonomy = manifests
    validate_manifest(clinical, base, taxonomy)
    released = [
        item for item in clinical["items"] if item["decision"] == "release_validated"
    ]
    assert [item["id"] for item in released] == [
        445725,
        458428,
        460637,
        559904,
        571660,
        651659,
    ]
    assert len(clinical["items"]) - len(released) == 27
    assert all(item["sources"] for item in released)
