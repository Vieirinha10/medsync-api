import hashlib
import logging
import os
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import (
    EmailVerificationRequest,
    EmailVerificationResend,
    MessageResponse,
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
)
from security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from services.activity import track_activity
from services.email import send_verification_email
from settings import is_admin_email

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

CURRENT_TERMS_VERSION = "2026-08-11"
CURRENT_PRIVACY_VERSION = "2026-08-11"
EMAIL_VERIFICATION_TTL_HOURS = int(os.getenv("EMAIL_VERIFICATION_TTL_HOURS", "24"))
EMAIL_RESEND_COOLDOWN_SECONDS = int(
    os.getenv("EMAIL_RESEND_COOLDOWN_SECONDS", "60")
)
GENERIC_RESEND_MESSAGE = (
    "Se houver uma conta pendente para este e-mail, enviaremos uma nova confirmação."
)
logger = logging.getLogger(__name__)


def _token_hash(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _verification_token() -> tuple[str, str, datetime]:
    raw_token = secrets.token_urlsafe(32)
    return (
        raw_token,
        _token_hash(raw_token),
        datetime.now(UTC) + timedelta(hours=EMAIL_VERIFICATION_TTL_HOURS),
    )


def _as_utc(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def user_response(user: User) -> dict[str, object]:
    entitlement = user.entitlement
    premium_expiry = entitlement.valido_ate if entitlement else None
    if premium_expiry and premium_expiry.tzinfo is None:
        premium_expiry = premium_expiry.replace(tzinfo=UTC)
    premium_active = bool(
        entitlement
        and entitlement.status == "ativo"
        and premium_expiry > datetime.now(UTC)
    )
    return {
        "id": user.id,
        "nome": user.nome,
        "email": user.email,
        "periodo_curso": user.periodo_curso,
        "faculdade": user.faculdade,
        "email_verificado": user.email_verified_at is not None,
        "is_admin": is_admin_email(user.email),
        "premium_ativo": premium_active,
        "premium_plano": entitlement.plano_id if premium_active else None,
        "premium_valido_ate": premium_expiry if premium_active else None,
        "created_at": user.created_at,
    }


@router.post(
    "/registrar", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def registrar_usuario(user: UserCreate, db: Session = Depends(get_db)):
    raw_token, token_hash, token_expiry = _verification_token()
    now = datetime.now(UTC)
    new_user = User(
        nome=user.nome,
        email=str(user.email),
        periodo_curso=user.periodo_curso,
        faculdade=user.faculdade,
        password_hash=hash_password(user.password),
        terms_accepted_at=datetime.now(UTC),
        terms_version=CURRENT_TERMS_VERSION,
        privacy_version=CURRENT_PRIVACY_VERSION,
        email_verification_token_hash=token_hash,
        email_verification_expires_at=token_expiry,
        email_verification_sent_at=now,
    )
    db.add(new_user)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado.",
        ) from None
    try:
        send_verification_email(
            email=new_user.email,
            nome=new_user.nome,
            raw_token=raw_token,
        )
    except Exception:
        db.rollback()
        logger.exception("Falha ao enviar confirmação para nova conta.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Não foi possível enviar o e-mail de confirmação agora. "
                "Tente criar a conta novamente em alguns instantes."
            ),
        ) from None
    db.commit()
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
    if user.email_verified_at is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Seu e-mail ainda não foi confirmado. "
                "Abra o link enviado pela MedSync ou solicite um novo envio."
            ),
        )
    user.last_login_at = datetime.now(UTC)
    track_activity(db, user.id, "login")
    db.commit()
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def obter_usuario_atual(current_user: User = Depends(get_current_user)):
    return user_response(current_user)


@router.post("/verificar-email", response_model=MessageResponse)
def verificar_email(payload: EmailVerificationRequest, db: Session = Depends(get_db)):
    now = datetime.now(UTC)
    user = db.scalar(
        select(User).where(
            User.email_verification_token_hash == _token_hash(payload.token)
        )
    )
    if (
        user is None
        or user.email_verified_at is not None
        or user.email_verification_expires_at is None
        or _as_utc(user.email_verification_expires_at) <= now
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O link de confirmação é inválido ou expirou.",
        )

    user.email_verified_at = now
    user.email_verification_token_hash = None
    user.email_verification_expires_at = None
    user.email_verification_sent_at = None
    db.commit()
    return {"message": "E-mail confirmado. Sua conta MedSync está pronta para uso."}


@router.post(
    "/reenviar-verificacao",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def reenviar_verificacao(
    payload: EmailVerificationResend,
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.email == str(payload.email)))
    if user is None or user.email_verified_at is not None:
        return {"message": GENERIC_RESEND_MESSAGE}

    now = datetime.now(UTC)
    if user.email_verification_sent_at is not None:
        sent_at = _as_utc(user.email_verification_sent_at)
        if (now - sent_at).total_seconds() < EMAIL_RESEND_COOLDOWN_SECONDS:
            return {"message": GENERIC_RESEND_MESSAGE}

    raw_token, token_hash, token_expiry = _verification_token()
    user.email_verification_token_hash = token_hash
    user.email_verification_expires_at = token_expiry
    user.email_verification_sent_at = now
    try:
        send_verification_email(
            email=user.email,
            nome=user.nome,
            raw_token=raw_token,
        )
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Falha ao reenviar confirmação de e-mail.")

    return {"message": GENERIC_RESEND_MESSAGE}
