from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, inspect, select, text
from sqlalchemy.orm import Session

from database import get_db
from models import User
from settings import admin_emails

router = APIRouter(tags=["Sistema"])


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.get("/estatisticas-publicas")
def public_stats(response: Response, db: Session = Depends(get_db)):
    query = select(func.count()).select_from(User)
    excluded_admins = admin_emails()
    if excluded_admins:
        query = query.where(func.lower(User.email).not_in(excluded_admins))

    response.headers["Cache-Control"] = "public, max-age=300"
    return {"estudantes_medsync": db.scalar(query) or 0}


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    inspector = inspect(db.get_bind())
    required_tables = {"visual_challenges", "announcements", "user_activities"}
    missing_tables = required_tables.difference(inspector.get_table_names())
    user_columns = {column["name"] for column in inspector.get_columns("users")}
    case_columns = {
        column["name"] for column in inspector.get_columns("clinical_cases")
    }
    if (
        missing_tables
        or "last_login_at" not in user_columns
        or "is_premium" not in case_columns
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco de dados aguardando migração.",
        )
    return {"status": "ready", "database": "ok"}


@router.get("/sistema/info")
def system_info(db: Session = Depends(get_db)):
    from models import ExamQuestion
    from routers.questions import get_active_catalog_version

    dialect = db.get_bind().dialect.name
    total_v1 = (
        db.scalar(
            select(func.count(ExamQuestion.id)).where(
                ExamQuestion.catalog_version == "v1"
            )
        )
        or 0
    )
    total_v2 = (
        db.scalar(
            select(func.count(ExamQuestion.id)).where(
                ExamQuestion.catalog_version == "v2"
            )
        )
        or 0
    )
    return {
        "database_dialect": dialect,
        "active_catalog": get_active_catalog_version(),
        "total_v1": total_v1,
        "total_v2": total_v2,
    }

