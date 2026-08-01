import json
import logging
import os
import re
import unicodedata
from typing import Any, Literal

from pydantic import BaseModel, Field

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
    recomendacoes_estudo: list[str]


class SimulationEvaluation(BaseModel):
    progresso_id: int
    caso_id: int
    caso_titulo: str
    pontuacao_total: int = Field(ge=0, le=100)
    pontuacao: ScoreBreakdown
    exames: ExamFeedback
    feedback: ClinicalNarrative
    fonte_feedback: Literal["openai", "agente_regras"]
    modelo_ia: str | None = None
    aviso_educacional: str = (
        "Feedback destinado exclusivamente ao treinamento acadêmico. "
        "Não substitui protocolos locais, supervisão docente ou decisão médica real."
    )


PILOT_RUBRICS: dict[int, dict[str, Any]] = {
    8: {
        "diagnostico_referencia": (
            "Tromboembolismo pulmonar agudo associado a trombose venosa do membro "
            "superior esquerdo em paciente com câncer."
        ),
        "diagnostico_termos": [
            "tromboembolismo pulmonar",
            "embolia pulmonar",
            "tep",
        ],
        "diagnostico_parcial": [
            "trombose venosa",
            "trombose",
        ],
        "exames_essenciais": ["angiotc", "doppler_mmss", "gaso"],
        "exames_opcionais": [],
        "exames_desnecessarios": ["dimerod"],
        "justificativa_exames": {
            "angiotc": (
                "Confirma o tromboembolismo pulmonar e demonstra a falha de enchimento."
            ),
            "doppler_mmss": (
                "Investiga a provável fonte trombótica diante do membro superior "
                "edemaciado, hiperemiado e doloroso."
            ),
            "gaso": (
                "Ajuda a avaliar a repercussão respiratória em uma paciente com "
                "saturação de 83%."
            ),
            "dimerod": (
                "Tem pouca utilidade para excluir TEP neste cenário de alta "
                "probabilidade clínica, câncer ativo e hipoxemia importante."
            ),
        },
        "conduta_criterios": [
            {
                "nome": "Estabilização e oxigenoterapia",
                "pontos": 8,
                "termos": [
                    "oxigenio",
                    "oxigenoterapia",
                    "suporte ventilatorio",
                    "abc",
                    "estabilizacao",
                ],
            },
            {
                "nome": "Anticoagulação",
                "pontos": 12,
                "termos": [
                    "anticoagulacao",
                    "heparina",
                    "enoxaparina",
                    "anticoagulante",
                ],
            },
            {
                "nome": "Estratificação de risco",
                "pontos": 6,
                "termos": [
                    "estratificacao de risco",
                    "estabilidade hemodinamica",
                    "instabilidade hemodinamica",
                    "reperfusao",
                    "trombolise",
                ],
            },
            {
                "nome": "Internação e monitorização",
                "pontos": 4,
                "termos": [
                    "internacao",
                    "monitorizacao",
                    "monitoramento",
                    "hospitalar",
                ],
            },
        ],
        "conduta_referencia": (
            "Estabilizar pelo ABC, ofertar oxigênio e monitorizar; iniciar "
            "anticoagulação se não houver contraindicação; estratificar o risco "
            "hemodinâmico para avaliar necessidade de reperfusão; manter acompanhamento "
            "hospitalar e abordar a trombose associada ao câncer."
        ),
        "temas_estudo": [
            "Escore de probabilidade pré-teste para TEP",
            "Indicações e limitações do D-dímero",
            "Estratificação de risco e tratamento do TEP",
        ],
    }
}


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
    elif _contains_any(
        submission.hipotese_diagnostica,
        rubric["diagnostico_parcial"],
    ):
        hypothesis_score = 15
    else:
        hypothesis_score = 0

    matched_conduct = []
    missing_conduct = []
    conduct_score = 0
    for criterion in rubric["conduta_criterios"]:
        if _contains_any(submission.conduta_proposta, criterion["termos"]):
            conduct_score += criterion["pontos"]
            matched_conduct.append(criterion["nome"])
        else:
            missing_conduct.append(criterion["nome"])

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
        "condutas_identificadas": matched_conduct,
        "condutas_ausentes": missing_conduct,
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
    if score.hipotese == 30:
        strengths.append("A hipótese principal está alinhada ao diagnóstico do caso.")
    elif score.hipotese == 15:
        improvements.append(
            "Você reconheceu o fenômeno trombótico, mas precisa explicitar o "
            "tromboembolismo pulmonar como hipótese principal."
        )
    else:
        improvements.append(
            "A hipótese não identificou o tromboembolismo pulmonar, diagnóstico "
            "mais provável diante da apresentação."
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

    if not strengths:
        strengths.append(
            "Você concluiu todas as etapas do caso e apresentou um raciocínio "
            "que pode ser aperfeiçoado com a revisão abaixo."
        )

    return ClinicalNarrative(
        resumo=(
            "Seu desempenho foi analisado pelo Agente Avaliador MedSync com base "
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
        feedback_seguranca=(
            "A hipoxemia importante exige estabilização e monitorização. A decisão "
            "sobre anticoagulação e reperfusão depende de contraindicações e da "
            "estabilidade hemodinâmica."
        ),
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
                        "clinicamente aceitável. Se a resposta do estudante estiver "
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
