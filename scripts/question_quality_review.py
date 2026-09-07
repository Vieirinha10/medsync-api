"""Offline integrity checks and guarded repair proposals; never writes to a DB."""
from __future__ import annotations

import hashlib
import re

from scripts.extract_clean_batch import sanitize_to_plain_text

HASH_FIELDS = ('content_hash_plain', 'content_hash_rich', 'answer_binding_hash')


def canonical_hashes(row):
    """Same payload contract as import_question_catalog.validate_and_normalize_record."""
    alts = sorted(row['alternativas'], key=lambda a: a['id'])
    ids = [a['id'] for a in alts]
    if len(ids) < 2 or len(set(ids)) != len(ids):
        raise ValueError('Invalid alternative IDs')
    if any(type(a['is_correct']) is not bool for a in alts):
        raise ValueError('Invalid correctness flags')
    correct = row['alternativa_correta_id']
    if [a['id'] for a in alts if a['is_correct']] != [correct]:
        raise ValueError('Answer binding mismatch')
    def sha(value):
        return hashlib.sha256(value.encode('utf-8')).hexdigest()
    plain = '|'.join(f"{a['id']}:{a['body_plain']}" for a in alts)
    rich = '|'.join(f"{a['id']}:{a['body_rich_html']}" for a in alts)
    binding = '|'.join(f"{a['id']}:{int(a['is_correct'])}" for a in alts)
    hp = sha(f"{row['statement_plain']}||{plain}")
    return dict(zip(HASH_FIELDS, [
        hp, sha(f"{row['statement_rich_html']}||{rich}"),
        sha(f'{hp}||{correct}||{binding}'),
    ], strict=True))


def compact(value):
    return re.sub(r'\s+', '', value or '')


def inspect_row(row):
    """Signals require review; no signal is a medical approval."""
    issues = []
    if not compact(row.get('statement_plain')):
        issues.append('empty_statement_plain')
    rich = row.get('statement_rich_html')
    if not rich:
        issues.append('missing_statement_rich_html')
    elif compact(sanitize_to_plain_text(rich)) != compact(row.get('statement_plain')):
        issues.append('statement_representation_mismatch')
    alts = row.get('alternativas')
    if not isinstance(alts, list):
        return issues + ['alternatives_not_array']
    for index, alt in enumerate(alts):
        if not isinstance(alt, dict):
            issues.append(f'alternative_{index}_not_object')
            continue
        if not any(compact(str(alt.get(k) or '')) for k in
                   ('body_plain', 'texto', 'body', 'body_rich_html', 'html')):
            issues.append(f'alternative_{index}_empty')
        html = alt.get('body_rich_html')
        if html and compact(sanitize_to_plain_text(html)) != compact(alt.get('body_plain')):
            issues.append(f'alternative_{index}_representation_mismatch')
    try:
        calculated = canonical_hashes(row)
        issues.extend(f'{key}_mismatch' for key, value in calculated.items()
                      if row.get(key) != value)
    except (KeyError, TypeError, ValueError, AttributeError):
        issues.append('invalid_canonical_payload')
    return issues


def repair_proposal(row):
    """Produce old/new values only after verifying all three original hashes."""
    old_hashes = canonical_hashes(row)
    if any(row.get(k) != v for k, v in old_hashes.items()):
        raise ValueError(f"Stale/corrupt hashes: {row['id']}")
    restored = sanitize_to_plain_text(row['statement_rich_html'])
    if compact(restored) == compact(row['statement_plain']):
        raise ValueError('No substantive statement change')
    hashes = canonical_hashes({**row, 'statement_plain': restored})
    hp = hashes['content_hash_plain']
    return {
        'id': row['id'],
        'expected': dict(row),
        'additional_live_guards': {
            'catalog_version': 'v2', 'status': 'publicada',
            'enunciado': row['statement_plain'],
            'fingerprint': f"q_v2_{row['source_id']}",
        },
        'set': {'statement_plain': restored, 'enunciado': restored, **hashes,
                'random_rank': int(hp[:13], 16) / float(1 << 52)},
        'requires_live_snapshot': ['updated_at', 'random_rank', 'enunciado'],
        'status': 'proposal_not_applied',
    }
