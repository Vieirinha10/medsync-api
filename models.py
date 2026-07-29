from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    progressos: Mapped[list["Progresso"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )


class Progresso(Base):
    __tablename__ = "progressos"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    id_caso: Mapped[int] = mapped_column(Integer, index=True)
    respostas_usuario: Mapped[dict[str, Any]] = mapped_column(JSON)
    pontuacao: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    usuario: Mapped[User] = relationship(back_populates="progressos")
