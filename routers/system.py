from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from database import get_db

router = APIRouter(tags=["Sistema"])


@router.get("/health")
def health_check():
    return {"status": "ok"}


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
