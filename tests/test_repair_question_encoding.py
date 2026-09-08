import copy

import pytest

from scripts.apply_question_quality_repairs import execute_plan
from scripts.question_quality_review import canonical_hashes
from scripts.repair_question_encoding import proposal, validate_encoding_plan
from tests.test_analyze_quality_snapshot import example
from tests.test_apply_question_quality_repairs import STAMP, assert_original, database


def sample():
    row = example()
    row.update(id=571701, updated_at='2026-09-07T00:00:00+00:00',
               statement_plain='Hb < 9', enunciado='Hb < 9',
               statement_rich_html='<p>Hb &amp;lt; 9</p>')
    row.update(canonical_hashes(row))
    for alt in row['alternativas']:
        alt['html'] = alt['body_rich_html']
    return row


def test_entities_fixed_without_changing_plain_or_answers():
    row = sample()
    p = proposal(row)
    assert p['set']['statement_rich_html'] == '<p>Hb &lt; 9</p>'
    assert 'statement_plain' not in p['set']
    assert 'alternativa_correta_id' not in p['set']
    validate_encoding_plan([p])
    bad = copy.deepcopy(p)
    bad['set']['enunciado'] = 'Alteração indevida'
    with pytest.raises(ValueError, match='exact reviewed'):
        validate_encoding_plan([bad])


def test_encoding_apply_repeat_reverse():
    plan = [proposal(sample())]
    engine, table = database(plan)
    options = {'validator': validate_encoding_plan}
    execute_plan(engine, table, plan, STAMP, **options)
    assert_original(engine, table, plan)
    assert execute_plan(engine, table, plan, STAMP, apply=True, **options)['changed'] == 1
    assert execute_plan(engine, table, plan, STAMP, apply=True, **options)['changed'] == 0
    execute_plan(engine, table, plan, STAMP, apply=True, reverse=True, **options)
    assert_original(engine, table, plan)


def test_truncated_and_unknown_ids_refused():
    row = sample()
    row['id'] = 645214
    with pytest.raises(ValueError, match='not in reviewed'):
        proposal(row)
