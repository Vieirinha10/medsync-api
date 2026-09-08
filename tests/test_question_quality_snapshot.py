import base64
import hashlib
import json
import zlib
from pathlib import Path

from services import question_catalog_audit as audit
from tests.test_question_catalog_audit import _Connection, _Result


def test_snapshot_transport_exact_and_database_read_only():
    ids = json.loads((Path(__file__).parents[1] /
                      'data/question_quality_flagged_ids.json').read_text())['ids']

    class Connection(_Connection):
        def execute(self, statement, parameters=None):
            self.statements.append(str(statement))
            if parameters:
                return _Result([{'id': i, 'enunciado': 'Hb < 8; ação',
                                 'alternativas': [{'is_correct': True}]}
                                for i in parameters['ids']])
            return _Result([])

    conn = Connection()
    messages = []
    audit.run_question_catalog_audit('test', mode='quality_snapshot',
                                     connect=lambda: conn, emit=messages.append)
    records = []
    for message in messages:
        if message.startswith('QUESTION_QUALITY_SNAPSHOT '):
            part = json.loads(message.split(' ', 1)[1])
            assert part['parts'] == 1
            raw = zlib.decompress(base64.b64decode(part['payload']))
            assert hashlib.sha256(raw).hexdigest() == part['sha256']
            row = json.loads(raw)
            assert row['enunciado'] == 'Hb < 8; ação'
            assert row['alternativas'][0]['is_correct'] is True
            records.append(row['id'])
    assert records == ids
    assert conn.transaction.rolled_back
    assert any('READ ONLY' in sql for sql in conn.statements)
    assert any('REPEATABLE READ' in sql for sql in conn.statements)
    assert not any(sql.strip().startswith(('UPDATE', 'INSERT', 'DELETE')) for sql in conn.statements)
    assert any('"complete":true' in m for m in messages)
