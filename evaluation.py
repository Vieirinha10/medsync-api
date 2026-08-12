import json
import logging
import os
import re
import unicodedata
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from clinical_rubric_catalog import CLINICAL_RUBRIC_VERSION, CLINICAL_RUBRICS

logger = logging.getLogger(__name__)


class SimulationSubmission(BaseModel):
    exames_solicitados: list[str] = Field(default_factory=list)
    justificativas_exames: dict[str, str] = Field(default_factory=dict)
    hipotese_diagnostica: str = Field(min_length=3, max_length=4000)
    conduta_proposta: str = Field(min_length=3, max_length=4000)

    @model_validator(mode="after")
    def validate_exam_rationales(self):
        selected = set(self.exames_solicitados)
        if set(self.justificativas_exames) - selected:
            raise ValueError("Só é possível justificar exames selecionados.")
        if any(len(text.strip()) > 600 for text in self.justificativas_exames.values()):
            raise ValueError("Cada justificativa deve ter no máximo 600 caracteres.")
        self.justificativas_exames = {
            exam_id: text.strip()
            for exam_id, text in self.justificativas_exames.items()
            if text.strip()
        }
        return self


class ScoreBreakdown(BaseModel):
    exames: int = Field(ge=0, le=40)
    hipotese: int = Field(ge=0, le=30)
    conduta: int = Field(ge=0, le=30)


class ExamFeedback(BaseModel):
    adequados: list[str]
    essenciais_ausentes: list[str]
    desnecessarios: list[str]
    comentario: str


class ExamRationaleFeedback(BaseModel):
    exame_id: str
    exame: str
    justificativa_estudante: str | None = None
    compreensao: Literal["adequada", "parcial", "nao_justificada"]
    feedback: str


class ClinicalEvent(BaseModel):
    tipo: Literal["tempo", "atraso", "resposta", "seguranca"]
    titulo: str
    descricao: str
    minutos: int = Field(default=0, ge=0)


class VitalReassessment(BaseModel):
    indicador: str
    antes: str
    depois: str
    tendencia: Literal["melhora", "estavel", "piora"]


class ClinicalConsequences(BaseModel):
    tempo_desperdicado_minutos: int = Field(default=0, ge=0)
    atraso_diagnostico_minutos: int = Field(default=0, ge=0)
    tempo_total_impactado_minutos: int = Field(default=0, ge=0)
    estado_paciente: Literal["estabilizado", "resposta_parcial", "deterioracao"]
    eventos: list[ClinicalEvent] = Field(default_factory=list)
    reavaliacao: list[VitalReassessment] = Field(default_factory=list)
    aviso_tempo: str = (
        "Tempo educacional fictício usado para demonstrar o impacto das decisões; "
        "não representa prazo real de atendimento ou de liberação de exames."
    )


class ClinicalNarrative(BaseModel):
    resumo: str
    sintese_raciocinio: str = "Síntese não registrada nesta versão da avaliação."
    acertos: list[str]
    omissoes: list[str] = Field(default_factory=list)
    exames_baixo_valor: list[str] = Field(default_factory=list)
    pontos_melhoria: list[str]
    feedback_hipotese: str
    feedback_conduta: str
    feedback_seguranca: str
    reacao_paciente: str = (
        "A reação do paciente não foi registrada nesta versão da avaliação."
    )
    desfecho_clinico: str = (
        "O desfecho clínico não foi registrado nesta versão da avaliação."
    )
    justificativas_exames: list[ExamRationaleFeedback] = Field(default_factory=list)
    plano_pessoal_melhoria: list[str] = Field(default_factory=list)
    recomendacoes_estudo: list[str]


