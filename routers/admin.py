from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import AcademicAnalyticsResponse
from security import get_current_user
from settings import is_admin_email

router = APIRouter(prefix="/admin", tags=["Administração"])


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not is_admin_email(current_user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito aos administradores do MedSync.",
        )
    return current_user


def percentage(value: int, total: int) -> float:
    return round((value / total) * 100, 1) if total else 0.0


@router.get("/analytics/academico", response_model=AcademicAnalyticsResponse)
def academic_analytics(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    total_users = db.scalar(select(func.count(User.id))) or 0
    completed_profiles = (
        db.scalar(
            select(func.count(User.id)).where(
                User.periodo_curso.is_not(None),
                User.faculdade.is_not(None),
            )
        )
        or 0
    )
    new_users = (
        db.scalar(
            select(func.count(User.id)).where(
                User.created_at >= datetime.now(UTC) - timedelta(days=30)
            )
        )
        or 0
    )

    period_rows = db.execute(
        select(User.periodo_curso, func.count(User.id))
        .where(User.periodo_curso.is_not(None))
        .group_by(User.periodo_curso)
        .order_by(User.periodo_curso)
    ).all()

    normalized_faculty = func.lower(func.trim(User.faculdade))
    faculty_rows = db.execute(
        select(func.min(User.faculdade), func.count(User.id))
        .where(User.faculdade.is_not(None), func.trim(User.faculdade) != "")
        .group_by(normalized_faculty)
        .order_by(func.count(User.id).desc(), func.min(User.faculdade))
    ).all()

    return {
        "total_usuarios": total_users,
        "perfis_academicos_preenchidos": completed_profiles,
        "cobertura_percentual": percentage(completed_profiles, total_users),
        "novos_ultimos_30_dias": new_users,
        "periodos": [
            {
                "periodo": period,
                "total": count,
                "percentual": percentage(count, completed_profiles),
            }
            for period, count in period_rows
        ],
        "faculdades": [
            {
                "faculdade": faculty,
                "total": count,
                "percentual": percentage(count, completed_profiles),
            }
            for faculty, count in faculty_rows
        ],
    }
