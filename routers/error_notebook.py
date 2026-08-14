from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import StudyError, User
from schemas import (
    SpacedReviewCreate,
    SpacedReviewPlanItem,
    StudyErrorResponse,
    StudyErrorStatusUpdate,
    VisualChallengeAttempt,
)
from security import get_current_user
from services.activity import track_activity

router = APIRouter(prefix="/caderno-erros", tags=["Caderno de Erros"])

MAX_REVIEW_INTERVAL_DAYS = 180
REVIEW_RATINGS = ("errei", "dificil", "bom", "facil")


def calculate_review_outcome(entry: StudyError, rating: str) -> dict:
    previous_interval = entry.intervalo_dias
    ease_factor = entry.fator_facilidade
    sequence = entry.sequencia_acertos
    next_ease_factor = ease_factor

    if rating == "errei":
        interval = 1
        next_sequence = 0
        next_ease_factor = max(1.3, ease_factor - 0.2)
        next_status = "pendente"
    elif rating == "dificil":
        next_sequence = sequence + 1
        interval = (
            1 if not previous_interval else max(2, round(previous_interval * 1.5))
        )
        next_ease_factor = max(1.3, ease_factor - 0.15)
        next_status = "revisando"
    elif rating == "bom":
        next_sequence = sequence + 1
        sequence_intervals = {1: 1, 2: 7, 3: 15}
        interval = sequence_intervals.get(
            next_sequence,
            max(1, round(previous_interval * ease_factor)),
        )
        next_status = "dominado" if next_sequence >= 3 else "revisando"
    else:  # facil
        next_sequence = sequence + 1
        sequence_intervals = {1: 3, 2: 10, 3: 30}
        interval = sequence_intervals.get(
            next_sequence,
            max(1, round(previous_interval * (ease_factor + 0.3))),
        )
        next_ease_factor = min(3.0, ease_factor + 0.15)
        next_status = "dominado" if next_sequence >= 3 else "revisando"

    return {
        "intervalo_dias": min(interval, MAX_REVIEW_INTERVAL_DAYS),
        "sequencia_acertos": next_sequence,
        "fator_facilidade": next_ease_factor,
        "status": next_status,
    }


def build_review_forecasts(entry: StudyError, now: datetime) -> dict:
    forecasts = {}
    for rating in REVIEW_RATINGS:
        outcome = calculate_review_outcome(entry, rating)
        interval = outcome["intervalo_dias"]
        forecasts[rating] = {
            "intervalo_dias": interval,
            "proxima_revisao_em": now + timedelta(days=interval),
        }
    return forecasts


def schedule_review(
    entry: StudyError,
    rating: str,
    now: datetime | None = None,
) -> StudyError:
    """Aplica um agendamento simples e previsível inspirado no SM-2."""
    reviewed_at = now or datetime.now(UTC)
    outcome = calculate_review_outcome(entry, rating)
    entry.sequencia_acertos = outcome["sequencia_acertos"]
    entry.fator_facilidade = outcome["fator_facilidade"]
    entry.status = outcome["status"]
    entry.dominado_em = reviewed_at if entry.status == "dominado" else None
    entry.intervalo_dias = outcome["intervalo_dias"]
    entry.revisoes_realizadas += 1
    entry.ultima_revisao_em = reviewed_at
    entry.proxima_revisao_em = reviewed_at + timedelta(days=entry.intervalo_dias)
    return entry


def _find_error(
    db: Session,
    user_id: int,
    source_type: str,
    source_id: str,
) -> StudyError | None:
    return db.scalar(
        select(StudyError).where(
            StudyError.id_usuario == user_id,
            StudyError.tipo_origem == source_type,
            StudyError.id_origem == source_id,
        )
    )


