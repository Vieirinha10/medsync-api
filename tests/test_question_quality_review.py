import copy
import json
from pathlib import Path

import pytest

from scripts.import_question_catalog import validate_and_normalize_record
from scripts.question_quality_review import (
    canonical_hashes,
    inspect_row,
    repair_proposal,
)
from services import question_catalog_audit as audit


def fixture_row():
    source = Path(__file__).parent / 'fixtures/pilot-100-import-ready.jsonl'
    raw = json.loads(source.read_text().splitlines()[0])
    row, *_ = validate_and_normalize_record(raw, 1)
    row['id'] = 1
    return row


def test_hash_contract_matches_canonical_importer_for_fixture():
    source = Path(__file__).parent / 'fixtures/pilot-100-import-ready.jsonl'
    for index, line in enumerate(source.read_text().splitlines(), 1):
        row, *_ = validate_and_normalize_record(json.loads(line), index)
        assert all(row[k] == v for k, v in canonical_hashes(row).items())


def test_repair_recovers_text_and_retains_answers_and_rich_hash():
    row = fixture_row()
    row.update(statement_plain='Hb', statement_rich_html='<p>Hb &lt; 8. Pergunta?</p>')
    row.update(canonical_hashes(row))
    before = copy.deepcopy(row)
    assert 'statement_representation_mismatch' in inspect_row(row)
    proposal = repair_proposal(row)
    assert proposal['set']['enunciado'] == 'Hb < 8. Pergunta?'
    assert proposal['set']['content_hash_rich'] == row['content_hash_rich']
    assert proposal['set']['answer_binding_hash'] != row['answer_binding_hash']
    assert not inspect_row({**row, **proposal['set']})
    assert row == before
    assert 'alternativas' not in proposal['set']
    assert 'alternativa_correta_id' not in proposal['set']


def test_repair_refuses_stale_hashes_and_unchanged_content():
    row = fixture_row()
    row['content_hash_plain'] = '0' * 64
    with pytest.raises(ValueError, match='hashes'):
        repair_proposal(row)
    row.update(statement_plain='Igual', statement_rich_html='<p>Igual</p>')
    row.update(canonical_hashes(row))
    with pytest.raises(ValueError, match='No substantive'):
        repair_proposal(row)


def test_malformed_alternatives_reported_without_aborting_audit():
    row = fixture_row()
    for alts in [None, 'bad', [None], [{'id': 'A'}]]:
        assert inspect_row({**row, 'alternativas': alts})


def test_full_scan_keyset_read_only_and_rolls_back_on_failure():
    from tests.test_question_catalog_audit import _Connection, _Result

    class Connection(_Connection):
        def __init__(self, fail=False):
            super().__init__()
            self.pages = 0
            self.fail = fail

        def execute(self, statement, parameters=None):
            sql = str(statement)
            self.statements.append(sql)
            if 'FROM exam_questions' in sql:
                self.pages += 1
                if self.pages == 1:
                    assert parameters == {'last_id': 0}
                    row = fixture_row()
                    row['id'] = 1003
                    return _Result([row])
                assert parameters == {'last_id': 1003}
                if self.fail:
                    raise RuntimeError('database unavailable')
                return _Result([])
            return _Result([])

    for fail in [False, True]:
        conn = Connection(fail)
        messages = []
        audit.run_question_catalog_audit('quality-test', mode='text_integrity',
                                         connect=lambda conn=conn: conn, emit=messages.append)
        assert conn.transaction.rolled_back
        assert any('READ ONLY' in s for s in conn.statements)
        assert any('REPEATABLE READ' in s for s in conn.statements)
        assert not any(s.lstrip().startswith(('UPDATE', 'INSERT', 'DELETE'))
                       for s in conn.statements)
        assert any('text_integrity_summary' in m for m in messages) is (not fail)
