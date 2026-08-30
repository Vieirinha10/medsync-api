import json
import logging
import os
import re
import time
import unicodedata
from functools import lru_cache
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from clinical_rubric_catalog import CLINICAL_RUBRIC_VERSION, CLINICAL_RUBRICS

logger = logging.getLogger(__name__)

MODEL_PRICING_USD_PER_MILLION = {
    "gpt-5.6": (4.0, 0.4, 20.0),
    "gpt-5.6-sol": (4.0, 0.4, 20.0),
    "gpt-5.6-terra": (2.0, 0.2, 12.0),
    "gpt-5.6-luna": (0.2, 0.02, 1.2),
}

DEFAULT_ROUTINE_MODEL = "gpt-5.6-luna"
DEFAULT_ADVANCED_MODEL = "gpt-5.6-terra"
DEFAULT_FEEDBACK_MAX_OUTPUT_TOKENS = 900
DEFAULT_QUESTION_MAX_OUTPUT_TOKENS = 450
DEFAULT_REASONING_EFFORT = "low"
SUPPORTED_REASONING_EFFORTS = {"none", "low", "medium", "high", "xhigh", "max"}

_SAFETY_QUESTION_TERMS = (
    "contraindic",
    "deterior",
    "emergenc",
    "instabil",
    "risco",
    "seguranca",
    "urgenc",
)

SYNAPSE_VOICE_GUIDE = (
    "Adote a voz de uma preceptora clínica atenta: acolhedora, clara e "
    "profissional. Reconheça primeiro uma decisão concreta e correta quando "
    "houver, explique seu significado clínico e apresente a correção como um "
    "próximo passo prático. Incentive sem elogios genéricos, infantilização ou "
    "entusiasmo artificial. Diante de risco ao paciente, seja calma, explícita "
    "e firme, sem suavizar a gravidade. Seja concisa e não repita a mesma "
    "informação em campos diferentes."
)

SYNAPSE_FEEDBACK_INSTRUCTIONS = (
    "Você é a camada de tutoria da Synapse na MedSync. A pontuação, os acertos, "
    "as omissões, a segurança e o impacto clínico já foram calculados pelo "
    "sistema e não devem ser refeitos. Produza apenas a síntese educacional, o "
    "feedback da hipótese e da conduta e até três próximos passos, em português "
    "brasileiro. "
    + SYNAPSE_VOICE_GUIDE
    + " Use somente o caso, o gabarito e a pontuação fornecidos. Não altere "
    "notas, não invente dados e não revele raciocínio interno. Diferencie erro, "
    "omissão e alternativa clinicamente aceitável. Na síntese, siga a sequência "
    "reconhecimento específico, significado clínico e próximo passo. Não copie "
    "integralmente as respostas do estudante nem o gabarito. Não invente "
    "evolução, tratamento ou prognóstico. Se a resposta estiver fora do tema, "
    "explique isso diretamente. Diante de uma omissão de segurança, mantenha a "
    "prioridade indicada pelo sistema e não a suavize."
)

SYNAPSE_QUESTION_INSTRUCTIONS = (
    "Você é a Synapse, tutora educacional da MedSync. Responda em português "
    "brasileiro. "
    + SYNAPSE_VOICE_GUIDE
    + " Responda primeiro à dúvida, explique brevemente o motivo clínico e "
    "finalize com um próximo passo aplicável ao estudo deste caso. Use "
    "exclusivamente o caso, a rubrica e o resultado fornecidos. Não invente "
    "sinais vitais, evolução, diagnósticos, condutas ou prognósticos. Não dê "
    "orientação para pacientes reais. Se algo não estiver informado, diga 'não "
    "informado'."
)


class AIUsageMetrics(BaseModel):
    input_tokens: int = Field(ge=0)
    cached_input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(ge=0)
    reasoning_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(ge=0)
    duracao_ms: int = Field(ge=0)
    custo_estimado_usd: float | None = Field(default=None, ge=0)
    response_id: str | None = None


@lru_cache(maxsize=1)
def _openai_client(api_key: str):
    """Mantém um único cliente e pool HTTP por processo do Gunicorn."""

    from openai import OpenAI

    return OpenAI(
        api_key=api_key,
        timeout=float(os.getenv("OPENAI_TIMEOUT_SECONDS", "40")),
        max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "0")),
    )


