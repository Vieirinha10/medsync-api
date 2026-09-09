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

from scripts.apply_question_quality_taxonomy_resolution import (
    WRITE_COLUMNS,
    execute,
    expected_state,
    matches,
    target_state,
    validate_manifests,
)


@pytest.fixture
def manifests():
    with open(
        "data/question_quality_taxonomy_resolution_manifest.json", encoding="utf-8"
    ) as source:
        resolution = json.load(source)
    with open("data/question_quality_funnel_manifest.json", encoding="utf-8") as source:
        base = json.load(source)
    return resolution, base


def build_database(resolution, base):
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
    base_by_id = validate_manifests(resolution, base)
    rows = []
    for item in resolution["items"]:
        state = expected_state(item, base_by_id)
        state["quality_reviewed_at"] = datetime.fromisoformat(
            state["quality_reviewed_at"]
        )
        rows.append(state)
    with engine.begin() as connection:
        connection.execute(table.insert(), rows)
    return engine, table, base_by_id


def test_resolution_dry_run_apply_idempotence_and_reverse(manifests):
    resolution, base = manifests
    engine, table, base_by_id = build_database(resolution, base)

    dry_run = execute(engine, table, resolution, base)
    assert dry_run == {
        "requested": 19,
        "changed": 19,
        "already_at_target": 0,
        "released": 17,
        "remaining_in_review": 2,
        "committed": False,
        "reverse": False,
    }
    first = resolution["items"][0]
    with engine.connect() as connection:
        current = dict(
            connection.execute(select(table).where(table.c.id == first["id"]))
            .mappings()
            .one()
        )
    assert matches(current, expected_state(first, base_by_id))

    applied = execute(engine, table, resolution, base, apply=True)
    assert applied["changed"] == 19
    assert applied["committed"] is True
    assert execute(engine, table, resolution, base, apply=True)["changed"] == 0

    reviewed_at = resolution["created_at"]
    with engine.connect() as connection:
        current = dict(
            connection.execute(select(table).where(table.c.id == first["id"]))
            .mappings()
            .one()
        )
    assert matches(current, target_state(first, base_by_id, reviewed_at))
    assert (
        execute(engine, table, resolution, base, apply=True, reverse=True)["changed"]
        == 19
    )


def test_resolution_stale_guard_rolls_back_everything(manifests):
    resolution, base = manifests
    engine, table, _ = build_database(resolution, base)
    first_id = resolution["items"][0]["id"]
    with engine.begin() as connection:
        connection.execute(
            table.update()
            .where(table.c.id == first_id)
            .values(answer_binding_hash="unexpected")
        )
    with pytest.raises(ValueError, match=str(first_id)):
        execute(engine, table, resolution, base, apply=True)

    second_id = resolution["items"][1]["id"]
    with engine.connect() as connection:
        second = connection.execute(
            select(table.c.assunto).where(table.c.id == second_id)
        ).scalar_one()
    assert second == "Hematologia"


def test_resolution_never_writes_question_content_or_answer(manifests):
    resolution, base = manifests
    validate_manifests(resolution, base)
    assert WRITE_COLUMNS.isdisjoint(
        {
            "statement_plain",
            "statement_rich_html",
            "enunciado",
            "alternativas",
            "alternativa_correta_id",
            "content_hash_plain",
            "content_hash_rich",
            "answer_binding_hash",
        }
    )


def test_resolution_keeps_editorial_overlap_in_review(manifests):
    resolution, base = manifests
    base_by_id = validate_manifests(resolution, base)
    states = {
        item["id"]: target_state(item, base_by_id, resolution["created_at"])
        for item in resolution["items"]
    }
    assert states[465800]["status"] == "revisao"
    assert states[651659]["status"] == "revisao"
    assert sum(state["status"] == "publicada" for state in states.values()) == 17
    assert all(
        "taxonomy_relocation_pending" not in state["quality_flags"]
        for state in states.values()
    )
