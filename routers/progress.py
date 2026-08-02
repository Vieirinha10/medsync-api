from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from database import get_db
from models import Progresso, User
from schemas import ProgressoCreate, ProgressoResetResponse, ProgressoResponse
from security import get_current_user
from services.clinical_content import get_published_case

router = APIRouter(prefix="/progresso", tags=["Progresso do Usuário"])


@router.post(
    "/registrar", response_model=ProgressoResponse, status_code=status.HTTP_201_CREATED
)
def registrar_progresso(
    progresso: ProgressoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if get_published_case(db, progresso.id_caso) is None:
        raise HTTPException(status_code=404, detail="Caso não encontrado.")
    entry = Progresso(id_usuario=current_user.id, **progresso.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/meu", response_model=list[ProgressoResponse])
def obter_meu_progresso(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(Progresso)
        .where(Progresso.id_usuario == current_user.id)
        .order_by(Progresso.id.desc())
    ).all()


@router.delete("/meu", response_model=ProgressoResetResponse)
def resetar_meu_progresso(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = db.execute(
        delete(Progresso).where(Progresso.id_usuario == current_user.id)
    )
    db.commit()
    return {
        "registros_removidos": result.rowcount or 0,
        "message": "Estatísticas redefinidas com sucesso.",
    }
