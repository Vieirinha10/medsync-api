from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from challenge_answers import BUILTIN_CHALLENGE_ANSWERS, BUILTIN_CHALLENGE_SOURCES
from database import get_db
from models import Announcement, User, VisualChallenge
from schemas import (
    AnnouncementResponse,
    VisualChallengeAnswerRequest,
    VisualChallengeAnswerResponse,
)
from security import get_current_user

router = APIRouter(tags=["Conteúdo dinâmico"])


def serialize_admin_challenge(challenge: VisualChallenge) -> dict:
    alternatives = challenge.alternativas
    correct_index = next(
        (
            index
            for index, option in enumerate(alternatives)
            if option["id"] == challenge.alternativa_correta_id
        ),
        0,
    )
    return {
        "id": challenge.id,
        "titulo": challenge.titulo,
        "especialidade": challenge.especialidade,
        "dificuldade": challenge.dificuldade,
        "modalidade": challenge.modalidade,
        "pergunta": challenge.pergunta,
        "imagem_url": challenge.imagem_url,
        "imagem_alt": challenge.imagem_alt,
        "alternativas": [option["texto"] for option in alternatives],
        "alternativa_correta": correct_index,
        "diagnostico_correto": challenge.diagnostico_correto,
        "explicacao": challenge.explicacao,
        "achados_chave": challenge.achados_chave,
        "fonte_credito": challenge.fonte_credito,
        "fonte_licenca": challenge.fonte_licenca,
        "fonte_url": challenge.fonte_url,
        "status": challenge.status,
        "created_at": challenge.created_at,
        "updated_at": challenge.updated_at,
    }


def serialize_public_challenge(challenge: VisualChallenge) -> dict:
    return {
        "id": challenge.id,
        "especialidade": challenge.especialidade,
        "dificuldade": challenge.dificuldade,
        "modalidade": challenge.modalidade,
        "pergunta": challenge.pergunta,
        "imagem_url": challenge.imagem_url,
        "imagem_alt": challenge.imagem_alt,
        "alternativas": challenge.alternativas,
        "status": challenge.status,
    }


@router.get("/desafios-visuais")
def list_dynamic_challenges(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    challenges = db.scalars(
        select(VisualChallenge)
        .where(VisualChallenge.status == "publicado")
        .order_by(VisualChallenge.created_at.desc())
    ).all()
    return [serialize_public_challenge(challenge) for challenge in challenges]


@router.post(
    "/desafios-visuais/{challenge_id}/responder",
    response_model=VisualChallengeAnswerResponse,
)
def answer_visual_challenge(
    challenge_id: str,
    payload: VisualChallengeAnswerRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    challenge = db.get(VisualChallenge, challenge_id)
    if challenge is not None and challenge.status == "publicado":
        valid_ids = {option["id"] for option in challenge.alternativas}
        if payload.alternativa_id not in valid_ids:
            raise HTTPException(status_code=422, detail="Alternativa inválida.")
        return {
            "correta": payload.alternativa_id == challenge.alternativa_correta_id,
            "alternativa_correta_id": challenge.alternativa_correta_id,
            "diagnostico_correto": challenge.diagnostico_correto,
            "explicacao": challenge.explicacao,
            "achados_chave": challenge.achados_chave,
            "fonte_credito": challenge.fonte_credito,
            "fonte_licenca": challenge.fonte_licenca,
            "fonte_url": challenge.fonte_url,
        }

    answer = BUILTIN_CHALLENGE_ANSWERS.get(challenge_id)
    if answer is None:
        raise HTTPException(status_code=404, detail="Desafio não encontrado.")
    source_credit, source_license, source_url = BUILTIN_CHALLENGE_SOURCES[challenge_id]
    return {
        "correta": payload.alternativa_id == answer["correct_option_id"],
        "alternativa_correta_id": answer["correct_option_id"],
        "diagnostico_correto": answer["diagnosis"],
        "explicacao": answer["explanation"],
        "achados_chave": answer["key_findings"],
        "fonte_credito": source_credit,
        "fonte_licenca": source_license,
        "fonte_url": source_url,
    }


@router.get("/avisos", response_model=list[AnnouncementResponse])
def list_active_announcements(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.now(UTC)
    return db.scalars(
        select(Announcement)
        .where(
            Announcement.ativo.is_(True),
            Announcement.inicia_em <= now,
            or_(Announcement.termina_em.is_(None), Announcement.termina_em >= now),
        )
        .order_by(Announcement.created_at.desc())
    ).all()
