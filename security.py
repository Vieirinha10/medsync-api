import os
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from database import get_db
from models import User
from settings import is_admin_email

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if ENVIRONMENT == "production" and not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY é obrigatória em produção.")
if ENVIRONMENT == "production" and len(JWT_SECRET_KEY or "") < 32:
    raise RuntimeError("JWT_SECRET_KEY deve ter pelo menos 32 caracteres em produção.")
JWT_SECRET_KEY = JWT_SECRET_KEY or "medsync-local-development-only-32-chars"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de autenticação inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized from None

    try:
        payload = jwt.decode(
            credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
        )
        user_id = int(payload["sub"])
    except (InvalidTokenError, KeyError, TypeError, ValueError):
        raise unauthorized from None

    user = db.get(User, user_id)
    if user is None:
        raise unauthorized
    return user


def has_active_premium(user: User) -> bool:
    if is_admin_email(user.email):
        return True
    entitlement = user.entitlement
    if entitlement is None or entitlement.status != "ativo":
        return False
    expiry = entitlement.valido_ate
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=UTC)
    return expiry > datetime.now(UTC)


def require_premium_content(user: User, *, is_premium: bool) -> None:
    if is_premium and not has_active_premium(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este conteúdo requer uma assinatura Premium ativa.",
        )
