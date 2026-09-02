"""Adiciona versionamento ao catalogo de questoes (v2) e aliases de duplicatas.

Revision ID: 20260902_16
Revises: 20260827_15
Create Date: 2026-09-02
"""

from datetime import UTC, datetime
import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260902_16"
down_revision = "20260827_15"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()

    if "exam_questions" in tables:
        existing_cols = {col["name"] for col in inspector.get_columns("exam_questions")}

        if "catalog_version" not in existing_cols:
            op.add_column(
                "exam_questions",
                sa.Column(
                    "catalog_version",
                    sa.String(20),
                    nullable=False,
                    server_default="v1",
                ),
            )
            op.create_index(
                "ix_exam_questions_catalog_version",
                "exam_questions",
                ["catalog_version"],
            )

        if "source_id" not in existing_cols:
            op.add_column(
                "exam_questions",
                sa.Column("source_id", sa.String(32), nullable=True),
            )
            op.create_index(
                "ix_exam_questions_source_id",
                "exam_questions",
                ["source_id"],
                unique=True,
            )

        if "statement_plain" not in existing_cols:
            op.add_column(
                "exam_questions",
                sa.Column("statement_plain", sa.Text(), nullable=True),
            )

        if "statement_rich_html" not in existing_cols:
            op.add_column(
                "exam_questions",
                sa.Column("statement_rich_html", sa.Text(), nullable=True),
            )

        if "random_rank" not in existing_cols:
            op.add_column(
                "exam_questions",
                sa.Column(
                    "random_rank",
                    sa.Float(),
                    nullable=False,
                    server_default="0.0",
                ),
            )
            op.create_index(
                "ix_exam_questions_random_rank",
                "exam_questions",
                ["random_rank"],
            )

        if "media_classification" not in existing_cols:
            op.add_column(
                "exam_questions",
                sa.Column(
                    "media_classification",
                    sa.String(40),
                    nullable=False,
                    server_default="NO_VISUAL_DEPENDENCY",
                ),
            )

        if "image_rights_status" not in existing_cols:
            op.add_column(
                "exam_questions",
                sa.Column(
                    "image_rights_status",
                    sa.String(40),
                    nullable=False,
                    server_default="NONE_REQUIRED",
                ),
            )

        if "content_hash" not in existing_cols:
            op.add_column(
                "exam_questions",
                sa.Column("content_hash", sa.String(64), nullable=True),
            )
            op.create_index(
                "ix_exam_questions_content_hash",
                "exam_questions",
                ["content_hash"],
            )

        if "answer_binding_hash" not in existing_cols:
            op.add_column(
                "exam_questions",
                sa.Column("answer_binding_hash", sa.String(64), nullable=True),
            )

        if "banca" not in existing_cols:
            op.add_column(
                "exam_questions",
                sa.Column("banca", sa.String(120), nullable=True),
            )

        if "finalidade" not in existing_cols:
            op.add_column(
                "exam_questions",
                sa.Column("finalidade", sa.String(120), nullable=True),
            )

        if "region" not in existing_cols:
            op.add_column(
                "exam_questions",
                sa.Column("region", sa.String(60), nullable=True),
            )

    if "question_source_aliases" not in tables:
        op.create_table(
            "question_source_aliases",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "canonical_question_id",
                sa.Integer(),
                sa.ForeignKey("exam_questions.id", ondelete="CASCADE"),
                nullable=False,
                index=True,
            ),
            sa.Column(
                "duplicate_source_id",
                sa.String(32),
                nullable=False,
                unique=True,
                index=True,
            ),
            sa.Column("ano", sa.Integer(), nullable=True),
            sa.Column("instituicao", sa.String(255), nullable=True),
            sa.Column("banca", sa.String(120), nullable=True),
            sa.Column("content_hash", sa.String(64), nullable=False, index=True),
            sa.Column("answer_binding_hash", sa.String(64), nullable=False, index=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.now(),
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()

    if "question_source_aliases" in tables:
        op.drop_table("question_source_aliases")

    if "exam_questions" in tables:
        existing_cols = {col["name"] for col in inspector.get_columns("exam_questions")}
        for col, idx in (
            ("content_hash", "ix_exam_questions_content_hash"),
            ("random_rank", "ix_exam_questions_random_rank"),
            ("source_id", "ix_exam_questions_source_id"),
            ("catalog_version", "ix_exam_questions_catalog_version"),
        ):
            if col in existing_cols:
                try:
                    op.drop_index(idx, "exam_questions")
                except Exception:
                    pass

        for col in (
            "region",
            "finalidade",
            "banca",
            "answer_binding_hash",
            "content_hash",
            "image_rights_status",
            "media_classification",
            "random_rank",
            "statement_rich_html",
            "statement_plain",
            "source_id",
            "catalog_version",
        ):
            if col in existing_cols:
                op.drop_column("exam_questions", col)