def register_clinical_result(
    db: Session,
    user_id: int,
    case: dict,
    submission: dict,
    evaluation_data: dict,
) -> StudyError | None:
    now = datetime.now(UTC)
    existing = _find_error(db, user_id, "caso_clinico", str(case["id"]))
    total_score = evaluation_data["pontuacao_total"]
    mastered = total_score == 100

    if mastered:
        if existing is not None:
            existing.status = "dominado"
            existing.dominado_em = now
            existing.visto_ultimo_em = now
            existing.proxima_revisao_em = now + timedelta(days=30)
        return existing

    rubric = case.get("rubrica", {})
    correct_answer = (
        rubric.get("diagnostico_referencia") or "Consulte o feedback revisado."
    )
    details = {
        "pontuacao_total": total_score,
        "pontuacao": evaluation_data["pontuacao"],
        "exames": evaluation_data["exames"],
        "pontos_melhoria": evaluation_data["feedback"]["pontos_melhoria"],
        "recomendacoes_estudo": evaluation_data["feedback"]["recomendacoes_estudo"],
        "feedback_hipotese": evaluation_data["feedback"]["feedback_hipotese"],
        "feedback_conduta": evaluation_data["feedback"]["feedback_conduta"],
        "feedback_seguranca": evaluation_data["feedback"]["feedback_seguranca"],
        "reacao_paciente": evaluation_data["feedback"].get("reacao_paciente"),
        "desfecho_clinico": evaluation_data["feedback"].get("desfecho_clinico"),
        "nivel_conduta": evaluation_data.get("nivel_conduta"),
        "categorias_erro": {
            "exames_omitidos": evaluation_data["exames"]["essenciais_ausentes"],
            "exames_desnecessarios": evaluation_data["exames"]["desnecessarios"],
            "hipotese_incompleta": evaluation_data["pontuacao"]["hipotese"] < 30,
            "conduta_incompleta": evaluation_data["pontuacao"]["conduta"] < 30,
            "risco_seguranca": evaluation_data.get("nivel_conduta") == "insegura",
        },
    }

    if existing is None:
        existing = StudyError(
            id_usuario=user_id,
            tipo_origem="caso_clinico",
            id_origem=str(case["id"]),
            titulo=case["titulo"],
            especialidade=case["especialidade"],
            dificuldade=case.get("nivel_dificuldade"),
            pergunta="Raciocínio diagnóstico e conduta no caso clínico",
            resposta_usuario=submission.get("hipotese_diagnostica", "Não informada"),
            resposta_correta=correct_answer,
            explicacao=evaluation_data["feedback"]["resumo"],
            detalhes=details,
            status="pendente",
            quantidade_erros=1,
            visto_primeiro_em=now,
            visto_ultimo_em=now,
        )
        db.add(existing)
    else:
        existing.resposta_usuario = submission.get(
            "hipotese_diagnostica", "Não informada"
        )
        existing.resposta_correta = correct_answer
        existing.explicacao = evaluation_data["feedback"]["resumo"]
        existing.detalhes = details
        existing.status = "pendente"
        existing.quantidade_erros += 1
        existing.visto_ultimo_em = now
        existing.dominado_em = None
        existing.sequencia_acertos = 0
        existing.proxima_revisao_em = now

    return existing


@router.get("/meu", response_model=list[StudyErrorResponse])
def list_my_errors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(StudyError)
        .where(StudyError.id_usuario == current_user.id)
        .order_by(StudyError.visto_ultimo_em.desc(), StudyError.id.desc())
    ).all()


@router.get("/revisoes-hoje", response_model=list[StudyErrorResponse])
def list_due_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.now(UTC)
    return db.scalars(
        select(StudyError)
        .where(
            StudyError.id_usuario == current_user.id,
            StudyError.proxima_revisao_em <= now,
        )
        .order_by(
            StudyError.proxima_revisao_em.asc(),
            StudyError.quantidade_erros.desc(),
            StudyError.id.asc(),
        )
        .limit(30)
    ).all()


