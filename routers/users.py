from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import Token, UserCreate, UserLogin, UserResponse
from security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from services.activity import track_activity
from settings import is_admin_email

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


def user_response(user: User) -> dict[str, object]:
    return {
        "id": user.id,
        "nome": user.nome,
        "email": user.email,
        "periodo_curso": user.periodo_curso,
        "faculdade": user.faculdade,
        "is_admin": is_admin_email(user.email),
        "created_at": user.created_at,
    }


@router.post(
    "/registrar", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def registrar_usuario(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        nome=user.nome,
        email=str(user.email),
        periodo_curso=user.periodo_curso,
        faculdade=user.faculdade,
        password_hash=hash_password(user.password),
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado.",
        ) from None
    db.refresh(new_user)
    return user_response(new_user)


@router.post("/login", response_model=Token)
def login_usuario(form_data: UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(form_data.email)))
    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos.",
        )
    user.last_login_at = datetime.now(UTC)
    track_activity(db, user.id, "login")
    db.commit()
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def obter_usuario_atual(current_user: User = Depends(get_current_user)):
    return user_response(current_user)
