import json
from types import SimpleNamespace

import pytest

from evaluation import (
    PILOT_RUBRICS,
    SYNAPSE_FEEDBACK_INSTRUCTIONS,
    SYNAPSE_QUESTION_INSTRUCTIONS,
    SimulationSubmission,
    SynapseNarrativeEnhancement,
    _contains_any,
    _usage_metrics,
    answer_simulation_question,
    build_compact_feedback_payload,
    build_rule_based_narrative,
    enhance_narrative_with_ai,
    evaluate_objective,
    select_feedback_model,
    select_question_model,
    synapse_runtime_config,
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


def test_synapse_runtime_config_separates_models_and_bounds_output(monkeypatch):
    monkeypatch.setenv("OPENAI_ROUTINE_MODEL", "modelo-economico")
    monkeypatch.setenv("OPENAI_ADVANCED_MODEL", "modelo-avancado")
    monkeypatch.setenv("OPENAI_QUESTION_MODEL", "modelo-do-banco-de-questoes")
    monkeypatch.setenv("OPENAI_REASONING_EFFORT", "inválido")
    monkeypatch.setenv("OPENAI_FEEDBACK_MAX_OUTPUT_TOKENS", "99999")
    monkeypatch.setenv("OPENAI_QUESTION_MAX_OUTPUT_TOKENS", "50")

    config = synapse_runtime_config()

    assert config["modelo_rotina"] == "modelo-economico"
    assert config["modelo_avancado"] == "modelo-avancado"
    assert config["modelo_perguntas"] == "modelo-economico"
    assert config["perguntas_com_roteamento_automatico"] is True
    assert config["esforco_raciocinio"] == "low"
    assert config["limite_saida_feedback"] == 1600
    assert config["limite_saida_pergunta"] == 200

    monkeypatch.setenv("OPENAI_SIMULATION_QUESTION_MODEL", "modelo-fixo")
    overridden = synapse_runtime_config()
    assert overridden["modelo_perguntas"] == "modelo-fixo"
    assert overridden["perguntas_com_roteamento_automatico"] is False


def test_compact_feedback_payload_omits_full_rubric_and_repeated_fields():
    submission = SimulationSubmission(
        exames_solicitados=["hemo"],
        justificativas_exames={"hemo": "Avaliar a intensidade da anemia."},
        hipotese_diagnostica="Anemia ferropriva após bypass gástrico",
        conduta_proposta="Ferro intravenoso e reavaliação com hemograma.",
    )
    case = {
        **_case_seven(),
        "nivel_dificuldade": "Intermediário",
        "historia_clinica": "Fadiga progressiva após cirurgia bariátrica.",
        "exame_fisico": "Palidez cutaneomucosa.",
    }
    score, exams, context = evaluate_objective(case, submission, PILOT_RUBRICS[7])
    compact = build_compact_feedback_payload(case, submission, score, exams, context)
    legacy = {
        "caso": case,
        "respostas_do_estudante": submission.model_dump(),
        "pontuacao_objetiva": score.model_dump(),
        "avaliacao_de_exames": exams.model_dump(),
        "gabarito_clinico": context["rubrica"],
    }

    compact_json = json.dumps(compact, ensure_ascii=False)
    legacy_json = json.dumps(legacy, ensure_ascii=False)
    assert len(compact_json) < len(legacy_json) * 0.7
    assert "fontes_clinicas" not in compact_json
    assert "diagnostico_termos" not in compact_json
    assert compact["avaliacao_objetiva"]["classificacao_hipotese"] == "correta"


def test_model_router_escalates_only_ambiguity_complexity_or_safety(monkeypatch):
    monkeypatch.setenv("OPENAI_ROUTINE_MODEL", "rotina")
    monkeypatch.setenv("OPENAI_ADVANCED_MODEL", "avancado")
    case = {**_case_seven(), "nivel_dificuldade": "Intermediário"}
    safe_submission = SimulationSubmission(
        exames_solicitados=["hemo"],
        hipotese_diagnostica="Anemia ferropriva após bypass gástrico",
        conduta_proposta=(
            "Avaliação urgente, suporte transfusional, ferro intravenoso e "
            "reavaliação com hemograma."
        ),
    )
    safe_score, _, safe_context = evaluate_objective(
        case, safe_submission, PILOT_RUBRICS[7]
    )
    unsafe_submission = SimulationSubmission(
        exames_solicitados=["vit_b12"],
        hipotese_diagnostica="Ansiedade",
        conduta_proposta="Alta e multivitamínico.",
    )
    unsafe_score, _, unsafe_context = evaluate_objective(
        case, unsafe_submission, PILOT_RUBRICS[7]
    )

    assert select_feedback_model(case, safe_score, safe_context) == "rotina"
    assert select_feedback_model(case, unsafe_score, unsafe_context) == "avancado"
    assert select_question_model("Como posso revisar este caso?", {}) == "rotina"
    assert select_question_model("Qual foi o risco de deterioração?", {}) == "avancado"


def test_ai_enhancement_has_output_ceiling_and_preserves_objective_feedback(
    monkeypatch,
):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_ROUTINE_MODEL", "modelo-rotina")
    monkeypatch.setenv("OPENAI_ADVANCED_MODEL", "modelo-avancado")
    monkeypatch.setenv("OPENAI_FEEDBACK_MAX_OUTPUT_TOKENS", "720")
    case = {
        **_case_seven(),
        "nivel_dificuldade": "Intermediário",
        "historia_clinica": "Fadiga progressiva após cirurgia bariátrica.",
        "exame_fisico": "Palidez cutaneomucosa.",
    }
    submission = SimulationSubmission(
        exames_solicitados=["hemo"],
        hipotese_diagnostica="Anemia ferropriva após bypass gástrico",
        conduta_proposta=(
            "Avaliação urgente, suporte transfusional, ferro intravenoso e "
            "reavaliação com hemograma."
        ),
    )
    score, exams, context = evaluate_objective(case, submission, PILOT_RUBRICS[7])
    enhancement = SynapseNarrativeEnhancement(
        resumo="Você reconheceu o problema central e pode consolidar a sequência.",
        sintese_raciocinio=(
            "A hipótese conecta os achados principais; agora organize a conduta "
            "por prioridade e reavaliação."
        ),
        feedback_hipotese="A hipótese foi bem direcionada.",
        feedback_conduta="A conduta contemplou os principais pilares.",
        plano_pessoal_melhoria=["Consolidar a sequência de reavaliação."],
    )
    captured = {}

    class FakeResponses:
        def parse(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                id="resp_efficiency",
                output_parsed=enhancement,
                usage=SimpleNamespace(
                    input_tokens=400,
                    input_tokens_details=SimpleNamespace(cached_tokens=0),
                    output_tokens=180,
                    output_tokens_details=SimpleNamespace(reasoning_tokens=0),
                    total_tokens=580,
                ),
            )

    monkeypatch.setattr(
        "evaluation._openai_client",
        lambda _api_key: SimpleNamespace(responses=FakeResponses()),
    )

    narrative, source, model, usage = enhance_narrative_with_ai(
        case, submission, score, exams, context
    )

    assert source == "openai"
    assert model == "modelo-rotina"
    assert captured["max_output_tokens"] == 720
    assert captured["store"] is False
    assert captured["reasoning"] == {"effort": "low"}
    assert captured["verbosity"] == "low"
    assert captured["text_format"] is SynapseNarrativeEnhancement
    assert narrative.resumo == enhancement.resumo
    assert narrative.acertos
    assert narrative.feedback_seguranca
    assert usage.total_tokens == 580


def test_follow_up_question_uses_compact_context_and_output_policy(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_ROUTINE_MODEL", "modelo-rotina")
    monkeypatch.setenv("OPENAI_QUESTION_MAX_OUTPUT_TOKENS", "333")
    captured = {}

    class FakeResponses:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                id="resp_question_efficiency",
                output_text="Você pode consolidar o caso revisando a sequência clínica.",
                usage=SimpleNamespace(
                    input_tokens=250,
                    input_tokens_details=SimpleNamespace(cached_tokens=50),
                    output_tokens=60,
                    output_tokens_details=SimpleNamespace(reasoning_tokens=10),
                    total_tokens=310,
                ),
            )

    monkeypatch.setattr(
        "evaluation._openai_client",
        lambda _api_key: SimpleNamespace(responses=FakeResponses()),
    )
    evaluation = {
        "pontuacao_total": 82,
        "pontuacao": {"exames": 32, "hipotese": 25, "conduta": 25},
        "nivel_conduta": "adequada",
        "exames": {"adequados": ["Hemograma"], "desnecessarios": []},
        "feedback": {
            "resumo": "Você reconheceu o eixo central do caso.",
            "sintese_raciocinio": "O raciocínio foi bem direcionado.",
            "plano_pessoal_melhoria": ["Revisar a sequência clínica."],
        },
        "fontes_clinicas": ["não deve ser reenviada"],
    }

    answer = answer_simulation_question(
        question="Como posso revisar este caso?",
        case={
            **_case_seven(),
            "nivel_dificuldade": "Intermediário",
            "historia_clinica": "Fadiga progressiva após cirurgia bariátrica.",
            "exame_fisico": "Palidez cutaneomucosa.",
        },
        submission={
            "exames_solicitados": ["hemo"],
            "hipotese_diagnostica": "Anemia ferropriva",
            "conduta_proposta": "Ferro intravenoso e reavaliação.",
        },
        evaluation=evaluation,
        rubric=PILOT_RUBRICS[7],
    )

    assert answer.fonte_feedback == "openai"
    assert answer.modelo_ia == "modelo-rotina"
    assert captured["max_output_tokens"] == 333
    assert captured["reasoning"] == {"effort": "low"}
    assert captured["text"] == {"verbosity": "low"}
    assert captured["store"] is False
    assert "fontes_clinicas" not in captured["input"]
