from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
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
    import json
    from models import ExamQuestion
    from routers.questions import (
        CATALOG_METADATA_CACHE_FILE,
        get_active_catalog_version,
    )

    dialect = db.get_bind().dialect.name
    cache_exists = CATALOG_METADATA_CACHE_FILE.is_file()
    if cache_exists:
        try:
            with open(CATALOG_METADATA_CACHE_FILE, encoding="utf-8") as f:
                cdata = json.load(f)
                total_v1 = cdata.get("v1", {}).get("total", 2811)
                total_v2 = cdata.get("v2", {}).get("total", 226792)
        except Exception:
            total_v1 = 2811
            total_v2 = 226792
    else:
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
        "cache_active": cache_exists,
    }



@router.post("/sistema/catalogo/batch")
async def sync_catalog_questions(
    fastapi_request: Request,
    db: Session = Depends(get_db),
):
    import gzip
    import json
    import os
    from datetime import UTC, datetime
    from models import ExamQuestion

    secret = fastapi_request.headers.get("X-Migration-Secret")
    expected = os.getenv(
        "MIGRATION_SECRET_KEY", "medsync-secret-catalog-v2-sync-token-2026"
    )
    if not secret or secret != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado.",
        )

    raw_body = await fastapi_request.body()
    if fastapi_request.headers.get("content-encoding") == "gzip":
        try:
            raw_body = gzip.decompress(raw_body)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro descompactando gzip: {e}",
            )

    try:
        data = json.loads(raw_body.decode("utf-8"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro decodificando JSON: {e}",
        )

    questions = data.get("questions", [])
    if not questions:
        return {"inserted": 0, "status": "empty"}

    for q in questions:
        if isinstance(q.get("alternativas"), str):
            try:
                q["alternativas"] = json.loads(q["alternativas"])
            except Exception:
                pass
        if isinstance(q.get("explicacao"), str) and q["explicacao"]:
            try:
                q["explicacao"] = json.loads(q["explicacao"])
            except Exception:
                pass
        for dt_col in ("created_at", "updated_at"):
            val = q.get(dt_col)
            if isinstance(val, str):
                try:
                    q[dt_col] = datetime.fromisoformat(val)
                except Exception:
                    q[dt_col] = datetime.now(UTC)
            elif val is None:
                q[dt_col] = datetime.now(UTC)

    dialect = db.get_bind().dialect.name
    if dialect == "postgresql":
        from sqlalchemy.dialects.postgresql import insert as pg_insert

        stmt = pg_insert(ExamQuestion).values(questions)
        stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
        db.execute(stmt)
    else:
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert

        stmt = sqlite_insert(ExamQuestion).values(questions)
        stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
        db.execute(stmt)

    db.commit()

    total_v2 = (
        db.scalar(
            select(func.count(ExamQuestion.id)).where(
                ExamQuestion.catalog_version == "v2"
            )
        )
        or 0
    )

    return {
        "inserted": len(questions),
        "total_v2_in_db": total_v2,
        "status": "success",
    }


