"""Exact encoding repairs for the individually reviewed residual records."""
import copy
import re

from scripts.extract_clean_batch import sanitize_to_plain_text
from scripts.question_quality_review import canonical_hashes, compact, inspect_row

REFERENCE_IDS = {534630, 537370}
ENTITY_IDS = {571701, 580413, 598810, 598812, 599515, 604019, 623270,
              623271, 627784, 628539, 657379, 657600, 657831}
MARKUP_ID = 657437
REVIEWED_IDS = REFERENCE_IDS | ENTITY_IDS | {MARKUP_ID}


def decode_extra_layer(value):
    # Change only known character references, never arbitrary escaped markup.
    return re.sub(r'&amp;((?:quot|apos|nbsp|lt|gt|#34|#39);)', r'&\1', value)


def proposal(row):
    if row['id'] not in REVIEWED_IDS:
        raise ValueError('ID not in reviewed encoding batch')
    if row['catalog_version'] != 'v2' or row['status'] != 'publicada':
        raise ValueError('Scope changed')
    if any(row[k] != v for k, v in canonical_hashes(row).items()):
        raise ValueError('Original hashes do not match')
    new = copy.deepcopy(row)
    if row['id'] in REFERENCE_IDS:
        restored = sanitize_to_plain_text(row['statement_rich_html'])
        if compact(restored.replace('<http', 'http')) != compact(row['statement_plain']):
            raise ValueError('Unexpected reference difference')
        if row['enunciado'] != row['statement_plain']:
            raise ValueError('Display/plain disagreement')
        new.update(statement_plain=restored, enunciado=restored)
    elif row['id'] in ENTITY_IDS:
        new['statement_rich_html'] = decode_extra_layer(row['statement_rich_html'])
        for alt in new['alternativas']:
            if alt['html'] != alt['body_rich_html']:
                raise ValueError('HTML aliases disagree')
            alt['body_rich_html'] = decode_extra_layer(alt['body_rich_html'])
            alt['html'] = alt['body_rich_html']
        # Keep all already readable plain text and all answer metadata intact.
    else:
        for index in (0, 1):
            old = row['alternativas'][index]
            if old['html'] != old['body_rich_html'] or old['texto'] != old['body_plain']:
                raise ValueError('Alternative aliases disagree')
            rich = old['body_rich_html']
            if not rich.startswith('&lt;P&gt;') or not rich.endswith('&lt;/P&gt;'):
                raise ValueError('Expected escaped paragraph wrapper')
            middle = rich[len('&lt;P&gt;'):-len('&lt;/P&gt;')]
            rich = '<p>' + decode_extra_layer(middle) + '</p>'
            plain = sanitize_to_plain_text(rich)
            if compact(re.sub(r'</?P>', '', old['body_plain'])) != compact(plain):
                raise ValueError('Unexpected paragraph content change')
            new['alternativas'][index].update(body_plain=plain, texto=plain,
                                               body_rich_html=rich, html=rich)
    hashes = canonical_hashes(new)
    new.update(hashes)
    new['random_rank'] = int(hashes['content_hash_plain'][:13], 16) / float(1 << 52)
    if inspect_row(new):
        raise ValueError('Residual integrity signals after encoding repair')
    keys = {'statement_plain', 'enunciado', 'statement_rich_html', 'alternativas',
            'content_hash_plain', 'content_hash_rich', 'answer_binding_hash', 'random_rank'}
    changes = {k: new[k] for k in sorted(keys) if row[k] != new[k]}
    if not changes:
        raise ValueError('No encoding change')
    return {'id': row['id'], 'expected': row, 'set': changes,
            'status': 'reviewed_encoding_proposal', 'clinical_review': 'not_performed'}


def validate_encoding_plan(plan):
    if not plan or len({p['id'] for p in plan}) != len(plan):
        raise ValueError('Empty plan or duplicate IDs')
    for p in plan:
        if p['id'] != p['expected']['id'] or not p['expected'].get('updated_at'):
            raise ValueError('Missing identity or timestamp guard')
        if proposal(p['expected'])['set'] != p['set']:
            raise ValueError('Plan differs from exact reviewed encoding transformation')
