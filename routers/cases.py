from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import CasoClinico, CasoClinicoDetalhes
from security import get_current_user
from services.activity import track_activity
from services.clinical_content import (
    get_published_case,
    list_published_cases,
    serialize_case,
)

router = APIRouter(prefix="/casos-clinicos", tags=["Casos Clínicos"])


@router.get("/", response_model=list[CasoClinico])
def listar_casos_clinicos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return [
        serialize_case(case, include_details=False) for case in list_published_cases(db)
    ]


@router.get("/{caso_id}", response_model=CasoClinicoDetalhes)
def obter_caso_clinico(
    caso_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = get_published_case(db, caso_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    track_activity(db, current_user.id, "visualizacao", "caso_clinico", caso_id)
    db.commit()
    return serialize_case(case)
