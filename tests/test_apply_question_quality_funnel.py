import copy
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

from scripts.apply_question_quality_funnel import (
    execute,
    expected_state,
    matches,
    target_state,
)


def build_database(manifest):
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
    with engine.begin() as connection:
        connection.execute(
            table.insert(), [expected_state(item) for item in manifest["items"]]
        )
    return engine, table


@pytest.fixture
def manifest():
    with open("data/question_quality_funnel_manifest.json", encoding="utf-8") as source:
        return json.load(source)


def test_quality_funnel_dry_run_apply_idempotence_and_reverse(manifest):
    engine, table = build_database(manifest)
    assert execute(engine, table, manifest)["changed"] == 209
    with engine.connect() as connection:
        assert matches(
            dict(
                connection.execute(select(table).where(table.c.id == 629086))
                .mappings()
                .one()
            ),
            expected_state(
                next(item for item in manifest["items"] if item["id"] == 629086)
            ),
        )

    applied = execute(engine, table, manifest, apply=True)
    assert applied == {
        "requested": 209,
        "changed": 209,
        "already_at_target": 0,
        "committed": True,
        "reverse": False,
    }
    assert execute(engine, table, manifest, apply=True)["changed"] == 0
    assert execute(engine, table, manifest, apply=True, reverse=True)["changed"] == 209


def test_quality_funnel_stale_guard_aborts_everything(manifest):
    engine, table = build_database(manifest)
    first_id = manifest["items"][0]["id"]
    with engine.begin() as connection:
        connection.execute(
            table.update()
            .where(table.c.id == first_id)
            .values(content_hash_plain="changed")
        )
    with pytest.raises(ValueError, match=str(first_id)):
        execute(engine, table, manifest, apply=True)

    untouched = manifest["items"][1]
    with engine.connect() as connection:
        row = dict(
            connection.execute(select(table).where(table.c.id == untouched["id"]))
            .mappings()
            .one()
        )
    assert matches(row, expected_state(untouched))


def test_quality_funnel_rejects_answer_mutations(manifest):
    modified = copy.deepcopy(manifest)
    modified["items"][0]["set"]["alternativa_correta_id"] = "A"
    # Recalcular o checksum não pode tornar uma escrita de gabarito aceitável.
    from scripts.apply_question_quality_funnel import manifest_digest

    modified["plan_sha256"] = manifest_digest(modified["items"])
    engine, table = build_database(manifest)
    with pytest.raises(ValueError, match="Invalid writes"):
        execute(engine, table, modified, apply=True)


def test_manifest_has_expected_quality_distribution(manifest):
    statuses = [target_state(item)["quality_status"] for item in manifest["items"]]
    assert statuses.count("triada") == 157
    assert statuses.count("revisao_necessaria") == 50
    assert statuses.count("anulada") == 2
    assert (
        sum(target_state(item)["status"] == "revisao" for item in manifest["items"])
        == 52
    )
