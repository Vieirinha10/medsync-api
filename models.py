from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
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
    periodo_curso: Mapped[int | None] = mapped_column(Integer, nullable=True)
    faculdade: Mapped[str | None] = mapped_column(String(180), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )

    progressos: Mapped[list["Progresso"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    erros_estudo: Mapped[list["StudyError"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    progressos_trilhas: Mapped[list["LearningPathProgress"]] = relationship(
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


class StudyError(Base):
    __tablename__ = "study_errors"
    __table_args__ = (
        UniqueConstraint(
            "id_usuario",
            "tipo_origem",
            "id_origem",
            name="uq_study_error_user_source",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    tipo_origem: Mapped[str] = mapped_column(String(30), index=True)
    id_origem: Mapped[str] = mapped_column(String(120))
    titulo: Mapped[str] = mapped_column(String(240))
    especialidade: Mapped[str] = mapped_column(String(120), index=True)
    dificuldade: Mapped[str | None] = mapped_column(String(40), nullable=True)
    pergunta: Mapped[str] = mapped_column(Text)
    resposta_usuario: Mapped[str] = mapped_column(Text)
    resposta_correta: Mapped[str] = mapped_column(Text)
    explicacao: Mapped[str] = mapped_column(Text)
    detalhes: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="pendente", index=True)
    quantidade_erros: Mapped[int] = mapped_column(Integer, default=1)
    visto_primeiro_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    visto_ultimo_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    dominado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revisoes_realizadas: Mapped[int] = mapped_column(Integer, default=0)
    sequencia_acertos: Mapped[int] = mapped_column(Integer, default=0)
    intervalo_dias: Mapped[int] = mapped_column(Integer, default=0)
    fator_facilidade: Mapped[float] = mapped_column(Float, default=2.5)
    ultima_revisao_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    proxima_revisao_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        index=True,
    )

    usuario: Mapped[User] = relationship(back_populates="erros_estudo")


class LearningPathProgress(Base):
    __tablename__ = "learning_path_progress"
    __table_args__ = (
        UniqueConstraint(
            "id_usuario",
            "trilha_id",
            "atividade_id",
            name="uq_learning_path_user_activity",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    trilha_id: Mapped[str] = mapped_column(String(100), index=True)
    atividade_id: Mapped[str] = mapped_column(String(120))
    tipo_atividade: Mapped[str] = mapped_column(String(30))
    tentativas: Mapped[int] = mapped_column(Integer, default=1)
    melhor_pontuacao: Mapped[int] = mapped_column(Integer, default=0)
    concluido_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    ultima_tentativa_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    usuario: Mapped[User] = relationship(back_populates="progressos_trilhas")


class ClinicalCase(Base):
    __tablename__ = "clinical_cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    titulo_publico: Mapped[str] = mapped_column(String(240))
    especialidade: Mapped[str] = mapped_column(String(120), index=True)
    nivel_dificuldade: Mapped[str] = mapped_column(String(40), index=True)
    historia_clinica: Mapped[str] = mapped_column(Text)
    exame_fisico: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="publicado", index=True)
    versao_conteudo: Mapped[int] = mapped_column(Integer, default=1)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
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


class VisualChallenge(Base):
    __tablename__ = "visual_challenges"

    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    titulo: Mapped[str] = mapped_column(String(240))
    especialidade: Mapped[str] = mapped_column(String(120), index=True)
    dificuldade: Mapped[str] = mapped_column(String(40), index=True)
    modalidade: Mapped[str] = mapped_column(String(80))
    pergunta: Mapped[str] = mapped_column(Text)
    imagem_url: Mapped[str] = mapped_column(String(1000))
    imagem_alt: Mapped[str] = mapped_column(String(500))
    alternativas: Mapped[list[dict[str, str]]] = mapped_column(JSON)
    alternativa_correta_id: Mapped[str] = mapped_column(String(20))
    diagnostico_correto: Mapped[str] = mapped_column(String(500))
    explicacao: Mapped[str] = mapped_column(Text)
    achados_chave: Mapped[list[str]] = mapped_column(JSON, default=list)
    fonte_credito: Mapped[str] = mapped_column(String(240), default="MedSync")
    fonte_licenca: Mapped[str] = mapped_column(String(120), default="Uso educacional")
    fonte_url: Mapped[str] = mapped_column(String(1000), default="#")
    status: Mapped[str] = mapped_column(String(30), default="publicado", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(180))
    mensagem: Mapped[str] = mapped_column(Text)
    tom: Mapped[str] = mapped_column(String(30), default="informativo")
    link_texto: Mapped[str | None] = mapped_column(String(100), nullable=True)
    link_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    inicia_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    termina_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    criado_por: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class UserActivity(Base):
    __tablename__ = "user_activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    evento: Mapped[str] = mapped_column(String(50), index=True)
    tipo_conteudo: Mapped[str | None] = mapped_column(
        String(40), nullable=True, index=True
    )
    id_conteudo: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )
