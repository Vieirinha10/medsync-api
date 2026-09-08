"""Export a fixed, reviewed ID list through the internal read-only auditor."""
import base64
import hashlib
import json
import zlib
from pathlib import Path

from sqlalchemy import bindparam, text


def export_snapshot(connection, run_id, emit):
    manifest = json.loads((Path(__file__).resolve().parents[1] /
                           'data/question_quality_flagged_ids.json').read_text())
    ids = manifest['ids']
    if len(ids) != 1321 or len(set(ids)) != len(ids) or not all(type(i) is int for i in ids):
        raise ValueError('Unexpected reviewed ID manifest')
    query = text('''SELECT id, source_id, catalog_version, status, enunciado,
        statement_plain, statement_rich_html, alternativas, alternativa_correta_id,
        content_hash_plain, content_hash_rich, answer_binding_hash, random_rank,
        fingerprint, updated_at, ano, instituicao, especialidade, assunto, tema,
        subtema, media_classification, image_rights_status
        FROM exam_questions WHERE id IN :ids ORDER BY id''').bindparams(bindparam('ids', expanding=True))
    seen = []
    for offset in range(0, len(ids), 100):
        rows = connection.execute(query, {'ids': ids[offset:offset + 100]}).mappings().all()
        for row in rows:
            record = dict(row)
            payload = json.dumps(record, ensure_ascii=False, sort_keys=True,
                                 default=str, separators=(',', ':')).encode()
            encoded = base64.b64encode(zlib.compress(payload)).decode()
            chunks = [encoded[i:i + 1500] for i in range(0, len(encoded), 1500)]
            for part, chunk in enumerate(chunks):
                emit('QUESTION_QUALITY_SNAPSHOT ' + json.dumps({
                    'run_id': run_id, 'id': record['id'], 'part': part,
                    'parts': len(chunks), 'sha256': hashlib.sha256(payload).hexdigest(),
                    'encoding': 'zlib-base64', 'payload': chunk,
                }, separators=(',', ':')))
            seen.append(record['id'])
    missing = sorted(set(ids) - set(seen))
    emit('QUESTION_QUALITY_SNAPSHOT_DONE ' + json.dumps({
        'run_id': run_id, 'requested': len(ids), 'exported': len(seen),
        'missing_ids': missing, 'complete': not missing,
    }, separators=(',', ':')))
