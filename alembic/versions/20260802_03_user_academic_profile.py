"""Adiciona o perfil acadêmico dos usuários."""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260802_03"
down_revision = "20260801_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    columns = {column["name"] for column in inspect(op.get_bind()).get_columns("users")}

    if "periodo_curso" not in columns:
        op.add_column("users", sa.Column("periodo_curso", sa.Integer(), nullable=True))
    if "faculdade" not in columns:
        op.add_column(
            "users", sa.Column("faculdade", sa.String(length=180), nullable=True)
        )


def downgrade() -> None:
    columns = {column["name"] for column in inspect(op.get_bind()).get_columns("users")}

    if "faculdade" in columns:
        op.drop_column("users", "faculdade")
    if "periodo_curso" in columns:
        op.drop_column("users", "periodo_curso")