class SimulationEvaluation(BaseModel):
    progresso_id: int
    caso_id: int
    caso_titulo: str
    diagnostico_referencia: str | None = None
    pontuacao_total: int = Field(ge=0, le=100)
    pontuacao: ScoreBreakdown
    exames: ExamFeedback
    feedback: ClinicalNarrative
    objetivos_aprendizagem: list[str] = Field(default_factory=list)
    fontes_clinicas: list[dict[str, Any]] = Field(default_factory=list)
    nivel_conduta: Literal["adequada", "parcial", "insegura"] = "parcial"
    consequencias: ClinicalConsequences | None = None
    versao_rubrica: int | None = None
    fonte_feedback: Literal["openai", "agente_regras"]
    modelo_ia: str | None = None
    aviso_educacional: str = (
        "Feedback destinado exclusivamente ao treinamento acadêmico. "
        "Não substitui protocolos locais, supervisão docente ou decisão médica real."
    )


class ConductCriterion(BaseModel):
    nome: str = Field(min_length=3, max_length=160)
    pontos: int = Field(gt=0, le=30)
    termos: list[str] = Field(min_length=1)


class SafetyCriterion(BaseModel):
    nome: str = Field(min_length=3, max_length=160)
    termos: list[str] = Field(min_length=1)
    feedback_omissao: str = Field(min_length=3)


class OutcomeLevel(BaseModel):
    reacao: str = Field(min_length=3)
    desfecho: str = Field(min_length=3)
    reavaliacao: list[VitalReassessment] = Field(default_factory=list)


class SimulationQuestionRequest(BaseModel):
    pergunta: str = Field(min_length=5, max_length=500)


class SimulationQuestionResponse(BaseModel):
    resposta: str
    fonte_feedback: Literal["openai", "agente_regras"]
    modelo_ia: str | None = None
    aviso_educacional: str = "Resposta restrita ao caso simulado e à rubrica revisada; não constitui orientação para pacientes reais."


class OutcomeMatrix(BaseModel):
    adequada: OutcomeLevel
    parcial: OutcomeLevel
    insegura: OutcomeLevel


class ClinicalSource(BaseModel):
    titulo: str = Field(min_length=3)
    organizacao: str = Field(min_length=2)
    ano: int = Field(ge=2000, le=2100)
    url: str = Field(pattern=r"^https://")


class ClinicalRubricDefinition(BaseModel):
    diagnostico_referencia: str = Field(min_length=3)
    diagnostico_termos: list[str] = Field(min_length=1)
    diagnostico_parcial: list[str] = Field(default_factory=list)
    exames_essenciais: list[str] = Field(default_factory=list)
    exames_opcionais: list[str] = Field(default_factory=list)
    exames_desnecessarios: list[str] = Field(default_factory=list)
    justificativa_exames: dict[str, str] = Field(default_factory=dict)
    conduta_criterios: list[ConductCriterion] = Field(min_length=1)
    conduta_referencia: str = Field(min_length=3)
    feedback_hipotese_parcial: str = Field(min_length=3)
    feedback_hipotese_incorreta: str = Field(min_length=3)
    feedback_seguranca: str = Field(min_length=3)
    objetivos_aprendizagem: list[str] = Field(default_factory=list)
    criterios_seguranca: list[SafetyCriterion] = Field(default_factory=list)
    desfechos_conduta: OutcomeMatrix | None = None
    reacao_paciente_referencia: str = Field(
        default="A resposta do paciente depende da adequação e da segurança das medidas propostas.",
        min_length=3,
    )
    desfecho_referencia: str = Field(
        default="O paciente deve ser reavaliado após a conduta inicial e acompanhado conforme a evolução clínica.",
        min_length=3,
    )
    temas_estudo: list[str] = Field(min_length=1)
    fontes_clinicas: list[ClinicalSource] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_scoring_and_exam_groups(self):
        if sum(item.pontos for item in self.conduta_criterios) > 30:
            raise ValueError("A soma dos critérios de conduta não pode ultrapassar 30.")

        groups = [
            set(self.exames_essenciais),
            set(self.exames_opcionais),
            set(self.exames_desnecessarios),
        ]
        if any(
            groups[index] & groups[other]
            for index in range(3)
            for other in range(index + 1, 3)
        ):
            raise ValueError(
                "Um exame não pode pertencer a grupos diferentes na rubrica."
            )
        return self


