"""add secure password recovery and session versioning

Revision ID: 20260827_15
Revises: 20260823_14
Create Date: 2026-08-27
"""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260827_15"
down_revision = "20260823_14"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}

    with op.batch_alter_table("users") as batch_op:
        if "password_reset_token_hash" not in columns:
            batch_op.add_column(
                sa.Column("password_reset_token_hash", sa.String(64), nullable=True)
            )
        if "password_reset_expires_at" not in columns:
            batch_op.add_column(
                sa.Column(
                    "password_reset_expires_at",
                    sa.DateTime(timezone=True),
                    nullable=True,
                )
            )
        if "password_reset_sent_at" not in columns:
            batch_op.add_column(
                sa.Column(
                    "password_reset_sent_at",
                    sa.DateTime(timezone=True),
                    nullable=True,
                )
            )
        if "auth_version" not in columns:
            batch_op.add_column(
                sa.Column(
                    "auth_version",
                    sa.Integer(),
                    nullable=False,
                    server_default="0",
                )
            )

    inspector = inspect(bind)
    indexes = {index["name"] for index in inspector.get_indexes("users")}
    if "ix_users_password_reset_token_hash" not in indexes:
        op.create_index(
            "ix_users_password_reset_token_hash",
            "users",
            ["password_reset_token_hash"],
            unique=True,
        )


def downgrade() -> None:
    inspector = inspect(op.get_bind())
    indexes = {index["name"] for index in inspector.get_indexes("users")}
    if "ix_users_password_reset_token_hash" in indexes:
        op.drop_index("ix_users_password_reset_token_hash", table_name="users")

    columns = {column["name"] for column in inspector.get_columns("users")}
    with op.batch_alter_table("users") as batch_op:
        for name in (
            "auth_version",
            "password_reset_sent_at",
            "password_reset_expires_at",
            "password_reset_token_hash",
        ):
            if name in columns:
                batch_op.drop_column(name)
