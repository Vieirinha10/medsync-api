import copy
from datetime import datetime

import pytest
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    Table,
    Text,
    create_engine,
    select,
    text,
)

from scripts.analyze_quality_snapshot import analyze
from scripts.apply_question_quality_repairs import execute_plan, matches
from tests.test_analyze_quality_snapshot import example

STAMP = '2026-09-08T03:00:00+00:00'


def database(plan):
    engine = create_engine('sqlite://')
    first = plan[0]['expected']
    columns = []
    for key, value in first.items():
        kind = (DateTime(timezone=True) if key == 'updated_at' else JSON if isinstance(value, (list, dict))
                else Integer if type(value) is int else Float if isinstance(value, float) else Text)
        columns.append(Column(key, kind, primary_key=key == 'id'))
    table = Table('exam_questions', MetaData(), *columns)
    table.create(engine)
    with engine.begin() as conn:
        for p in plan:
            row = {**p['expected'], 'updated_at': datetime.fromisoformat(p['expected']['updated_at'])}
            conn.execute(table.insert().values(**row))
    return engine, table


def proposals():
    result = []
    for id in [1, 2]:
        row = example()
        row.update(id=id, updated_at='2026-09-07T00:00:00+00:00')
        result.append(analyze(row)['proposal'])
    return result


def assert_original(engine, table, plan):
    with engine.connect() as conn:
        rows = conn.execute(select(table).order_by(table.c.id)).mappings().all()
    assert all(matches(row, p['expected']) for row, p in zip(rows, plan, strict=True))


def test_dry_run_apply_idempotence_and_reverse_exact():
    plan = proposals()
    engine, table = database(plan)
    assert execute_plan(engine, table, plan, STAMP)['changed'] == 2
    assert_original(engine, table, plan)
    assert execute_plan(engine, table, plan, STAMP, apply=True)['changed'] == 2
    assert execute_plan(engine, table, plan, STAMP, apply=True)['changed'] == 0
    assert execute_plan(engine, table, plan, STAMP, apply=True, reverse=True)['changed'] == 2
    assert_original(engine, table, plan)


def test_concurrent_change_blocks_entire_batch():
    plan = proposals()
    engine, table = database(plan)
    with engine.begin() as conn:
        conn.execute(table.update().where(table.c.id == 2).values(enunciado='Nova edição'))
    with pytest.raises(ValueError, match='ID 2'):
        execute_plan(engine, table, plan, STAMP, apply=True)
    with engine.connect() as conn:
        assert matches(conn.execute(select(table).where(table.c.id == 1)).mappings().one(), plan[0]['expected'])


def test_database_failure_rolls_back_previous_updates():
    plan = proposals()
    engine, table = database(plan)
    with engine.begin() as conn:
        conn.execute(text("CREATE TRIGGER fail_second BEFORE UPDATE ON exam_questions WHEN OLD.id=2 BEGIN SELECT RAISE(ABORT, 'simulated failure'); END"))
    with pytest.raises(Exception, match='simulated failure'):
        execute_plan(engine, table, plan, STAMP, apply=True)
    assert_original(engine, table, plan)


def test_forbidden_field_or_changed_answer_refused():
    plan = proposals()
    engine, table = database(plan)
    modified = copy.deepcopy(plan)
    modified[0]['set']['alternativa_correta_id'] = 'B'
    with pytest.raises(ValueError, match='Forbidden'):
        execute_plan(engine, table, modified, STAMP, apply=True)
    assert_original(engine, table, plan)