def _nested_value(value: Any, *names: str, default: Any = None) -> Any:
    current = value
    for name in names:
        if current is None:
            return default
        if isinstance(current, dict):
            current = current.get(name)
        else:
            current = getattr(current, name, None)
    return default if current is None else current


def _bounded_env_int(
    name: str,
    default: int,
    *,
    minimum: int,
    maximum: int,
) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        logger.warning("Valor inválido em %s; usando %s.", name, default)
        return default
    return min(maximum, max(minimum, value))


def synapse_runtime_config() -> dict[str, Any]:
    """Expõe somente a configuração operacional segura para telemetria/admin."""

    routine_model = (os.getenv("OPENAI_ROUTINE_MODEL") or DEFAULT_ROUTINE_MODEL).strip()
    advanced_model = (
        os.getenv("OPENAI_ADVANCED_MODEL")
        or os.getenv("OPENAI_MODEL")
        or DEFAULT_ADVANCED_MODEL
    ).strip()
    question_override = os.getenv("OPENAI_SIMULATION_QUESTION_MODEL", "").strip()
    reasoning_effort = (
        os.getenv("OPENAI_REASONING_EFFORT", DEFAULT_REASONING_EFFORT).strip().lower()
    )
    if reasoning_effort not in SUPPORTED_REASONING_EFFORTS:
        logger.warning(
            "Valor inválido em OPENAI_REASONING_EFFORT; usando %s.",
            DEFAULT_REASONING_EFFORT,
        )
        reasoning_effort = DEFAULT_REASONING_EFFORT
    return {
        "modelo_rotina": routine_model,
        "modelo_avancado": advanced_model,
        "modelo_perguntas": question_override or routine_model,
        "perguntas_com_roteamento_automatico": not bool(question_override),
        "esforco_raciocinio": reasoning_effort,
        "limite_saida_feedback": _bounded_env_int(
            "OPENAI_FEEDBACK_MAX_OUTPUT_TOKENS",
            DEFAULT_FEEDBACK_MAX_OUTPUT_TOKENS,
            minimum=400,
            maximum=1600,
        ),
        "limite_saida_pergunta": _bounded_env_int(
            "OPENAI_QUESTION_MAX_OUTPUT_TOKENS",
            DEFAULT_QUESTION_MAX_OUTPUT_TOKENS,
            minimum=200,
            maximum=800,
        ),
    }


def _price_rates(model: str) -> tuple[float, float, float] | None:
    default = MODEL_PRICING_USD_PER_MILLION.get(model)
    configured = (
        os.getenv("OPENAI_INPUT_USD_PER_1M"),
        os.getenv("OPENAI_CACHED_INPUT_USD_PER_1M"),
        os.getenv("OPENAI_OUTPUT_USD_PER_1M"),
    )
    if all(value not in {None, ""} for value in configured):
        return tuple(float(value) for value in configured)  # type: ignore[return-value]
    return default


def _usage_metrics(
    response: Any, model: str, started_at: float
) -> AIUsageMetrics | None:
    usage = getattr(response, "usage", None)
    if usage is None:
        return None

    input_tokens = int(_nested_value(usage, "input_tokens", default=0))
    cached_tokens = int(
        _nested_value(
            usage,
            "input_tokens_details",
            "cached_tokens",
            default=0,
        )
    )
    output_tokens = int(_nested_value(usage, "output_tokens", default=0))
    reasoning_tokens = int(
        _nested_value(
            usage,
            "output_tokens_details",
            "reasoning_tokens",
            default=0,
        )
    )
    total_tokens = int(
        _nested_value(
            usage,
            "total_tokens",
            default=input_tokens + output_tokens,
        )
    )
    estimated_cost = None
    rates = _price_rates(model)
    if rates is not None:
        input_rate, cached_rate, output_rate = rates
        # A tabela oficial cobra contexto acima de 272 mil tokens com fatores
        # diferentes. Os prompts atuais ficam muito abaixo desse limite, mas o
        # cálculo permanece correto caso a entrada cresça no futuro.
        if input_tokens > 272_000:
            input_rate *= 2
            cached_rate *= 2
            output_rate *= 1.5
        uncached_tokens = max(0, input_tokens - cached_tokens)
        estimated_cost = round(
            (
                uncached_tokens * input_rate
                + cached_tokens * cached_rate
                + output_tokens * output_rate
            )
            / 1_000_000,
            8,
        )

    metrics = AIUsageMetrics(
        input_tokens=input_tokens,
        cached_input_tokens=cached_tokens,
        output_tokens=output_tokens,
        reasoning_tokens=reasoning_tokens,
        total_tokens=total_tokens,
        duracao_ms=round((time.perf_counter() - started_at) * 1000),
        custo_estimado_usd=estimated_cost,
        response_id=getattr(response, "id", None),
    )
    logger.info(
        "Synapse usage model=%s input_tokens=%s cached_input_tokens=%s "
        "output_tokens=%s reasoning_tokens=%s total_tokens=%s duration_ms=%s "
        "estimated_cost_usd=%s response_id=%s",
        model,
        metrics.input_tokens,
        metrics.cached_input_tokens,
        metrics.output_tokens,
        metrics.reasoning_tokens,
        metrics.total_tokens,
        metrics.duracao_ms,
        metrics.custo_estimado_usd,
        metrics.response_id,
    )
    return metrics


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


