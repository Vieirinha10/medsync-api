"""Adiciona o módulo independente de questões de provas."""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260818_13"
down_revision = "20260811_11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    tables = inspect(op.get_bind()).get_table_names()

    if "exam_questions" not in tables:
        op.create_table(
            "exam_questions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("ano", sa.Integer(), nullable=False),
            sa.Column("instituicao", sa.String(180), nullable=False),
            sa.Column("cabecalho", sa.String(240), nullable=False),
            sa.Column("especialidade", sa.String(120), nullable=False),
            sa.Column("assunto", sa.String(160), nullable=False),
            sa.Column("enunciado", sa.Text(), nullable=False),
            sa.Column("alternativas", sa.JSON(), nullable=False),
            sa.Column("alternativa_correta_id", sa.String(5), nullable=False),
            sa.Column("fingerprint", sa.String(64), nullable=False, unique=True),
            sa.Column("explicacao", sa.JSON()),
            sa.Column("explicacao_status", sa.String(30), nullable=False),
            sa.Column("status", sa.String(30), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        for column in (
            "ano",
            "instituicao",
            "especialidade",
            "assunto",
            "fingerprint",
            "explicacao_status",
            "status",
        ):
            op.create_index(f"ix_exam_questions_{column}", "exam_questions", [column])

    if "question_attempts" not in tables:
        op.create_table(
            "question_attempts",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("id_usuario", sa.Integer(), nullable=False),
            sa.Column("id_questao", sa.Integer(), nullable=False),
            sa.Column("alternativa_selecionada_id", sa.String(5), nullable=False),
            sa.Column("correta", sa.Boolean(), nullable=False),
            sa.Column("tempo_segundos", sa.Integer()),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["id_usuario"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(
                ["id_questao"], ["exam_questions.id"], ondelete="CASCADE"
            ),
        )
        for column in ("id_usuario", "id_questao", "correta", "created_at"):
            op.create_index(
                f"ix_question_attempts_{column}", "question_attempts", [column]
            )

    if "question_reports" not in tables:
        op.create_table(
            "question_reports",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("id_usuario", sa.Integer(), nullable=False),
            sa.Column("id_questao", sa.Integer(), nullable=False),
            sa.Column("motivo", sa.String(60), nullable=False),
            sa.Column("descricao", sa.Text()),
            sa.Column("status", sa.String(30), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("resolved_at", sa.DateTime(timezone=True)),
            sa.ForeignKeyConstraint(["id_usuario"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(
                ["id_questao"], ["exam_questions.id"], ondelete="CASCADE"
            ),
        )
        for column in (
            "id_usuario",
            "id_questao",
            "motivo",
            "status",
            "created_at",
        ):
            op.create_index(
                f"ix_question_reports_{column}", "question_reports", [column]
            )


def downgrade() -> None:
    tables = inspect(op.get_bind()).get_table_names()
    for table in ("question_reports", "question_attempts", "exam_questions"):
        if table in tables:
            op.drop_table(table)
