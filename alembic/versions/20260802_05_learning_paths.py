"""Adiciona progresso persistente das trilhas de aprendizagem."""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260802_05"
down_revision = "20260802_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if "learning_path_progress" in inspect(op.get_bind()).get_table_names():
        return

    op.create_table(
        "learning_path_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("id_usuario", sa.Integer(), nullable=False),
        sa.Column("trilha_id", sa.String(length=100), nullable=False),
        sa.Column("atividade_id", sa.String(length=120), nullable=False),
        sa.Column("tipo_atividade", sa.String(length=30), nullable=False),
        sa.Column("tentativas", sa.Integer(), nullable=False),
        sa.Column("melhor_pontuacao", sa.Integer(), nullable=False),
        sa.Column("concluido_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ultima_tentativa_em", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["id_usuario"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "id_usuario",
            "trilha_id",
            "atividade_id",
            name="uq_learning_path_user_activity",
        ),
    )
    op.create_index(
        "ix_learning_path_progress_id_usuario",
        "learning_path_progress",
        ["id_usuario"],
    )
    op.create_index(
        "ix_learning_path_progress_trilha_id",
        "learning_path_progress",
        ["trilha_id"],
    )


def downgrade() -> None:
    if "learning_path_progress" in inspect(op.get_bind()).get_table_names():
        op.drop_table("learning_path_progress")
