"""Adiciona versionamento ao catalogo de questoes (v2) e aliases de duplicatas.

Revision ID: 20260902_16
Revises: 20260827_15
Create Date: 2026-09-02
"""

from datetime import UTC, datetime
import sqlalchemy as sa
from alembic import op

revision = "20260902_16"
down_revision = "20260827_15"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing_cols = {c["name"] for c in insp.get_columns("exam_questions")}
    existing_indexes = {i["name"] for i in insp.get_indexes("exam_questions")}
    existing_tables = set(insp.get_table_names())

    # 1. Alterar exam_questions via batch_alter_table
    with op.batch_alter_table("exam_questions") as batch_op:
        if "catalog_version" not in existing_cols:
            batch_op.add_column(
                sa.Column(
                    "catalog_version",
                    sa.String(20),
                    nullable=False,
                    server_default="v1",
                )
            )
        if "source_id" not in existing_cols:
            batch_op.add_column(sa.Column("source_id", sa.String(32), nullable=True))
        if "statement_plain" not in existing_cols:
            batch_op.add_column(sa.Column("statement_plain", sa.Text(), nullable=True))
        if "statement_rich_html" not in existing_cols:
            batch_op.add_column(sa.Column("statement_rich_html", sa.Text(), nullable=True))
        if "random_rank" not in existing_cols:
            batch_op.add_column(
                sa.Column(
                    "random_rank",
                    sa.Float(),
                    nullable=False,
                    server_default="0.0",
                )
            )
        if "media_classification" not in existing_cols:
            batch_op.add_column(
                sa.Column(
                    "media_classification",
                    sa.String(40),
                    nullable=False,
                    server_default="NO_VISUAL_DEPENDENCY",
                )
            )
        if "image_rights_status" not in existing_cols:
            batch_op.add_column(
                sa.Column(
                    "image_rights_status",
                    sa.String(40),
                    nullable=False,
                    server_default="NONE_REQUIRED",
                )
            )
        if "content_hash_plain" not in existing_cols:
            batch_op.add_column(
                sa.Column("content_hash_plain", sa.String(64), nullable=True)
            )
        if "content_hash_rich" not in existing_cols:
            batch_op.add_column(
                sa.Column("content_hash_rich", sa.String(64), nullable=True)
            )
        if "answer_binding_hash" not in existing_cols:
            batch_op.add_column(
                sa.Column("answer_binding_hash", sa.String(64), nullable=True)
            )
        if "banca" not in existing_cols:
            batch_op.add_column(sa.Column("banca", sa.String(120), nullable=True))
        if "finalidade" not in existing_cols:
            batch_op.add_column(sa.Column("finalidade", sa.String(120), nullable=True))
        if "regiao" not in existing_cols:
            batch_op.add_column(sa.Column("regiao", sa.String(60), nullable=True))
        if "tema" not in existing_cols:
            batch_op.add_column(sa.Column("tema", sa.String(160), nullable=True))
        if "subtema" not in existing_cols:
            batch_op.add_column(sa.Column("subtema", sa.String(160), nullable=True))
        if "tipo_prova" not in existing_cols:
            batch_op.add_column(sa.Column("tipo_prova", sa.String(60), nullable=True))

        if "ix_exam_questions_catalog_status_rank_id" not in existing_indexes:
            batch_op.create_index(
                "ix_exam_questions_catalog_status_rank_id",
                ["catalog_version", "status", "random_rank", "id"],
            )
        if "ix_exam_questions_catalog_version" not in existing_indexes:
            batch_op.create_index("ix_exam_questions_catalog_version", ["catalog_version"])
        if "ix_exam_questions_source_id" not in existing_indexes:
            batch_op.create_index("ix_exam_questions_source_id", ["source_id"], unique=True)
        if "ix_exam_questions_content_hash_plain" not in existing_indexes:
            batch_op.create_index("ix_exam_questions_content_hash_plain", ["content_hash_plain"])
        if "ix_exam_questions_tema" not in existing_indexes:
            batch_op.create_index("ix_exam_questions_tema", ["tema"])

    # 2. Criar tabela question_source_aliases
    if "question_source_aliases" not in existing_tables:
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
            sa.Column("regiao", sa.String(60), nullable=True),
            sa.Column("content_hash_plain", sa.String(64), nullable=False, index=True),
            sa.Column("content_hash_rich", sa.String(64), nullable=False, index=True),
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
    insp = sa.inspect(bind)
    existing_tables = set(insp.get_table_names())
    existing_indexes = {i["name"] for i in insp.get_indexes("exam_questions")}
    existing_cols = {c["name"] for c in insp.get_columns("exam_questions")}

    # 1. Dropar tabela de aliases se existir
    if "question_source_aliases" in existing_tables:
        op.drop_table("question_source_aliases")

    # 2. Reverter colunas e índices em exam_questions
    with op.batch_alter_table("exam_questions") as batch_op:
        for idx in [
            "ix_exam_questions_catalog_status_rank_id",
            "ix_exam_questions_catalog_status_rank",
            "ix_exam_questions_tema",
            "ix_exam_questions_content_hash_plain",
            "ix_exam_questions_source_id",
            "ix_exam_questions_catalog_version",
            "ix_exam_questions_content_hash",  # compatibilidade com schema intermediário
        ]:
            if idx in existing_indexes:
                batch_op.drop_index(idx)

        for col in [
            "tipo_prova",
            "subtema",
            "tema",
            "regiao",
            "finalidade",
            "banca",
            "answer_binding_hash",
            "content_hash_rich",
            "content_hash_plain",
            "content_hash",  # compatibilidade com schema intermediário
            "region",        # compatibilidade com schema intermediário
            "image_rights_status",
            "media_classification",
            "random_rank",
            "statement_rich_html",
            "statement_plain",
            "source_id",
            "catalog_version",
        ]:
            if col in existing_cols:
                batch_op.drop_column(col)
