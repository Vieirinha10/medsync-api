"""Cria o esquema inicial persistente do MedSync."""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260801_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    existing_tables = set(inspect(op.get_bind()).get_table_names())

    if "users" not in existing_tables:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("nome", sa.String(length=120), nullable=False),
            sa.Column("email", sa.String(length=320), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.UniqueConstraint("email", name="uq_users_email"),
        )
        op.create_index("ix_users_email", "users", ["email"], unique=True)

    if "progressos" not in existing_tables:
        op.create_table(
            "progressos",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("id_usuario", sa.Integer(), nullable=False),
            sa.Column("id_caso", sa.Integer(), nullable=False),
            sa.Column("respostas_usuario", sa.JSON(), nullable=False),
            sa.Column("pontuacao", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["id_usuario"], ["users.id"]),
        )
        op.create_index("ix_progressos_id_usuario", "progressos", ["id_usuario"])
        op.create_index("ix_progressos_id_caso", "progressos", ["id_caso"])


def downgrade() -> None:
    existing_tables = set(inspect(op.get_bind()).get_table_names())
    if "progressos" in existing_tables:
        op.drop_table("progressos")
    if "users" in existing_tables:
        op.drop_table("users")