class SynapseNarrativeEnhancement(BaseModel):
    """Pequena camada gerativa aplicada sobre o feedback determinístico."""

    resumo: str = Field(min_length=10, max_length=420)
    sintese_raciocinio: str = Field(min_length=20, max_length=850)
    feedback_hipotese: str = Field(min_length=10, max_length=650)
    feedback_conduta: str = Field(min_length=10, max_length=700)
    plano_pessoal_melhoria: list[str] = Field(min_length=1, max_length=3)

    @model_validator(mode="after")
    def keep_improvement_steps_compact(self):
        if any(len(item) > 320 for item in self.plano_pessoal_melhoria):
            raise ValueError("Cada próximo passo deve ter no máximo 320 caracteres.")
        return self


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
    uso_ia: AIUsageMetrics | None = None
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
    uso_ia: AIUsageMetrics | None = None
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


_TERM_ALIASES: dict[str, tuple[str, ...]] = {
    "urgencia": (r"\burgenc\w*", r"\burgent\w*", r"\bemergenc\w*"),
    "internacao": (r"\bintern\w*", r"\bhospitaliz\w*"),
    "transfusao": (r"\b(?:hemo)?transfus\w*",),
    "estabilizacao": (r"\bestabiliz\w*",),
    "reavaliar": (r"\breavali\w*",),
    "acompanhamento": (r"\bacompanh\w*",),
}

_NEGATION_PATTERN = re.compile(
    r"\b(?:nao|nem|sem|dispens\w*|desnecessar\w*|evit\w*|"
    r"contraindic\w*|recus\w*|proib\w*|suspender|retirar|interromper|omitir)\b"
)
_ADVERSATIVE_PATTERN = re.compile(r"\b(?:mas|porem|contudo|entretanto|todavia)\b")


def _term_patterns(term: str) -> tuple[str, ...]:
    normalized = _normalize(term)
    aliases = _TERM_ALIASES.get(normalized)
    if aliases:
        return aliases
    return (rf"(?<!\w){re.escape(normalized)}(?!\w)",)


def _is_negated(text: str, occurrence_start: int) -> bool:
    prefix = text[:occurrence_start]
    boundary = max(prefix.rfind(marker) for marker in ".!?;:\n")
    clause = prefix[boundary + 1 :]
    adversatives = list(_ADVERSATIVE_PATTERN.finditer(clause))
    if adversatives:
        clause = clause[adversatives[-1].end() :]

    # Portuguese clinical prose frequently negates an entire coordinated list,
    # e.g. "não há necessidade de internação, transfusão ou avaliação urgente".
    # Twelve words cover that list without letting a negation leak across a sentence.
    recent_words = clause.split()[-12:]
    recent = " ".join(recent_words)
    if re.search(r"\bnao\s+(?:deixar|deixe)\s+de\b", recent):
        return False
    if re.search(r"\bsem\s+contraindic\w*(?:\s+\w+){0,4}\s*$", recent):
        return False
    return bool(_NEGATION_PATTERN.search(recent))


