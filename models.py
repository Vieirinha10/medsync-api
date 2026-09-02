from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
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
    asaas_customer_id: Mapped[str | None] = mapped_column(
        String(120), unique=True, nullable=True, index=True
    )
    terms_accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    terms_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    privacy_version: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    email_verification_token_hash: Mapped[str | None] = mapped_column(
        String(64), unique=True, nullable=True, index=True
    )
    email_verification_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    email_verification_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    password_reset_token_hash: Mapped[str | None] = mapped_column(
        String(64), unique=True, nullable=True, index=True
    )
    password_reset_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    password_reset_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    auth_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    progressos: Mapped[list["Progresso"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    erros_estudo: Mapped[list["StudyError"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    progressos_trilhas: Mapped[list["LearningPathProgress"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    tentativas_questoes: Mapped[list["QuestionAttempt"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    relatos_questoes: Mapped[list["QuestionReport"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )
    entitlement: Mapped["UserEntitlement | None"] = relationship(
        back_populates="usuario", cascade="all, delete-orphan", uselist=False
    )
    simulation_requests: Mapped[list["SimulationRequest"]] = relationship(
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


class SimulationRequest(Base):
    """Reserva persistente que torna o envio à Synapse idempotente."""

    __tablename__ = "simulation_requests"
    __table_args__ = (
        UniqueConstraint(
            "id_usuario",
            "idempotency_key",
            name="uq_simulation_request_user_key",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    id_caso: Mapped[int] = mapped_column(Integer, index=True)
    idempotency_key: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(20), default="processing", index=True)
    progresso_id: Mapped[int | None] = mapped_column(
        ForeignKey("progressos.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    usuario: Mapped[User] = relationship(back_populates="simulation_requests")
    progresso: Mapped[Progresso | None] = relationship()


class AIUsageRecord(Base):
    """Métrica financeira e operacional de cada chamada feita pela Synapse."""

    __tablename__ = "ai_usage_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    progresso_id: Mapped[int | None] = mapped_column(
        ForeignKey("progressos.id", ondelete="SET NULL"), nullable=True, index=True
    )
    operacao: Mapped[str] = mapped_column(String(40), index=True)
    modelo: Mapped[str] = mapped_column(String(80), index=True)
    input_tokens: Mapped[int] = mapped_column(Integer)
    cached_input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer)
    reasoning_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer)
    duracao_ms: Mapped[int] = mapped_column(Integer)
    custo_estimado_usd: Mapped[float | None] = mapped_column(Float, nullable=True)
    response_id: Mapped[str | None] = mapped_column(
        String(120), unique=True, nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )


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


class ExamQuestion(Base):
    __tablename__ = "exam_questions"
    __table_args__ = (
        Index(
            "ix_exam_questions_catalog_status_rank",
            "catalog_version",
            "status",
            "random_rank",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ano: Mapped[int] = mapped_column(Integer, index=True)
    instituicao: Mapped[str] = mapped_column(String(180), index=True)
    cabecalho: Mapped[str] = mapped_column(String(240))
    especialidade: Mapped[str] = mapped_column(String(120), index=True)
    assunto: Mapped[str] = mapped_column(String(160), index=True)
    enunciado: Mapped[str] = mapped_column(Text)
    alternativas: Mapped[list[dict[str, str]]] = mapped_column(JSON)
    alternativa_correta_id: Mapped[str] = mapped_column(String(5))
    fingerprint: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    explicacao: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    explicacao_status: Mapped[str] = mapped_column(
        String(30), default="pendente", index=True
    )
    status: Mapped[str] = mapped_column(String(30), default="publicada", index=True)
    catalog_version: Mapped[str] = mapped_column(
        String(20), default="v1", index=True
    )
    source_id: Mapped[str | None] = mapped_column(
        String(32), unique=True, index=True, nullable=True
    )
    statement_plain: Mapped[str | None] = mapped_column(Text, nullable=True)
    statement_rich_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    random_rank: Mapped[float] = mapped_column(Float, default=0.0)
    media_classification: Mapped[str] = mapped_column(
        String(40), default="NO_VISUAL_DEPENDENCY"
    )
    image_rights_status: Mapped[str] = mapped_column(
        String(40), default="NONE_REQUIRED"
    )
    content_hash_plain: Mapped[str | None] = mapped_column(
        String(64), index=True, nullable=True
    )
    content_hash_rich: Mapped[str | None] = mapped_column(
        String(64), index=True, nullable=True
    )
    answer_binding_hash: Mapped[str | None] = mapped_column(
        String(64), index=True, nullable=True
    )
    banca: Mapped[str | None] = mapped_column(String(120), nullable=True)
    finalidade: Mapped[str | None] = mapped_column(String(120), nullable=True)
    regiao: Mapped[str | None] = mapped_column(String(60), nullable=True)
    tema: Mapped[str | None] = mapped_column(String(160), index=True, nullable=True)
    subtema: Mapped[str | None] = mapped_column(String(160), nullable=True)
    tipo_prova: Mapped[str | None] = mapped_column(String(60), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    tentativas: Mapped[list["QuestionAttempt"]] = relationship(
        back_populates="questao", cascade="all, delete-orphan"
    )
    relatos: Mapped[list["QuestionReport"]] = relationship(
        back_populates="questao", cascade="all, delete-orphan"
    )
    aliases: Mapped[list["QuestionSourceAlias"]] = relationship(
        back_populates="questao_canonica", cascade="all, delete-orphan"
    )


class QuestionSourceAlias(Base):
    __tablename__ = "question_source_aliases"

    id: Mapped[int] = mapped_column(primary_key=True)
    canonical_question_id: Mapped[int] = mapped_column(
        ForeignKey("exam_questions.id", ondelete="CASCADE"), index=True
    )
    duplicate_source_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    ano: Mapped[int | None] = mapped_column(Integer, nullable=True)
    instituicao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    banca: Mapped[str | None] = mapped_column(String(120), nullable=True)
    regiao: Mapped[str | None] = mapped_column(String(60), nullable=True)
    content_hash_plain: Mapped[str] = mapped_column(String(64), index=True)
    content_hash_rich: Mapped[str] = mapped_column(String(64), index=True)
    answer_binding_hash: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    questao_canonica: Mapped[ExamQuestion] = relationship(back_populates="aliases")


class QuestionAttempt(Base):
    __tablename__ = "question_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    id_questao: Mapped[int] = mapped_column(
        ForeignKey("exam_questions.id", ondelete="CASCADE"), index=True
    )
    alternativa_selecionada_id: Mapped[str] = mapped_column(String(5))
    correta: Mapped[bool] = mapped_column(Boolean, index=True)
    tempo_segundos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )

    usuario: Mapped[User] = relationship(back_populates="tentativas_questoes")
    questao: Mapped[ExamQuestion] = relationship(back_populates="tentativas")


class QuestionReport(Base):
    __tablename__ = "question_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    id_questao: Mapped[int] = mapped_column(
        ForeignKey("exam_questions.id", ondelete="CASCADE"), index=True
    )
    motivo: Mapped[str] = mapped_column(String(60), index=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="aberto", index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    usuario: Mapped[User] = relationship(back_populates="relatos_questoes")
    questao: Mapped[ExamQuestion] = relationship(back_populates="relatos")


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


class PaymentOrder(Base):
    __tablename__ = "payment_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    plano_id: Mapped[str] = mapped_column(String(40), index=True)
    valor_centavos: Mapped[int] = mapped_column(Integer)
    moeda: Mapped[str] = mapped_column(String(3), default="BRL")
    tipo_cobranca: Mapped[str] = mapped_column(String(30))
    forma_pagamento: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(30), default="criado", index=True)
    asaas_checkout_id: Mapped[str | None] = mapped_column(
        String(120), unique=True, nullable=True, index=True
    )
    checkout_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    ultimo_pagamento_asaas_id: Mapped[str | None] = mapped_column(
        String(120), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class UserEntitlement(Base):
    __tablename__ = "user_entitlements"

    id_usuario: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    plano_id: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(30), default="ativo", index=True)
    valido_ate: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    renovacao_automatica: Mapped[bool] = mapped_column(Boolean, default=False)
    asaas_subscription_id: Mapped[str | None] = mapped_column(
        String(120), nullable=True, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    usuario: Mapped[User] = relationship(back_populates="entitlement")


class PaymentGrant(Base):
    __tablename__ = "payment_grants"

    asaas_payment_id: Mapped[str] = mapped_column(String(120), primary_key=True)
    pedido_id: Mapped[str] = mapped_column(
        ForeignKey("payment_orders.id", ondelete="CASCADE"), index=True
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class AsaasWebhookEvent(Base):
    __tablename__ = "asaas_webhook_events"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    tipo: Mapped[str] = mapped_column(String(80), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