@router.get("/revisoes-plano", response_model=list[SpacedReviewPlanItem])
def list_review_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.now(UTC)
    entries = db.scalars(
        select(StudyError)
        .where(StudyError.id_usuario == current_user.id)
        .order_by(
            StudyError.proxima_revisao_em.asc(),
            StudyError.quantidade_erros.desc(),
            StudyError.id.asc(),
        )
    ).all()
    return [
        {
            **StudyErrorResponse.model_validate(entry).model_dump(),
            "previsoes": build_review_forecasts(entry, now),
        }
        for entry in entries
    ]


@router.post("/{error_id}/revisar", response_model=StudyErrorResponse)
def review_error(
    error_id: int,
    review: SpacedReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = db.scalar(
        select(StudyError).where(
            StudyError.id == error_id,
            StudyError.id_usuario == current_user.id,
        )
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="Erro de estudo não encontrado.")

    schedule_review(entry, review.avaliacao)
    db.commit()
    db.refresh(entry)
    return entry


@router.post(
    "/desafios",
    response_model=StudyErrorResponse | None,
    status_code=status.HTTP_200_OK,
)
def register_visual_challenge_attempt(
    attempt: VisualChallengeAttempt,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.now(UTC)
    track_activity(
        db,
        current_user.id,
        "resposta",
        "desafio_visual",
        attempt.desafio_id,
    )
    existing = _find_error(db, current_user.id, "desafio_visual", attempt.desafio_id)
    correct = attempt.resposta_usuario == attempt.resposta_correta

    if correct:
        if existing is None:
            db.commit()
            return None
        existing.status = "dominado"
        existing.dominado_em = now
        existing.visto_ultimo_em = now
        existing.proxima_revisao_em = now + timedelta(days=30)
        db.commit()
        db.refresh(existing)
        return existing

    details = {"imagem": attempt.imagem}
    if existing is None:
        existing = StudyError(
            id_usuario=current_user.id,
            tipo_origem="desafio_visual",
            id_origem=attempt.desafio_id,
            titulo=attempt.titulo,
            especialidade=attempt.especialidade,
            dificuldade=attempt.dificuldade,
            pergunta=attempt.pergunta,
            resposta_usuario=attempt.resposta_usuario,
            resposta_correta=attempt.resposta_correta,
            explicacao=attempt.explicacao,
            detalhes=details,
            status="pendente",
            quantidade_erros=1,
            visto_primeiro_em=now,
            visto_ultimo_em=now,
        )
        db.add(existing)
    else:
        existing.titulo = attempt.titulo
        existing.especialidade = attempt.especialidade
        existing.dificuldade = attempt.dificuldade
        existing.pergunta = attempt.pergunta
        existing.resposta_usuario = attempt.resposta_usuario
        existing.resposta_correta = attempt.resposta_correta
        existing.explicacao = attempt.explicacao
        existing.detalhes = details
        existing.status = "pendente"
        existing.quantidade_erros += 1
        existing.visto_ultimo_em = now
        existing.dominado_em = None
        existing.sequencia_acertos = 0
        existing.proxima_revisao_em = now

    db.commit()
    db.refresh(existing)
    return existing


@router.patch("/{error_id}/status", response_model=StudyErrorResponse)
def update_error_status(
    error_id: int,
    update: StudyErrorStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = db.scalar(
        select(StudyError).where(
            StudyError.id == error_id,
            StudyError.id_usuario == current_user.id,
        )
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="Erro de estudo não encontrado.")

    entry.status = update.status
    now = datetime.now(UTC)
    entry.dominado_em = now if update.status == "dominado" else None
    entry.proxima_revisao_em = (
        now + timedelta(days=30) if update.status == "dominado" else now
    )
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{error_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_error(
    error_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = db.scalar(
        select(StudyError).where(
            StudyError.id == error_id,
            StudyError.id_usuario == current_user.id,
        )
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="Erro de estudo não encontrado.")
    db.delete(entry)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
