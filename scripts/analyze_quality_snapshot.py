"""Offline cause analysis and conditional proposals; no database access."""
import argparse
import copy
import html
import json
import re
from collections import Counter
from pathlib import Path

from scripts.extract_clean_batch import sanitize_to_plain_text
from scripts.question_quality_review import canonical_hashes, compact, inspect_row


def legacy_plain(raw):
    value = html.unescape(raw or '')
    value = value.replace('\xa0', ' ').replace('\u200b', '').replace('\ufeff', '')
    value = re.sub(r'</(?:p|div|li|tr|h\d)>', '\n', value, flags=re.I)
    value = re.sub(r'<(?:br|hr)[\s/>]*>', '\n', value, flags=re.I)
    value = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', value, flags=re.S | re.I)
    value = re.sub(r'<[^>]+>', '', value)
    value = '\n'.join(re.sub(r'[ \t]+', ' ', line).strip() for line in value.split('\n'))
    return re.sub(r'\n{3,}', '\n\n', value).strip()


def analyze(row):
    issues = inspect_row(row)
    # A previously edited display/HTML can already agree with the stored hashes.
    # Only propose aligning the stale plain field if all evidence agrees exactly.
    display = row.get('enunciado')
    if (row.get('catalog_version') == 'v2' and row.get('status') == 'publicada'
            and display and display != row.get('statement_plain')
            and display == sanitize_to_plain_text(row.get('statement_rich_html') or '')):
        aligned = {**row, 'statement_plain': display}
        if not inspect_row(aligned) and all(row.get(k) == v for k, v in canonical_hashes(aligned).items()):
            return {'id': row['id'], 'category': 'stale_plain_alignment_candidate',
                    'issues': issues, 'guards': [],
                    'differences': [{'field': 'statement', 'old': row['statement_plain'],
                                     'proposed': display, 'legacy_parser_reproduces': False}],
                    'proposal': {'id': row['id'], 'expected': row,
                                 'set': {'statement_plain': display},
                                 'status': 'conditional_proposal_not_applied',
                                 'clinical_review': 'not_performed',
                                 'requires': ['fresh_row_compare', 'durable_backup',
                                              'transactional_application']}}
    differences = []
    candidate = copy.deepcopy(row)
    guards = []
    if row.get('catalog_version') != 'v2' or row.get('status') != 'publicada':
        guards.append('scope_changed')
    try:
        if any(row.get(k) != v for k, v in canonical_hashes(row).items()):
            guards.append('canonical_hash_mismatch')
    except (KeyError, ValueError, TypeError):
        guards.append('invalid_canonical_payload')

    pairs = [('statement', row.get('statement_plain'), row.get('statement_rich_html'))]
    pairs += [(f'alternative_{i}', a.get('body_plain'), a.get('body_rich_html'))
              for i, a in enumerate(row.get('alternativas') or [])]
    for field, old, rich in pairs:
        if not rich:
            continue
        new = sanitize_to_plain_text(rich)
        if compact(old) == compact(new):
            continue
        reproducible = compact(legacy_plain(rich)) == compact(old)
        differences.append({'field': field, 'old': old, 'proposed': new,
                            'legacy_parser_reproduces': reproducible})
        if not reproducible:
            guards.append('difference_not_explained_by_legacy_parser')
        if not compact(new):
            guards.append('restored_text_empty')
        if field == 'statement':
            if row.get('enunciado') != old:
                guards.append('enunciado_not_equal_to_plain')
            candidate.update(statement_plain=new, enunciado=new)
        else:
            index = int(field.split('_')[1])
            if candidate['alternativas'][index].get('texto') != old:
                guards.append('alternative_texto_not_equal_to_plain')
            candidate['alternativas'][index].update(body_plain=new, texto=new)

    proposal = None
    if differences and not guards:
        hashes = canonical_hashes(candidate)
        candidate.update(hashes)
        candidate['random_rank'] = int(hashes['content_hash_plain'][:13], 16) / float(1 << 52)
        remaining = inspect_row(candidate)
        if remaining:
            guards.append('remaining_structural_signals')
        else:
            keys = ('statement_plain', 'enunciado', 'alternativas', 'content_hash_plain',
                    'content_hash_rich', 'answer_binding_hash', 'random_rank')
            proposal = {'id': row['id'], 'expected': row,
                        'set': {k: candidate[k] for k in keys if candidate.get(k) != row.get(k)},
                        'status': 'conditional_proposal_not_applied',
                        'clinical_review': 'not_performed',
                        'requires': ['review_html_context', 'fresh_row_compare',
                                     'durable_backup', 'transactional_application']}
    category = ('no_longer_flagged' if not issues else
                'reproducible_parser_candidate' if proposal else 'manual_review')
    return {'id': row['id'], 'category': category, 'issues': issues,
            'guards': sorted(set(guards)), 'differences': differences, 'proposal': proposal}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    rows = json.loads(args.snapshot.read_text())['records']
    analysis = [analyze(row) for row in rows]
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'analysis.json').write_text(json.dumps(analysis, ensure_ascii=False, indent=2))
    summary = {'records': len(rows), 'categories': dict(Counter(r['category'] for r in analysis)),
               'differences': sum(len(r['differences']) for r in analysis),
               'guards': dict(Counter(g for r in analysis for g in r['guards'])),
               'database_mutations': 0}
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
