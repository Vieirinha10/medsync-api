"""Vincula usuários aos clientes da Asaas para checkout transparente."""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260811_10"
down_revision = "20260811_09"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "asaas_customer_id" not in columns:
        op.add_column(
            "users",
            sa.Column("asaas_customer_id", sa.String(120), nullable=True),
        )
        op.create_index(
            "ix_users_asaas_customer_id",
            "users",
            ["asaas_customer_id"],
            unique=True,
        )


def downgrade() -> None:
    columns = {column["name"] for column in inspect(op.get_bind()).get_columns("users")}
    if "asaas_customer_id" in columns:
        op.drop_index("ix_users_asaas_customer_id", table_name="users")
        op.drop_column("users", "asaas_customer_id")
