from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import StudyError, User
from schemas import (
    StudyErrorResponse,
    StudyErrorStatusUpdate,
    VisualChallengeAttempt,
)
from security import get_current_user

router = APIRouter(prefix="/caderno-erros", tags=["Caderno de Erros"])


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
        return existing

    rubric = case.get("rubrica", {})
    correct_answer = rubric.get("diagnostico_referencia") or "Consulte o feedback revisado."
    details = {
        "pontuacao_total": total_score,
        "pontuacao": evaluation_data["pontuacao"],
        "exames": evaluation_data["exames"],
        "pontos_melhoria": evaluation_data["feedback"]["pontos_melhoria"],
        "recomendacoes_estudo": evaluation_data["feedback"]["recomendacoes_estudo"],
        "feedback_hipotese": evaluation_data["feedback"]["feedback_hipotese"],
        "feedback_conduta": evaluation_data["feedback"]["feedback_conduta"],
        "feedback_seguranca": evaluation_data["feedback"]["feedback_seguranca"],
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
    existing = _find_error(
        db, current_user.id, "desafio_visual", attempt.desafio_id
    )
    correct = attempt.resposta_usuario == attempt.resposta_correta

    if correct:
        if existing is None:
            return None
        existing.status = "dominado"
        existing.dominado_em = now
        existing.visto_ultimo_em = now
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
    entry.dominado_em = datetime.now(UTC) if update.status == "dominado" else None
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