def _contains_any(text: str, terms: list[str]) -> bool:
    normalized = _normalize(text)
    for term in terms:
        for pattern in _term_patterns(term):
            for match in re.finditer(pattern, normalized):
                if not _is_negated(normalized, match.start()):
                    return True
    return False


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

    essential_points = (
        36 if not essential else round(36 * len(selected_essential) / len(essential))
    )
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
                    "Você registrou o motivo do pedido. Para deixá-lo mais "
                    f"clínico e verificável, compare-o com esta utilidade: {reference}"
                    if student_text
                    else (
                        "A justificativa era opcional e não foi informada. No próximo "
                        "caso, experimente registrar o que o resultado mudaria na sua "
                        f"decisão. Utilidade neste caso: {reference}"
                    )
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
    hypothesis_level = context["classificacao_hipotese"]
    conduct_level = context.get("nivel_conduta", "parcial")
    diagnosis = rubric["diagnostico_referencia"].strip().rstrip(".")
    matched_conduct = context["condutas_identificadas"]
    missing_conduct = context["condutas_ausentes"]
    missing_safety = context.get("seguranca_ausente", [])
    strengths: list[str] = []
    improvements: list[str] = []

    if exams.adequados:
        strengths.append(
            "Você selecionou exames pertinentes para confirmar a hipótese e avaliar "
            "a gravidade: " + ", ".join(exams.adequados) + "."
        )
    if hypothesis_level == "correta":
        strengths.append(
            "Você reconheceu corretamente o eixo diagnóstico central do caso."
        )
        hypothesis_feedback = (
            f"Você identificou corretamente {diagnosis}. Isso mostra que os achados "
            "centrais foram integrados de forma coerente. Mantenha essa lógica ao "
            "comparar as hipóteses diferenciais."
        )
    elif hypothesis_level == "parcial":
        rubric_hypothesis_feedback = rubric.get(
            "feedback_hipotese_parcial",
            "A hipótese reconheceu parte do quadro, mas precisa ser mais específica.",
        )
        improvements.append(rubric_hypothesis_feedback)
        hypothesis_feedback = (
            "Você identificou parte importante do padrão clínico. "
            f"{rubric_hypothesis_feedback} A formulação de referência é {diagnosis}. "
            "Para avançar, reúna os achados em uma hipótese mais específica."
        )
    else:
        rubric_hypothesis_feedback = rubric.get(
            "feedback_hipotese_incorreta",
            "A hipótese informada não corresponde ao diagnóstico de referência.",
        )
        improvements.append(rubric_hypothesis_feedback)
        hypothesis_feedback = (
            "A hipótese escolhida não explicou o eixo principal deste caso. "
            f"{rubric_hypothesis_feedback} A referência é {diagnosis}. No próximo "
            "caso, destaque primeiro os achados que mais aumentam ou reduzem a "
            "probabilidade de cada hipótese."
        )

    if matched_conduct:
        strengths.append(
            "Você levou o raciocínio para ações clinicamente relevantes: "
            + ", ".join(matched_conduct)
            + "."
        )

    if exams.essenciais_ausentes:
        improvements.append(
            "Inclua os exames essenciais que poderiam mudar a confirmação, a "
            "gravidade ou a segurança da conduta: "
            + ", ".join(exams.essenciais_ausentes)
            + "."
        )
    if exams.desnecessarios:
        improvements.append(
            "Antes de solicitar "
            + ", ".join(exams.desnecessarios)
            + ", confirme se o resultado realmente mudaria sua decisão neste caso."
        )
    if missing_conduct:
        improvements.append(
            "Complete a conduta com: " + ", ".join(missing_conduct) + "."
        )
    for safety_item in missing_safety:
        improvements.append(safety_item["feedback"])

    if not strengths:
        strengths.append(
            "Sua resposta permite localizar com clareza os pontos que precisam de "
            "revisão antes do próximo caso."
        )

    outcome_matrix = rubric.get("desfechos_conduta")

    if outcome_matrix:
        selected_outcome = outcome_matrix[conduct_level]
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

    rubric_safety_feedback = rubric.get(
        "feedback_seguranca",
        "Revise os sinais de gravidade e as medidas iniciais de segurança deste caso.",
    )
    if missing_safety:
        safety_feedback = (
            "Há um ponto importante de segurança para revisar antes de prosseguir. "
            + " ".join(item["feedback"] for item in missing_safety)
            + " Orientação da rubrica: "
            + rubric_safety_feedback
        )
    elif rubric.get("criterios_seguranca"):
        safety_feedback = (
            "Você contemplou os critérios de segurança rastreados neste caso. "
            + rubric_safety_feedback
        )
    else:
        safety_feedback = (
            "Mantenha como referência de segurança: " + rubric_safety_feedback
        )

    if conduct_level == "adequada":
        conduct_feedback = (
            "Você estruturou uma conduta consistente ao contemplar "
            + ", ".join(matched_conduct)
            + ". Esses são os principais pilares previstos para o caso."
        )
        if missing_conduct:
            conduct_feedback += (
                " Para refinar o plano, incorpore também "
                + ", ".join(missing_conduct)
                + "."
            )
        else:
            conduct_feedback += " Mantenha-os organizados por prioridade e reavaliação."
    elif matched_conduct:
        conduct_feedback = (
            "Você iniciou a condução por medidas pertinentes, incluindo "
            + ", ".join(matched_conduct)
            + ". Para tornar o plano mais completo, acrescente "
            + ", ".join(missing_conduct)
            + ". Referência do caso: "
            + rubric["conduta_referencia"]
        )
    else:
        conduct_feedback = (
            "A conduta ainda não contemplou os pilares centrais da rubrica. Comece "
            "organizando as prioridades em "
            + ", ".join(missing_conduct)
            + ". Referência do caso: "
            + rubric["conduta_referencia"]
        )

    if hypothesis_level == "correta" and conduct_level == "adequada":
        summary = (
            "Seu raciocínio foi consistente e conectou diagnóstico, investigação e "
            "conduta de forma segura."
        )
        reasoning_summary = (
            f"Você reconheceu corretamente o eixo central do caso: {diagnosis}. "
            "Também transformou esse reconhecimento em uma conduta alinhada aos "
            "principais critérios clínicos e de segurança. Use a análise a seguir "
            "para consolidar o que sustentou esse bom resultado."
        )
    elif hypothesis_level == "correta" and conduct_level == "insegura":
        summary = (
            "O diagnóstico foi bem reconhecido, mas há uma prioridade de segurança "
            "que precisa ser corrigida antes de prosseguir."
        )
        reasoning_summary = (
            f"Você reconheceu corretamente o eixo central do caso: {diagnosis}. "
            "Seu raciocínio diagnóstico foi bem direcionado. Agora, o ponto mais "
            "importante é transformar esse reconhecimento em um plano seguro, "
            "corrigindo primeiro a omissão destacada no alerta de segurança."
        )
    elif hypothesis_level == "correta":
        summary = (
            "Você reconheceu o problema central; o próximo ganho está em completar e "
            "priorizar a conduta."
        )
        reasoning_summary = (
            f"Você reconheceu corretamente o eixo central do caso: {diagnosis}. "
            "Seu raciocínio diagnóstico foi bem direcionado. O próximo passo é "
            "transformar esse reconhecimento em um plano mais específico, completo "
            "e seguro. Você já identificou o problema principal; agora vamos "
            "aprimorar como conduzi-lo."
        )
    elif hypothesis_level == "parcial":
        summary = (
            "Você construiu uma base clínica útil; o próximo passo é tornar a hipótese "
            "mais específica e conectá-la à conduta."
        )
        reasoning_summary = (
            "Você identificou parte importante do quadro e já tem uma base para "
            f"avançar. A referência deste caso é {diagnosis}. Reorganize os achados "
            "que melhor diferenciam essa hipótese e, em seguida, transforme-os em "
            "prioridades objetivas de investigação e conduta."
        )
    else:
        summary = (
            "O resultado mostra com clareza onde concentrar sua próxima revisão: "
            "reconhecer o padrão clínico antes de definir a conduta."
        )
        reasoning_summary = (
            "Sua hipótese ainda não reuniu os achados centrais do caso, mas o feedback "
            f"indica um caminho objetivo de revisão. A referência é {diagnosis}. "
            "Retome os dados de maior valor diagnóstico e use-os para justificar, em "
            "ordem, a investigação e a conduta."
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
    omissions.extend(item["feedback"] for item in missing_safety)

    improvement_plan = []
    if missing_safety:
        improvement_plan.append(
            "Antes de finalizar a conduta, faça uma checagem explícita de riscos, "
            "estabilização e reavaliação."
        )
    if hypothesis_level != "correta":
        improvement_plan.append(
            "Selecione os três achados que mais mudam a probabilidade diagnóstica e "
            "use-os para formular uma hipótese específica."
        )
    if exams.essenciais_ausentes or exams.desnecessarios:
        improvement_plan.append(
            "Justifique cada exame com uma pergunta simples: o resultado confirmará "
            "a hipótese, medirá gravidade ou mudará a conduta?"
        )
    if missing_conduct:
        improvement_plan.append(
            "Reescreva a conduta em ordem de prioridade, incluindo tratamento, "
            "segurança e critério de reavaliação."
        )
    if not improvement_plan:
        improvement_plan = [
            "Consolide este raciocínio explicando, em uma frase, por que cada exame "
            "escolhido poderia mudar a conduta.",
            "Treine a mesma sequência em um novo caso: reconhecer, priorizar, agir e "
            "reavaliar.",
        ]
    improvement_plan = improvement_plan[:3]

    return ClinicalNarrative(
        resumo=summary,
        sintese_raciocinio=reasoning_summary,
        acertos=strengths,
        omissoes=omissions,
        exames_baixo_valor=exams.desnecessarios,
        pontos_melhoria=improvements,
        feedback_hipotese=hypothesis_feedback,
        feedback_conduta=conduct_feedback,
        feedback_seguranca=safety_feedback,
        reacao_paciente=patient_reaction,
        desfecho_clinico=clinical_outcome,
        justificativas_exames=rationales,
        plano_pessoal_melhoria=improvement_plan,
        recomendacoes_estudo=rubric["temas_estudo"],
    )


def _compact_text(value: Any, max_chars: int) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


def _compact_case_payload(case: dict[str, Any]) -> dict[str, str]:
    return {
        "titulo": _compact_text(case.get("titulo"), 240),
        "dificuldade": _compact_text(case.get("nivel_dificuldade"), 40),
        "historia_clinica": _compact_text(case.get("historia_clinica"), 1800),
        "exame_fisico": _compact_text(case.get("exame_fisico"), 1200),
    }


def build_compact_feedback_payload(
    case: dict[str, Any],
    submission: SimulationSubmission,
    score: ScoreBreakdown,
    exams: ExamFeedback,
    context: dict[str, Any],
) -> dict[str, Any]:
    """Envia à IA apenas os dados necessários para a camada de tutoria."""

    rubric = context["rubrica"]
    selected_exams = []
    for exam_id in context["exames_selecionados"]:
        rationale = submission.justificativas_exames.get(exam_id)
        selected_exams.append(
            {
                "nome": context["nomes_exames"].get(exam_id, exam_id),
                "justificativa": (
                    _compact_text(rationale, 360) if rationale else "não informada"
                ),
            }
        )

    return {
        "caso": _compact_case_payload(case),
        "decisoes_estudante": {
            "exames": selected_exams,
            "hipotese": _compact_text(submission.hipotese_diagnostica, 900),
            "conduta": _compact_text(submission.conduta_proposta, 1800),
        },
        "avaliacao_objetiva": {
            "pontuacao": score.model_dump(),
            "classificacao_hipotese": context["classificacao_hipotese"],
            "nivel_conduta": context["nivel_conduta"],
            "exames_adequados": exams.adequados,
            "exames_essenciais_ausentes": exams.essenciais_ausentes,
            "exames_baixo_valor": exams.desnecessarios,
            "condutas_identificadas": context["condutas_identificadas"],
            "condutas_ausentes": context["condutas_ausentes"],
            "omissoes_seguranca": [
                {
                    "nome": item["nome"],
                    "feedback": _compact_text(item["feedback"], 500),
                }
                for item in context.get("seguranca_ausente", [])
            ],
        },
        "referencia_clinica": {
            "diagnostico": _compact_text(rubric["diagnostico_referencia"], 500),
            "conduta": _compact_text(rubric["conduta_referencia"], 1400),
            "feedback_hipotese_parcial": _compact_text(
                rubric.get("feedback_hipotese_parcial"), 500
            ),
            "feedback_hipotese_incorreta": _compact_text(
                rubric.get("feedback_hipotese_incorreta"), 500
            ),
            "feedback_seguranca": _compact_text(rubric.get("feedback_seguranca"), 650),
        },
    }


def build_compact_question_payload(
    *,
    question: str,
    case: dict[str, Any],
    submission: dict[str, Any],
    evaluation: dict[str, Any],
    rubric: dict[str, Any],
) -> dict[str, Any]:
    """Resume um resultado persistido sem reenviar a avaliação inteira."""

    exam_by_id = {exam["id"]: exam for exam in case.get("exames_disponiveis", [])}
    selected_ids = submission.get("exames_solicitados", [])
    selected_exams = [
        {
            "nome": exam_by_id.get(exam_id, {}).get("nome", exam_id),
            "resultado": _compact_text(
                exam_by_id.get(exam_id, {}).get("resultado", "não informado"), 500
            ),
        }
        for exam_id in selected_ids
    ]
    relevant_exam_ids = dict.fromkeys(
        [
            *selected_ids,
            *rubric.get("exames_essenciais", []),
            *rubric.get("exames_desnecessarios", []),
        ]
    )
    exam_reasons = {
        exam_by_id.get(exam_id, {}).get("nome", exam_id): _compact_text(reason, 500)
        for exam_id in relevant_exam_ids
        if (reason := rubric.get("justificativa_exames", {}).get(exam_id))
    }
    narrative = evaluation.get("feedback", {})
    outcome_matrix = rubric.get("desfechos_conduta") or {}
    current_outcome = outcome_matrix.get(evaluation.get("nivel_conduta", "parcial"), {})

    return {
        "pergunta": _compact_text(question, 500),
        "caso": _compact_case_payload(case),
        "decisoes_estudante": {
            "exames": selected_exams,
            "hipotese": _compact_text(submission.get("hipotese_diagnostica"), 900),
            "conduta": _compact_text(submission.get("conduta_proposta"), 1800),
        },
        "resultado_objetivo": {
            "pontuacao_total": evaluation.get("pontuacao_total"),
            "pontuacao": evaluation.get("pontuacao", {}),
            "nivel_conduta": evaluation.get("nivel_conduta"),
            "exames": evaluation.get("exames", {}),
            "resumo": _compact_text(narrative.get("resumo"), 420),
            "sintese": _compact_text(narrative.get("sintese_raciocinio"), 850),
            "feedback_hipotese": _compact_text(narrative.get("feedback_hipotese"), 650),
            "feedback_conduta": _compact_text(narrative.get("feedback_conduta"), 700),
            "feedback_seguranca": _compact_text(
                narrative.get("feedback_seguranca"), 700
            ),
            "proximos_passos": narrative.get("plano_pessoal_melhoria", [])[:3],
        },
        "referencia_clinica": {
            "diagnostico": _compact_text(rubric["diagnostico_referencia"], 500),
            "conduta": _compact_text(rubric["conduta_referencia"], 1400),
            "seguranca": _compact_text(rubric.get("feedback_seguranca"), 650),
            "utilidade_exames_relevantes": exam_reasons,
            "impacto_simulado_atual": current_outcome,
        },
    }


def select_feedback_model(
    case: dict[str, Any],
    score: ScoreBreakdown,
    context: dict[str, Any],
) -> str:
    config = synapse_runtime_config()
    if context.get("nivel_conduta") == "insegura":
        return config["modelo_avancado"]
    if context.get("classificacao_hipotese") == "parcial":
        return config["modelo_avancado"]

    difficulty = _normalize(str(case.get("nivel_dificuldade", "")))
    incomplete_complex_case = difficulty in {"dificil", "critico"} and (
        context.get("classificacao_hipotese") != "correta"
        or context.get("nivel_conduta") != "adequada"
        or score.exames < 28
    )
    return (
        config["modelo_avancado"]
        if incomplete_complex_case
        else config["modelo_rotina"]
    )


def select_question_model(question: str, evaluation: dict[str, Any]) -> str:
    config = synapse_runtime_config()
    if not config["perguntas_com_roteamento_automatico"]:
        return config["modelo_perguntas"]

    normalized = _normalize(question)
    needs_advanced_model = (
        evaluation.get("nivel_conduta") == "insegura"
        or len(question) > 260
        or any(term in normalized for term in _SAFETY_QUESTION_TERMS)
        or "diagnostico diferencial" in normalized
        or "alternativa aceitavel" in normalized
    )
    return (
        config["modelo_avancado"] if needs_advanced_model else config["modelo_rotina"]
    )


def enhance_narrative_with_ai(
    case: dict[str, Any],
    submission: SimulationSubmission,
    score: ScoreBreakdown,
    exams: ExamFeedback,
    context: dict[str, Any],
) -> tuple[
    ClinicalNarrative,
    Literal["openai", "agente_regras"],
    str | None,
    AIUsageMetrics | None,
]:
    fallback = build_rule_based_narrative(
        submission,
        score,
        exams,
        context,
    )
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback, "agente_regras", None, None

    config = synapse_runtime_config()
    model = select_feedback_model(case, score, context)
    try:
        client = _openai_client(api_key)
        payload = build_compact_feedback_payload(
            case,
            submission,
            score,
            exams,
            context,
        )
        started_at = time.perf_counter()
        response = client.responses.parse(
            model=model,
            store=False,
            max_output_tokens=config["limite_saida_feedback"],
            reasoning={"effort": config["esforco_raciocinio"]},
            verbosity="low",
            input=[
                {
                    "role": "developer",
                    "content": SYNAPSE_FEEDBACK_INSTRUCTIONS,
                },
                {
                    "role": "user",
                    "content": json.dumps(payload, ensure_ascii=False),
                },
            ],
            text_format=SynapseNarrativeEnhancement,
        )
        usage = _usage_metrics(response, model, started_at)
        if response.output_parsed is None:
            return (
                fallback,
                "agente_regras",
                model,
                usage,
            )
        enhanced = fallback.model_copy(
            update=response.output_parsed.model_dump(),
        )
        return (
            enhanced,
            "openai",
            model,
            usage,
        )
    except Exception:
        logger.exception(
            "Falha ao gerar feedback clínico com OpenAI usando o modelo %s",
            model,
        )
        return fallback, "agente_regras", None, None


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
            explanation = " ".join(details) or exam_feedback.get("comentario", "")
            fallback_answer = (
                "Vamos tornar essa escolha mais intencional. "
                + explanation
                + " No próximo caso, pergunte se o resultado mudaria a hipótese, a "
                "avaliação de gravidade ou a conduta."
            )
        else:
            fallback_answer = (
                "Neste caso, sua seleção não incluiu exames classificados como de "
                "baixo valor. Isso mostra uma investigação focada; mantenha o hábito "
                "de justificar o que cada resultado mudaria na decisão."
            )
    elif "instavel" in normalized or "instabilidade" in normalized:
        fallback_answer = (
            "Aqui, a prioridade é a segurança do paciente. Em uma deterioração "
            "simulada, siga primeiro estes critérios da rubrica: "
            + rubric.get(
                "feedback_seguranca", "reconhecer gravidade, estabilizar e reavaliar."
            )
            + " Depois, compare sua sequência com a conduta de referência: "
            + rubric.get("conduta_referencia", "não informada")
        )
    elif "diferenc" in normalized or "diagnostico" in normalized:
        fallback_answer = (
            f"A referência deste caso é {rubric['diagnostico_referencia']} Para "
            "diferenciá-la, reúna história, exame físico e resultados que realmente "
            "mudam a probabilidade diagnóstica. Como próximo passo, escolha os três "
            "achados mais discriminativos e explique como cada um sustenta a hipótese."
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

    config = synapse_runtime_config()
    model = select_question_model(question, evaluation)
    try:
        payload = build_compact_question_payload(
            question=question,
            case=case,
            submission=submission,
            evaluation=evaluation,
            rubric=rubric,
        )
        started_at = time.perf_counter()
        response = _openai_client(api_key).responses.create(
            model=model,
            store=False,
            max_output_tokens=config["limite_saida_pergunta"],
            reasoning={"effort": config["esforco_raciocinio"]},
            text={"verbosity": "low"},
            instructions=SYNAPSE_QUESTION_INSTRUCTIONS,
            input=json.dumps(payload, ensure_ascii=False),
        )
        usage = _usage_metrics(response, model, started_at)
        answer = (response.output_text or "").strip()
        if not answer:
            return SimulationQuestionResponse(
                resposta=fallback_answer,
                fonte_feedback="agente_regras",
                modelo_ia=model,
                uso_ia=usage,
            )
        return SimulationQuestionResponse(
            resposta=answer,
            fonte_feedback="openai",
            modelo_ia=model,
            uso_ia=usage,
        )
    except Exception:
        logger.exception(
            "Falha ao responder pergunta pós-simulação com o modelo %s", model
        )
        return SimulationQuestionResponse(
            resposta=fallback_answer,
            fonte_feedback="agente_regras",
        )
