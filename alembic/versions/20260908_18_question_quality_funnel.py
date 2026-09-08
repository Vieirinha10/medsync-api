"""Adiciona o funil de qualidade editorial ao catálogo de questões.

Revision ID: 20260908_18
Revises: 20260902_17
Create Date: 2026-09-08
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260908_18"
down_revision: str | None = "20260902_17"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("exam_questions")}
    indexes = {index["name"] for index in inspector.get_indexes("exam_questions")}

    with op.batch_alter_table("exam_questions") as batch_op:
        if "quality_status" not in columns:
            # Todo o legado v2 já passou pela triagem estrutural integral. O
            # default Python do modelo continua sendo "importada" para novas cargas.
            batch_op.add_column(
                sa.Column(
                    "quality_status",
                    sa.String(32),
                    nullable=False,
                    server_default="triada",
                )
            )
        if "quality_flags" not in columns:
            batch_op.add_column(
                sa.Column(
                    "quality_flags",
                    sa.JSON(),
                    nullable=False,
                    server_default=sa.text("'[]'"),
                )
            )
        if "quality_method" not in columns:
            batch_op.add_column(
                sa.Column(
                    "quality_method",
                    sa.String(80),
                    nullable=True,
                    server_default="structural_catalog_audit_v1",
                )
            )
        if "quality_source_reference" not in columns:
            batch_op.add_column(
                sa.Column("quality_source_reference", sa.Text(), nullable=True)
            )
        if "quality_reviewed_at" not in columns:
            batch_op.add_column(
                sa.Column(
                    "quality_reviewed_at", sa.DateTime(timezone=True), nullable=True
                )
            )
        if "ix_exam_questions_quality_status" not in indexes:
            batch_op.create_index(
                "ix_exam_questions_quality_status", ["quality_status"]
            )

    # O catálogo v1 não participou da auditoria estrutural integral do v2.
    op.execute(
        sa.text(
            "UPDATE exam_questions "
            "SET quality_status = 'importada', quality_method = NULL "
            "WHERE catalog_version <> 'v2'"
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("exam_questions")}
    indexes = {index["name"] for index in inspector.get_indexes("exam_questions")}

    with op.batch_alter_table("exam_questions") as batch_op:
        if "ix_exam_questions_quality_status" in indexes:
            batch_op.drop_index("ix_exam_questions_quality_status")
        for column in (
            "quality_reviewed_at",
            "quality_source_reference",
            "quality_method",
            "quality_flags",
            "quality_status",
        ):
            if column in columns:
                batch_op.drop_column(column)
