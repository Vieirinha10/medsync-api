from types import SimpleNamespace

import pytest

from evaluation import (
    PILOT_RUBRICS,
    SYNAPSE_FEEDBACK_INSTRUCTIONS,
    SYNAPSE_QUESTION_INSTRUCTIONS,
    SimulationSubmission,
    _contains_any,
    _usage_metrics,
    build_rule_based_narrative,
    evaluate_objective,
)


def test_openai_usage_metrics_include_cache_reasoning_duration_and_cost(monkeypatch):
    monkeypatch.setattr("evaluation.time.perf_counter", lambda: 11.25)
    response = SimpleNamespace(
        id="resp_synapse_123",
        usage=SimpleNamespace(
            input_tokens=1000,
            input_tokens_details=SimpleNamespace(cached_tokens=200),
            output_tokens=500,
            output_tokens_details=SimpleNamespace(reasoning_tokens=300),
            total_tokens=1500,
        ),
    )

    metrics = _usage_metrics(response, "gpt-5.6", 10.0)

    assert metrics.input_tokens == 1000
    assert metrics.cached_input_tokens == 200
    assert metrics.output_tokens == 500
    assert metrics.reasoning_tokens == 300
    assert metrics.total_tokens == 1500
    assert metrics.duracao_ms == 1250
    assert metrics.custo_estimado_usd == pytest.approx(0.01328)
    assert metrics.response_id == "resp_synapse_123"


def _case_seven():
    return {
        "id": 7,
        "titulo": "Fadiga após cirurgia bariátrica",
        "exames_disponiveis": [
            {"id": "hemo", "nome": "Hemograma"},
            {"id": "ferro", "nome": "Perfil de Ferro"},
            {"id": "vit_b12", "nome": "Vitamina B12 e Folato"},
        ],
    }


def test_conduct_matching_accepts_clinical_language_variants_without_losing_safety():
    submission = SimulationSubmission(
        exames_solicitados=["hemo"],
        hipotese_diagnostica="Anemia ferropriva após bypass gástrico",
        conduta_proposta=(
            "Encaminhar para avaliação urgente devido à anemia grave. "
            "Considerar suporte transfusional conforme estabilidade e iniciar "
            "ferro intravenoso. Reavaliar com hemograma e ferritina."
        ),
    )

    score, _, context = evaluate_objective(_case_seven(), submission, PILOT_RUBRICS[7])

    assert score.conduta == 24
    assert context["seguranca_ausente"] == []
    assert context["nivel_conduta"] == "adequada"


def test_negated_interventions_do_not_earn_conduct_or_safety_credit():
    submission = SimulationSubmission(
        exames_solicitados=["vit_b12"],
        hipotese_diagnostica="Ansiedade com sintomas somáticos",
        conduta_proposta=(
            "Dar alta para acompanhamento ambulatorial e usar multivitamínico. "
            "Não há necessidade de internação, transfusão ou avaliação urgente."
        ),
    )

    score, _, context = evaluate_objective(_case_seven(), submission, PILOT_RUBRICS[7])

    assert score.conduta == 6
    assert len(context["seguranca_ausente"]) == 2
    assert context["nivel_conduta"] == "insegura"


def test_negated_diagnosis_does_not_match_reference_term():
    assert not _contains_any(
        "O quadro não é anemia ferropriva.",
        ["anemia ferropriva"],
    )


def test_rule_based_feedback_recognizes_reasoning_before_the_next_step():
    submission = SimulationSubmission(
        exames_solicitados=["hemo"],
        hipotese_diagnostica=(
            "Anemia ferropriva após bypass gástrico — anotação livre do estudante"
        ),
        conduta_proposta=("Iniciar ferro intravenoso — anotação livre do estudante"),
    )

    score, exams, context = evaluate_objective(
        _case_seven(), submission, PILOT_RUBRICS[7]
    )
    narrative = build_rule_based_narrative(submission, score, exams, context)

    assert narrative.sintese_raciocinio.startswith(
        "Você reconheceu corretamente o eixo central do caso"
    )
    assert "ponto mais importante" in narrative.sintese_raciocinio
    assert "anotação livre do estudante" not in narrative.model_dump_json()


def test_rule_based_feedback_keeps_patient_safety_explicit_and_firm():
    submission = SimulationSubmission(
        exames_solicitados=["vit_b12"],
        hipotese_diagnostica="Ansiedade com sintomas somáticos",
        conduta_proposta=(
            "Alta com multivitamínico; não há necessidade de avaliação urgente."
        ),
    )

    score, exams, context = evaluate_objective(
        _case_seven(), submission, PILOT_RUBRICS[7]
    )
    narrative = build_rule_based_narrative(submission, score, exams, context)

    assert context["nivel_conduta"] == "insegura"
    assert narrative.feedback_seguranca.startswith(
        "Há um ponto importante de segurança para revisar antes de prosseguir."
    )
    assert "avaliação urgente" in narrative.feedback_seguranca
    assert narrative.plano_pessoal_melhoria[0].startswith(
        "Antes de finalizar a conduta"
    )


def test_synapse_ai_prompts_share_the_same_educational_voice_contract():
    for instructions in (
        SYNAPSE_FEEDBACK_INSTRUCTIONS,
        SYNAPSE_QUESTION_INSTRUCTIONS,
    ):
        assert "preceptora clínica atenta" in instructions
        assert "próximo passo" in instructions
        assert "elogios genéricos" in instructions
        assert "risco ao paciente" in instructions