PILOT_RUBRIC_VERSION = CLINICAL_RUBRIC_VERSION
PILOT_RUBRICS = CLINICAL_RUBRICS


def is_v2_case(case_id: int) -> bool:
    return case_id in PILOT_RUBRICS


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    without_accents = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return re.sub(r"\s+", " ", without_accents.lower()).strip()


def _contains_any(text: str, terms: list[str]) -> bool:
    normalized = _normalize(text)
    return any(_normalize(term) in normalized for term in terms)


def _exam_name_map(case: dict[str, Any]) -> dict[str, str]:
    return {exam["id"]: exam["nome"] for exam in case.get("exames_disponiveis", [])}


def evaluate_objective(
    case: dict[str, Any],
    submission: SimulationSubmission,
    rubric: dict[str, Any] | None = None,
) -> tuple[ScoreBreakdown, ExamFeedback, dict[str, Any]]:
    rubric = rubric or PILOT_RUBRICS[case["id"]]
    names = _exam_name_map(case)
    selected = set(submission.exames_solicitados)
    essential = set(rubric["exames_essenciais"])
    optional = set(rubric["exames_opcionais"])
    unnecessary = set(rubric["exames_desnecessarios"])

    selected_essential = selected & essential
    missing_essential = essential - selected
    selected_unnecessary = selected & unnecessary
    accepted = selected_essential | (selected & optional)

    essential_points = round(36 * len(selected_essential) / max(len(essential), 1))
    unnecessary_penalty = 4 * len(selected_unnecessary)
    exam_score = max(0, min(40, essential_points + 4 - unnecessary_penalty))

    if _contains_any(
        submission.hipotese_diagnostica,
        rubric["diagnostico_termos"],
    ):
        hypothesis_score = 30
        hypothesis_classification = "correta"
    elif _contains_any(
        submission.hipotese_diagnostica,
        rubric["diagnostico_parcial"],
    ):
        hypothesis_score = 15
        hypothesis_classification = "parcial"
    else:
        hypothesis_score = 0
        hypothesis_classification = "incorreta"

    matched_conduct = []
    missing_conduct = []
    missing_safety = []
    conduct_score = 0
    for criterion in rubric["conduta_criterios"]:
        if _contains_any(submission.conduta_proposta, criterion["termos"]):
            conduct_score += criterion["pontos"]
            matched_conduct.append(criterion["nome"])
        else:
            missing_conduct.append(criterion["nome"])

    for criterion in rubric.get("criterios_seguranca", []):
        if not _contains_any(submission.conduta_proposta, criterion["termos"]):
            missing_safety.append(
                {
                    "nome": criterion["nome"],
                    "feedback": criterion["feedback_omissao"],
                }
            )

    score = ScoreBreakdown(
        exames=exam_score,
        hipotese=hypothesis_score,
        conduta=conduct_score,
    )
    exam_feedback = ExamFeedback(
        adequados=[names[exam_id] for exam_id in sorted(accepted)],
        essenciais_ausentes=[names[exam_id] for exam_id in sorted(missing_essential)],
        desnecessarios=[names[exam_id] for exam_id in sorted(selected_unnecessary)],
        comentario=(
            "A seleção foi comparada ao gabarito clínico estruturado do caso. "
            "Exames essenciais ausentes reduzem a pontuação e exames de baixo valor "
            "neste cenário geram penalidade."
        ),
    )
    context = {
        "rubrica": rubric,
        "nomes_exames": names,
        "exames_selecionados": sorted(selected),
        "classificacao_hipotese": hypothesis_classification,
        "condutas_identificadas": matched_conduct,
        "condutas_ausentes": missing_conduct,
        "seguranca_ausente": missing_safety,
        "nivel_conduta": (
            "insegura"
            if missing_safety
            else "adequada"
            if conduct_score >= 24
            else "parcial"
        ),
    }
    return score, exam_feedback, context


