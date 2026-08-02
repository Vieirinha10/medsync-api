from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from database import get_db
from models import Announcement, User, VisualChallenge
from schemas import AnnouncementResponse
from security import get_current_user

router = APIRouter(tags=["Conteúdo dinâmico"])


def serialize_challenge(challenge: VisualChallenge) -> dict:
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
    return [serialize_challenge(challenge) for challenge in challenges]


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
