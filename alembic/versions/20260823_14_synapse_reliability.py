"""restore email verification and add Synapse request idempotency

Revision ID: 20260823_14
Revises: 20260818_13
Create Date: 2026-08-23
"""

from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260823_14"
down_revision = "20260818_13"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    user_columns = {column["name"] for column in inspector.get_columns("users")}

    with op.batch_alter_table("users") as batch_op:
        if "email_verified_at" not in user_columns:
            batch_op.add_column(
                sa.Column(
                    "email_verified_at", sa.DateTime(timezone=True), nullable=True
                )
            )
        if "email_verification_token_hash" not in user_columns:
            batch_op.add_column(
                sa.Column(
                    "email_verification_token_hash",
                    sa.String(length=64),
                    nullable=True,
                )
            )
        if "email_verification_expires_at" not in user_columns:
            batch_op.add_column(
                sa.Column(
                    "email_verification_expires_at",
                    sa.DateTime(timezone=True),
                    nullable=True,
                )
            )
        if "email_verification_sent_at" not in user_columns:
            batch_op.add_column(
                sa.Column(
                    "email_verification_sent_at",
                    sa.DateTime(timezone=True),
                    nullable=True,
                )
            )

    # Contas existentes já tinham acesso antes desta correção. Marcá-las como
    # verificadas evita bloquear usuários legítimos durante a migração.
    users = sa.table(
        "users",
        sa.column("email_verified_at", sa.DateTime(timezone=True)),
    )
    bind.execute(
        users.update()
        .where(users.c.email_verified_at.is_(None))
        .values(email_verified_at=datetime.now(UTC))
    )

    inspector = inspect(bind)
    user_indexes = {index["name"] for index in inspector.get_indexes("users")}
    if "ix_users_email_verification_token_hash" not in user_indexes:
        op.create_index(
            "ix_users_email_verification_token_hash",
            "users",
            ["email_verification_token_hash"],
            unique=True,
        )

    if "simulation_requests" not in inspector.get_table_names():
        op.create_table(
            "simulation_requests",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("id_usuario", sa.Integer(), nullable=False),
            sa.Column("id_caso", sa.Integer(), nullable=False),
            sa.Column("idempotency_key", sa.String(length=100), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("progresso_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["id_usuario"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(
                ["progresso_id"], ["progressos.id"], ondelete="SET NULL"
            ),
            sa.UniqueConstraint(
                "id_usuario",
                "idempotency_key",
                name="uq_simulation_request_user_key",
            ),
        )
        for column in ("id_usuario", "id_caso", "status", "progresso_id"):
            op.create_index(
                f"ix_simulation_requests_{column}",
                "simulation_requests",
                [column],
            )

    inspector = inspect(bind)
    if "ai_usage_records" not in inspector.get_table_names():
        op.create_table(
            "ai_usage_records",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("id_usuario", sa.Integer(), nullable=False),
            sa.Column("progresso_id", sa.Integer(), nullable=True),
            sa.Column("operacao", sa.String(length=40), nullable=False),
            sa.Column("modelo", sa.String(length=80), nullable=False),
            sa.Column("input_tokens", sa.Integer(), nullable=False),
            sa.Column("cached_input_tokens", sa.Integer(), nullable=False),
            sa.Column("output_tokens", sa.Integer(), nullable=False),
            sa.Column("reasoning_tokens", sa.Integer(), nullable=False),
            sa.Column("total_tokens", sa.Integer(), nullable=False),
            sa.Column("duracao_ms", sa.Integer(), nullable=False),
            sa.Column("custo_estimado_usd", sa.Float(), nullable=True),
            sa.Column("response_id", sa.String(length=120), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["id_usuario"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(
                ["progresso_id"], ["progressos.id"], ondelete="SET NULL"
            ),
        )
        for column in (
            "id_usuario",
            "progresso_id",
            "operacao",
            "modelo",
            "response_id",
            "created_at",
        ):
            op.create_index(
                f"ix_ai_usage_records_{column}",
                "ai_usage_records",
                [column],
                unique=column == "response_id",
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "ai_usage_records" in inspector.get_table_names():
        op.drop_table("ai_usage_records")
    if "simulation_requests" in inspector.get_table_names():
        op.drop_table("simulation_requests")

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    user_indexes = {index["name"] for index in inspector.get_indexes("users")}
    if "ix_users_email_verification_token_hash" in user_indexes:
        op.drop_index("ix_users_email_verification_token_hash", table_name="users")
    with op.batch_alter_table("users") as batch_op:
        for column in (
            "email_verification_sent_at",
            "email_verification_expires_at",
            "email_verification_token_hash",
            "email_verified_at",
        ):
            if column in user_columns:
                batch_op.drop_column(column)