def build_exam_rationale_feedback(
    submission: SimulationSubmission,
    context: dict[str, Any],
) -> list[ExamRationaleFeedback]:
    rubric = context["rubrica"]
    names = context["nomes_exames"]
    references = rubric.get("justificativa_exames", {})
    feedback = []
    for exam_id in context["exames_selecionados"]:
        student_text = submission.justificativas_exames.get(exam_id)
        reference = references.get(
            exam_id,
            "A utilidade deste exame não foi detalhada na rubrica revisada.",
        )
        feedback.append(
            ExamRationaleFeedback(
                exame_id=exam_id,
                exame=names.get(exam_id, exam_id),
                justificativa_estudante=student_text,
                compreensao="parcial" if student_text else "nao_justificada",
                feedback=(
                    f"Sua justificativa foi registrada. Compare com a referência: {reference}"
                    if student_text
                    else f"Justificativa opcional não informada. Utilidade de referência: {reference}"
                ),
            )
        )
    return feedback


def build_clinical_consequences(
    exams: ExamFeedback,
    context: dict[str, Any],
) -> ClinicalConsequences:
    """Converte decisões em consequências educacionais determinísticas da rubrica."""
    wasted = 12 * len(exams.desnecessarios)
    delay = 18 * len(exams.essenciais_ausentes)
    level = context.get("nivel_conduta", "parcial")
    state_by_level = {
        "adequada": "estabilizado",
        "parcial": "resposta_parcial",
        "insegura": "deterioracao",
    }
    events: list[ClinicalEvent] = []
    if exams.desnecessarios:
        events.append(
            ClinicalEvent(
                tipo="tempo",
                titulo="Exames de baixo valor consumiram tempo",
                descricao="Na simulação: " + ", ".join(exams.desnecessarios) + ".",
                minutos=wasted,
            )
        )
    if exams.essenciais_ausentes:
        events.append(
            ClinicalEvent(
                tipo="atraso",
                titulo="Omissões atrasaram a definição diagnóstica",
                descricao="Exames essenciais ausentes: "
                + ", ".join(exams.essenciais_ausentes)
                + ".",
                minutos=delay,
            )
        )
    outcome = (context["rubrica"].get("desfechos_conduta") or {}).get(level, {})
    events.append(
        ClinicalEvent(
            tipo="resposta" if level != "insegura" else "seguranca",
            titulo={
                "adequada": "A conduta estabilizou o paciente",
                "parcial": "A resposta clínica foi parcial",
                "insegura": "A conduta aumentou o risco de deterioração",
            }[level],
            descricao=outcome.get("reacao", "Reação delimitada pela rubrica clínica."),
        )
    )
    return ClinicalConsequences(
        tempo_desperdicado_minutos=wasted,
        atraso_diagnostico_minutos=delay,
        tempo_total_impactado_minutos=wasted + delay,
        estado_paciente=state_by_level[level],
        eventos=events,
        reavaliacao=outcome.get("reavaliacao", []),
    )


