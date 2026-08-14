"""record legal document acceptance

Revision ID: 20260811_11
Revises: 20260811_10
Create Date: 2026-08-11
"""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260811_11"
down_revision = "20260811_10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    columns = {column["name"] for column in inspect(op.get_bind()).get_columns("users")}
    with op.batch_alter_table("users") as batch_op:
        if "terms_accepted_at" not in columns:
            batch_op.add_column(
                sa.Column(
                    "terms_accepted_at", sa.DateTime(timezone=True), nullable=True
                )
            )
        if "terms_version" not in columns:
            batch_op.add_column(
                sa.Column("terms_version", sa.String(length=20), nullable=True)
            )
        if "privacy_version" not in columns:
            batch_op.add_column(
                sa.Column("privacy_version", sa.String(length=20), nullable=True)
            )


def downgrade() -> None:
    columns = {column["name"] for column in inspect(op.get_bind()).get_columns("users")}
    with op.batch_alter_table("users") as batch_op:
        if "privacy_version" in columns:
            batch_op.drop_column("privacy_version")
        if "terms_version" in columns:
            batch_op.drop_column("terms_version")
        if "terms_accepted_at" in columns:
            batch_op.drop_column("terms_accepted_at")
