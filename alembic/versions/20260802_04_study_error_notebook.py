"""Cria o caderno de erros persistente por usuário."""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260802_04"
down_revision = "20260802_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if "study_errors" in inspect(op.get_bind()).get_table_names():
        return

    op.create_table(
        "study_errors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("id_usuario", sa.Integer(), nullable=False),
        sa.Column("tipo_origem", sa.String(length=30), nullable=False),
        sa.Column("id_origem", sa.String(length=120), nullable=False),
        sa.Column("titulo", sa.String(length=240), nullable=False),
        sa.Column("especialidade", sa.String(length=120), nullable=False),
        sa.Column("dificuldade", sa.String(length=40), nullable=True),
        sa.Column("pergunta", sa.Text(), nullable=False),
        sa.Column("resposta_usuario", sa.Text(), nullable=False),
        sa.Column("resposta_correta", sa.Text(), nullable=False),
        sa.Column("explicacao", sa.Text(), nullable=False),
        sa.Column("detalhes", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("quantidade_erros", sa.Integer(), nullable=False),
        sa.Column("visto_primeiro_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("visto_ultimo_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dominado_em", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["id_usuario"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "id_usuario",
            "tipo_origem",
            "id_origem",
            name="uq_study_error_user_source",
        ),
    )
    op.create_index("ix_study_errors_id_usuario", "study_errors", ["id_usuario"])
    op.create_index("ix_study_errors_tipo_origem", "study_errors", ["tipo_origem"])
    op.create_index("ix_study_errors_especialidade", "study_errors", ["especialidade"])
    op.create_index("ix_study_errors_status", "study_errors", ["status"])


def downgrade() -> None:
    if "study_errors" in inspect(op.get_bind()).get_table_names():
        op.drop_table("study_errors")