def build_rule_based_narrative(
    submission: SimulationSubmission,
    score: ScoreBreakdown,
    exams: ExamFeedback,
    context: dict[str, Any],
) -> ClinicalNarrative:
    rubric = context["rubrica"]
    strengths = []
    improvements = []

    if exams.adequados:
        strengths.append(
            "Você selecionou exames que contribuem diretamente para confirmar "
            "o diagnóstico e avaliar a gravidade."
        )
    if context["classificacao_hipotese"] == "correta":
        strengths.append("A hipótese principal está alinhada ao diagnóstico do caso.")
    elif context["classificacao_hipotese"] == "parcial":
        improvements.append(
            rubric.get(
                "feedback_hipotese_parcial",
                "A hipótese reconheceu parte do quadro, mas precisa ser mais específica.",
            )
        )
    else:
        improvements.append(
            rubric.get(
                "feedback_hipotese_incorreta",
                "A hipótese informada não corresponde ao diagnóstico de referência.",
            )
        )

    if context["condutas_identificadas"]:
        strengths.append(
            "A conduta contemplou: "
            + ", ".join(context["condutas_identificadas"])
            + "."
        )

    if exams.essenciais_ausentes:
        improvements.append(
            "Revise a indicação dos exames essenciais que não foram solicitados."
        )
    if exams.desnecessarios:
        improvements.append(
            "Evite exames de baixo valor quando a probabilidade clínica já é alta "
            "e o resultado não mudará a necessidade de investigação definitiva."
        )
    if context["condutas_ausentes"]:
        improvements.append(
            "A conduta precisa contemplar: "
            + ", ".join(context["condutas_ausentes"])
            + "."
        )
    for safety_item in context.get("seguranca_ausente", []):
        improvements.append(safety_item["feedback"])

    if not strengths:
        strengths.append(
            "Você concluiu todas as etapas do caso e apresentou um raciocínio "
            "que pode ser aperfeiçoado com a revisão abaixo."
        )

    outcome_matrix = rubric.get("desfechos_conduta")
    outcome_level = context.get("nivel_conduta", "parcial")

    if outcome_matrix:
        selected_outcome = outcome_matrix[outcome_level]
        patient_reaction = selected_outcome["reacao"]
        clinical_outcome = selected_outcome["desfecho"]
    elif score.conduta >= 24:
        reaction_context = (
            "Sua conduta contemplou os principais pilares previstos na rubrica. "
        )
        outcome_context = (
            "Com a execução adequada e reavaliação contínua, o desfecho esperado é: "
        )
        patient_reaction = reaction_context + rubric.get(
            "reacao_paciente_referencia",
            "A resposta do paciente depende da adequação e da segurança das medidas propostas.",
        )
        clinical_outcome = outcome_context + rubric.get(
            "desfecho_referencia",
            "O paciente deve ser reavaliado após a conduta inicial.",
        )
    elif score.conduta >= 12:
        reaction_context = (
            "Sua conduta tende a produzir resposta apenas parcial, pois ainda há "
            "medidas importantes ausentes. "
        )
        outcome_context = (
            "O desfecho permanece condicionado à correção das omissões apontadas: "
        )
        patient_reaction = reaction_context + rubric.get(
            "reacao_paciente_referencia",
            "A resposta do paciente depende das medidas propostas.",
        )
        clinical_outcome = outcome_context + rubric.get(
            "desfecho_referencia",
            "O paciente deve ser reavaliado.",
        )
    else:
        reaction_context = (
            "Com poucas medidas essenciais contempladas, o paciente mantém risco de "
            "não responder ou de apresentar deterioração. "
        )
        outcome_context = "Sem revisão imediata da conduta, o desfecho de referência fica comprometido: "
        patient_reaction = reaction_context + rubric.get(
            "reacao_paciente_referencia",
            "A resposta do paciente depende das medidas propostas.",
        )
        clinical_outcome = outcome_context + rubric.get(
            "desfecho_referencia",
            "O paciente deve ser reavaliado.",
        )

    safety_feedback = rubric.get(
        "feedback_seguranca",
        "Revise os sinais de gravidade e as medidas iniciais de segurança deste caso.",
    )
    if context.get("seguranca_ausente"):
        safety_feedback += " Omissões identificadas: " + " ".join(
            item["feedback"] for item in context["seguranca_ausente"]
        )

    rationales = build_exam_rationale_feedback(submission, context)
    omissions = []
    if exams.essenciais_ausentes:
        omissions.append(
            "Exames essenciais ausentes: " + ", ".join(exams.essenciais_ausentes) + "."
        )
    if context["condutas_ausentes"]:
        omissions.append(
            "Elementos ausentes na conduta: "
            + ", ".join(context["condutas_ausentes"])
            + "."
        )
    omissions.extend(item["feedback"] for item in context.get("seguranca_ausente", []))
    improvement_plan = [
        "Revisar a relação entre os achados do caso e o diagnóstico de referência.",
        "Treinar a seleção de exames perguntando se cada resultado mudaria a conduta.",
        "Reescrever a conduta em ordem de prioridade, incluindo segurança e reavaliação.",
    ]

    return ClinicalNarrative(
        resumo=(
            "Seu desempenho foi analisado pela Synapse com base "
            "no gabarito estruturado deste caso."
        ),
        sintese_raciocinio=(
            f"Você formulou a hipótese “{submission.hipotese_diagnostica.strip()}” e propôs "
            "uma conduta que foi comparada aos critérios clínicos e de segurança da rubrica."
        ),
        acertos=strengths,
        omissoes=omissions,
        exames_baixo_valor=exams.desnecessarios,
        pontos_melhoria=improvements,
        feedback_hipotese=(
            f"Diagnóstico de referência: {rubric['diagnostico_referencia']} "
            f"Sua resposta foi: {submission.hipotese_diagnostica.strip()}"
        ),
        feedback_conduta=(
            f"Conduta de referência: {rubric['conduta_referencia']} "
            f"Sua resposta foi: {submission.conduta_proposta.strip()}"
        ),
        feedback_seguranca=safety_feedback,
        reacao_paciente=patient_reaction,
        desfecho_clinico=clinical_outcome,
        justificativas_exames=rationales,
        plano_pessoal_melhoria=improvement_plan,
        recomendacoes_estudo=rubric["temas_estudo"],
    )


