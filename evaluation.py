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
    hipotese_diagnostica: str = Field(min_length=3, max_length=4000)
    conduta_proposta: str = Field(min_length=3, max_length=4000)


class ScoreBreakdown(BaseModel):
    exames: int = Field(ge=0, le=40)
    hipotese: int = Field(ge=0, le=30)
    conduta: int = Field(ge=0, le=30)


class ExamFeedback(BaseModel):
    adequados: list[str]
    essenciais_ausentes: list[str]
    desnecessarios: list[str]
    comentario: str


class ClinicalNarrative(BaseModel):
    resumo: str
    acertos: list[str]
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
        outcome_context = (
            "Sem revisão imediata da conduta, o desfecho de referência fica comprometido: "
        )
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

    return ClinicalNarrative(
        resumo=(
            "Seu desempenho foi analisado pela Synapse com base "
            "no gabarito estruturado deste caso."
        ),
        acertos=strengths,
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
                        "fora do tema, explique isso diretamente."
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
