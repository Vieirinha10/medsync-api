from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
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
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    usuario: Mapped[User] = relationship(back_populates="progressos")


class ClinicalCase(Base):
    __tablename__ = "clinical_cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    especialidade: Mapped[str] = mapped_column(String(120), index=True)
    nivel_dificuldade: Mapped[str] = mapped_column(String(40), index=True)
    historia_clinica: Mapped[str] = mapped_column(Text)
    exame_fisico: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="publicado", index=True)
    versao_conteudo: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    exames: Mapped[list["ClinicalExam"]] = relationship(
        back_populates="caso",
        cascade="all, delete-orphan",
        order_by="ClinicalExam.ordem",
    )
    rubrica: Mapped["ClinicalRubric | None"] = relationship(
        back_populates="caso",
        cascade="all, delete-orphan",
        uselist=False,
    )


class ClinicalExam(Base):
    __tablename__ = "clinical_exams"
    __table_args__ = (
        UniqueConstraint("id_caso", "codigo", name="uq_clinical_exam_case_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    id_caso: Mapped[int] = mapped_column(
        ForeignKey("clinical_cases.id", ondelete="CASCADE"), index=True
    )
    codigo: Mapped[str] = mapped_column(String(80))
    nome: Mapped[str] = mapped_column(String(240))
    resultado: Mapped[str] = mapped_column(Text)
    referencia_adequada: Mapped[bool] = mapped_column(Boolean, default=True)
    ordem: Mapped[int] = mapped_column(Integer, default=0)

    caso: Mapped[ClinicalCase] = relationship(back_populates="exames")


class ClinicalRubric(Base):
    __tablename__ = "clinical_rubrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_caso: Mapped[int] = mapped_column(
        ForeignKey("clinical_cases.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    versao: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(30), default="revisada", index=True)
    definicao: Mapped[dict[str, Any]] = mapped_column(JSON)
    revisado_por: Mapped[str | None] = mapped_column(String(160), nullable=True)
    revisado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    caso: Mapped[ClinicalCase] = relationship(back_populates="rubrica")