def enhance_narrative_with_ai(
    case: dict[str, Any],
    submission: SimulationSubmission,
    score: ScoreBreakdown,
    exams: ExamFeedback,
    context: dict[str, Any],
) -> tuple[ClinicalNarrative, Literal["openai", "agente_regras"], str | None]:
    fallback = build_rule_based_narrative(
        submission,
        score,
        exams,
        context,
    )
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback, "agente_regras", None

    model = os.getenv("OPENAI_MODEL", "gpt-5.6")
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        payload = {
            "caso": {
                "titulo": case["titulo"],
                "historia_clinica": case["historia_clinica"],
                "exame_fisico": case["exame_fisico"],
            },
            "respostas_do_estudante": submission.model_dump(),
            "pontuacao_objetiva": score.model_dump(),
            "avaliacao_de_exames": exams.model_dump(),
            "gabarito_clinico": context["rubrica"],
        }
        response = client.responses.parse(
            model=model,
            input=[
                {
                    "role": "developer",
                    "content": (
                        "Você é o Agente Avaliador Clínico da MedSync. Produza "
                        "feedback educacional, objetivo, respeitoso e em português "
                        "brasileiro. Use somente o caso, o gabarito e a pontuação "
                        "fornecidos. Não altere notas, não invente dados e não revele "
                        "raciocínio interno. Diferencie erro, omissão e alternativa "
                        "clinicamente aceitável. Personalize reacao_paciente e "
                        "desfecho_clinico comparando a conduta enviada exclusivamente "
                        "com as referências fornecidas; não invente evolução, tratamento "
                        "ou prognóstico. Se a resposta do estudante estiver "
                        "fora do tema, explique isso diretamente. Avalie as "
                        "justificativas dos exames somente contra justificativa_exames "
                        "da rubrica; preserve como nao_justificada quando ausente. "
                        "Organize obrigatoriamente síntese, acertos, omissões, exames "
                        "de baixo valor, hipótese, conduta, segurança, reação, desfecho "
                        "e plano pessoal de melhoria."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(payload, ensure_ascii=False),
                },
            ],
            text_format=ClinicalNarrative,
        )
        if response.output_parsed is None:
            return fallback, "agente_regras", None
        return response.output_parsed, "openai", model
    except Exception:
        logger.exception(
            "Falha ao gerar feedback clínico com OpenAI usando o modelo %s",
            model,
        )
        return fallback, "agente_regras", None


def answer_simulation_question(
    *,
    question: str,
    case: dict[str, Any],
    submission: dict[str, Any],
    evaluation: dict[str, Any],
    rubric: dict[str, Any],
) -> SimulationQuestionResponse:
    normalized = _normalize(question)
    exam_feedback = evaluation.get("exames", {})
    narrative = evaluation.get("feedback", {})

    if "desnecess" in normalized or "baixo valor" in normalized:
        low_value = exam_feedback.get("desnecessarios", [])
        if low_value:
            references = rubric.get("justificativa_exames", {})
            names = _exam_name_map(case)
            details = []
            for exam_id in submission.get("exames_solicitados", []):
                if names.get(exam_id) in low_value:
                    details.append(references.get(exam_id, names[exam_id]))
            fallback_answer = " ".join(details) or exam_feedback.get("comentario", "")
        else:
            fallback_answer = "Você não solicitou exames classificados como de baixo valor nesta rubrica."
    elif "instavel" in normalized or "instabilidade" in normalized:
        fallback_answer = (
            "Em uma deterioração simulada, priorize os critérios de segurança da rubrica: "
            + rubric.get(
                "feedback_seguranca", "reconhecer gravidade, estabilizar e reavaliar."
            )
            + " Conduta de referência: "
            + rubric.get("conduta_referencia", "não informada")
        )
    elif "diferenc" in normalized or "diagnostico" in normalized:
        fallback_answer = (
            f"O diagnóstico de referência é {rubric['diagnostico_referencia']} "
            "Diferencie-o relacionando história, exame físico e resultados que realmente mudam a probabilidade diagnóstica. "
            + narrative.get("feedback_hipotese", "")
        )
    else:
        fallback_answer = (
            narrative.get("sintese_raciocinio")
            or narrative.get("resumo")
            or "Revise a hipótese, a conduta e os critérios de segurança mostrados no resultado."
        )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return SimulationQuestionResponse(
            resposta=fallback_answer,
            fonte_feedback="agente_regras",
        )

    model = os.getenv("OPENAI_MODEL", "gpt-5.6")
    try:
        from openai import OpenAI

        payload = {
            "pergunta": question,
            "caso": {
                "titulo": case["titulo"],
                "historia_clinica": case["historia_clinica"],
                "exame_fisico": case["exame_fisico"],
            },
            "respostas_estudante": submission,
            "resultado": evaluation,
            "rubrica_revisada": rubric,
        }
        response = OpenAI(api_key=api_key).responses.create(
            model=model,
            store=False,
            instructions=(
                "Você é a Synapse, tutora educacional da MedSync. Responda em português "
                "brasileiro, de modo direto e didático, usando exclusivamente o caso, a "
                "rubrica e o resultado fornecidos. Não invente sinais vitais, evolução, "
                "diagnósticos, condutas ou prognósticos. Não dê orientação para pacientes "
                "reais. Se algo não estiver informado, diga 'não informado'."
            ),
            input=json.dumps(payload, ensure_ascii=False),
        )
        answer = (response.output_text or "").strip()
        if not answer:
            raise ValueError("Resposta vazia da Synapse.")
        return SimulationQuestionResponse(
            resposta=answer,
            fonte_feedback="openai",
            modelo_ia=model,
        )
    except Exception:
        logger.exception(
            "Falha ao responder pergunta pós-simulação com o modelo %s", model
        )
        return SimulationQuestionResponse(
            resposta=fallback_answer,
            fonte_feedback="agente_regras",
        )
