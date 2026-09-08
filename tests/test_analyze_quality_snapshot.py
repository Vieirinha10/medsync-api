import copy

from scripts.analyze_quality_snapshot import analyze, legacy_plain
from scripts.question_quality_review import canonical_hashes
from tests.test_question_quality_review import fixture_row


def example():
    row = fixture_row()
    rich = '<p>Hb &lt; 8 g/dL; <b>próxima pergunta.</b></p>'
    row.update(statement_rich_html=rich, statement_plain=legacy_plain(rich),
               enunciado=legacy_plain(rich), catalog_version='v2', status='publicada')
    row.update(canonical_hashes(row))
    row['random_rank'] = 0.5
    return row


def test_reproducible_recovery_retains_key_and_original():
    row = example()
    before = copy.deepcopy(row)
    result = analyze(row)
    assert result['category'] == 'reproducible_parser_candidate'
    assert result['proposal']['set']['enunciado'] == 'Hb < 8 g/dL; próxima pergunta.'
    assert 'alternativa_correta_id' not in result['proposal']['set']
    assert row == before


def test_stale_hash_and_divergent_display_text_block_proposals():
    row = example()
    row['content_hash_plain'] = 'stale'
    assert analyze(row)['proposal'] is None
    row = example()
    row['enunciado'] = 'Edição posterior'
    assert analyze(row)['proposal'] is None


def test_unexplained_difference_cannot_be_automatically_repaired():
    row = example()
    row['statement_plain'] = row['enunciado'] = 'Texto reescrito manualmente'
    row.update(canonical_hashes(row))
    result = analyze(row)
    assert result['proposal'] is None
    assert 'difference_not_explained_by_legacy_parser' in result['guards']


def test_align_stale_plain_only_when_display_html_and_stored_hashes_agree():
    row = example()
    row['enunciado'] = 'Hb < 8 g/dL; próxima pergunta.'
    row.update(canonical_hashes({**row, 'statement_plain': row['enunciado']}))
    result = analyze(row)
    assert result['category'] == 'stale_plain_alignment_candidate'
    assert result['proposal']['set'] == {'statement_plain': row['enunciado']}
    row['answer_binding_hash'] = 'stale'
    assert analyze(row)['proposal'] is None
