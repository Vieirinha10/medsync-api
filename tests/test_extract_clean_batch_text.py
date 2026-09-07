import pytest

from scripts.extract_clean_batch import sanitize_to_plain_text


@pytest.mark.parametrize(('source', 'expected'), [
    ('<p>Neutropenia (&lt;500/mm³). Qual NÃO é critério?</p>',
     'Neutropenia (<500/mm³). Qual NÃO é critério?'),
    ('<div>Hb &lt; 8 g%: alto risco.</div><div>Próxima assertiva.</div>',
     'Hb < 8 g%: alto risco.\nPróxima assertiva.'),
    ('<p>AST: 22 (&lt;40); ALT: 20 (&lt;40); BT: 0,7 (&lt;1,2).</p>',
     'AST: 22 (<40); ALT: 20 (<40); BT: 0,7 (<1,2).'),
    ('<p>8 < Hb < 11 e plaquetas > 100.</p>',
     '8 < Hb < 11 e plaquetas > 100.'),
    ('<p>SpO<sub>2</sub> &gt; 92% &amp; estável.</p>',
     'SpO2 > 92% & estável.'),
    ('<p>&lt;teste&gt; literal</p>', '<teste> literal'),
    ('<p>&amp;lt; literal</p>', '&lt; literal'),
    ('<script>segredo</script><style>oculto</style><p>Visível</p>', 'Visível'),
    ('<table><tr><td>Hb</td><td>8</td></tr></table>', 'Hb 8'),
    ('<P>A</P><BR/><p>B&nbsp; C</p>', 'A\n\nB C'),
    ('', ''),
])
def test_plain_text_preserves_clinical_content(source, expected):
    assert sanitize_to_plain_text(source) == expected
