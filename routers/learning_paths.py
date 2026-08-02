from copy import deepcopy
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from learning_path_catalog import (
    LEARNING_PATHS,
    get_learning_activity,
    get_learning_path,
)
from models import LearningPathProgress, User
from schemas import LearningPathCompletion, LearningPathProgressResponse
from security import get_current_user

router = APIRouter(prefix="/trilhas", tags=["Trilhas de Aprendizagem"])


def _progress_map(db: Session, user_id: int) -> dict[tuple[str, str], LearningPathProgress]:
    entries = db.scalars(
        select(LearningPathProgress).where(
            LearningPathProgress.id_usuario == user_id
        )
    ).all()
    return {(entry.trilha_id, entry.atividade_id): entry for entry in entries}


@router.get("")
def list_learning_paths(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    progress = _progress_map(db, current_user.id)
    paths = deepcopy(LEARNING_PATHS)

    for path in paths:
        completed = 0
        total = 0
        total_best_score = 0
        for module in path["modulos"]:
            module_completed = 0
            for activity in module["atividades"]:
                total += 1
                entry = progress.get((path["id"], activity["id"]))
                activity["progresso"] = {
                    "concluida": entry is not None,
                    "tentativas": entry.tentativas if entry else 0,
                    "melhor_pontuacao": entry.melhor_pontuacao if entry else 0,
                    "concluido_em": entry.concluido_em if entry else None,
                }
                if entry is not None:
                    completed += 1
                    module_completed += 1
                    total_best_score += entry.melhor_pontuacao
            module["progresso"] = {
                "concluidas": module_completed,
                "total": len(module["atividades"]),
            }
        path["progresso"] = {
            "concluidas": completed,
            "total": total,
            "percentual": round((completed / total) * 100) if total else 0,
            "media_melhores_notas": round(total_best_score / completed)
            if completed
            else 0,
        }
    return paths


@router.post(
    "/{path_id}/atividades/{activity_id}/concluir",
    response_model=LearningPathProgressResponse,
)
def complete_learning_activity(
    path_id: str,
    activity_id: str,
    completion: LearningPathCompletion,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    path = get_learning_path(path_id)
    if path is None:
        raise HTTPException(status_code=404, detail="Trilha não encontrada.")
    activity = get_learning_activity(path, activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Atividade não encontrada na trilha.")

    entry = db.scalar(
        select(LearningPathProgress).where(
            LearningPathProgress.id_usuario == current_user.id,
            LearningPathProgress.trilha_id == path_id,
            LearningPathProgress.atividade_id == activity_id,
        )
    )
    now = datetime.now(UTC)
    if entry is None:
        entry = LearningPathProgress(
            id_usuario=current_user.id,
            trilha_id=path_id,
            atividade_id=activity_id,
            tipo_atividade=activity["tipo"],
            tentativas=1,
            melhor_pontuacao=completion.pontuacao,
            concluido_em=now,
            ultima_tentativa_em=now,
        )
        db.add(entry)
    else:
        entry.tentativas += 1
        entry.melhor_pontuacao = max(
            entry.melhor_pontuacao, completion.pontuacao
        )
        entry.ultima_tentativa_em = now

    db.commit()
    db.refresh(entry)
    return entry
