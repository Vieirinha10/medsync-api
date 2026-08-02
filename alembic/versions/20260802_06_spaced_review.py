"""Adiciona agendamento de revisão espaçada ao caderno de erros."""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260802_06"
down_revision = "20260802_05"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    if "study_errors" not in inspector.get_table_names():
        return

    existing = {column["name"] for column in inspector.get_columns("study_errors")}
    additions = [
        sa.Column(
            "revisoes_realizadas", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "sequencia_acertos", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("intervalo_dias", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fator_facilidade", sa.Float(), nullable=False, server_default="2.5"),
        sa.Column("ultima_revisao_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "proxima_revisao_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    ]
    with op.batch_alter_table("study_errors") as batch_op:
        for column in additions:
            if column.name not in existing:
                batch_op.add_column(column)

    indexes = {
        index["name"] for index in inspect(op.get_bind()).get_indexes("study_errors")
    }
    if "ix_study_errors_proxima_revisao_em" not in indexes:
        op.create_index(
            "ix_study_errors_proxima_revisao_em",
            "study_errors",
            ["proxima_revisao_em"],
        )


def downgrade() -> None:
    inspector = inspect(op.get_bind())
    if "study_errors" not in inspector.get_table_names():
        return

    indexes = {index["name"] for index in inspector.get_indexes("study_errors")}
    if "ix_study_errors_proxima_revisao_em" in indexes:
        op.drop_index("ix_study_errors_proxima_revisao_em", table_name="study_errors")

    existing = {
        column["name"] for column in inspect(op.get_bind()).get_columns("study_errors")
    }
    with op.batch_alter_table("study_errors") as batch_op:
        for column_name in (
            "proxima_revisao_em",
            "ultima_revisao_em",
            "fator_facilidade",
            "intervalo_dias",
            "sequencia_acertos",
            "revisoes_realizadas",
        ):
            if column_name in existing:
                batch_op.drop_column(column_name)
