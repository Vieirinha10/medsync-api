"""Cria a taxonomia médica unificada e a classificação semântica em sombra.

Revision ID: 20260910_20
Revises: 20260910_19
Create Date: 2026-09-10
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260910_20"
down_revision: str | None = "20260910_19"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "medical_taxonomy_versions",
        sa.Column("id", sa.String(40), primary_key=True),
        sa.Column("nome", sa.String(160), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("status", sa.String(24), nullable=False, server_default="rascunho"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('rascunho', 'validando', 'publicada', 'arquivada')",
            name="ck_medical_taxonomy_version_status",
        ),
    )
    op.create_index(
        "ix_medical_taxonomy_versions_status",
        "medical_taxonomy_versions",
        ["status"],
    )

    op.create_table(
        "medical_taxonomy_nodes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "taxonomy_version",
            sa.String(40),
            sa.ForeignKey("medical_taxonomy_versions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code", sa.String(180), nullable=False),
        sa.Column("label", sa.String(180), nullable=False),
        sa.Column("level", sa.String(20), nullable=False),
        sa.Column(
            "parent_id",
            sa.Integer(),
            sa.ForeignKey("medical_taxonomy_nodes.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("aliases", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("status", sa.String(24), nullable=False, server_default="rascunho"),
        sa.Column("source", sa.String(80), nullable=False, server_default="editorial"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "taxonomy_version",
            "code",
            name="uq_medical_taxonomy_version_code",
        ),
        sa.CheckConstraint(
            "level IN ('especialidade', 'tema', 'assunto')",
            name="ck_medical_taxonomy_node_level",
        ),
        sa.CheckConstraint(
            "status IN ('rascunho', 'proposto', 'aprovado', 'descontinuado')",
            name="ck_medical_taxonomy_node_status",
        ),
    )
    op.create_index(
        "ix_medical_taxonomy_nodes_taxonomy_version",
        "medical_taxonomy_nodes",
        ["taxonomy_version"],
    )
    op.create_index(
        "ix_medical_taxonomy_nodes_level",
        "medical_taxonomy_nodes",
        ["level"],
    )
    op.create_index(
        "ix_medical_taxonomy_nodes_parent_id",
        "medical_taxonomy_nodes",
        ["parent_id"],
    )
    op.create_index(
        "ix_medical_taxonomy_nodes_status",
        "medical_taxonomy_nodes",
        ["status"],
    )
    op.create_index(
        "ix_medical_taxonomy_parent_level",
        "medical_taxonomy_nodes",
        ["taxonomy_version", "parent_id", "level", "status"],
    )

    op.create_table(
        "taxonomy_classification_runs",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "taxonomy_version",
            sa.String(40),
            sa.ForeignKey("medical_taxonomy_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("content_type", sa.String(32), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="preparando"),
        sa.Column("cursor_after_id", sa.String(120), nullable=True),
        sa.Column("processed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("verified_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("review_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("configuration", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "content_type IN ('questao', 'caso_clinico', 'desafio_visual')",
            name="ck_taxonomy_run_content_type",
        ),
        sa.CheckConstraint(
            "status IN ('preparando', 'executando', 'pausada', 'concluida', 'falhou')",
            name="ck_taxonomy_run_status",
        ),
    )
    op.create_index(
        "ix_taxonomy_classification_runs_taxonomy_version",
        "taxonomy_classification_runs",
        ["taxonomy_version"],
    )
    op.create_index(
        "ix_taxonomy_classification_runs_content_type",
        "taxonomy_classification_runs",
        ["content_type"],
    )
    op.create_index(
        "ix_taxonomy_classification_runs_status",
        "taxonomy_classification_runs",
        ["status"],
    )

    op.create_table(
        "content_taxonomy_classifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("content_type", sa.String(32), nullable=False),
        sa.Column("content_id", sa.String(120), nullable=False),
        sa.Column(
            "taxonomy_version",
            sa.String(40),
            sa.ForeignKey("medical_taxonomy_versions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("specialty_code", sa.String(180), nullable=False),
        sa.Column("specialty_label", sa.String(180), nullable=False),
        sa.Column("theme_code", sa.String(180), nullable=False),
        sa.Column("theme_label", sa.String(180), nullable=False),
        sa.Column("subject_code", sa.String(180), nullable=False),
        sa.Column("subject_label", sa.String(180), nullable=False),
        sa.Column("learning_objectives", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("competencies", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("clinical_contexts", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("difficulty", sa.String(32), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("classifier_confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("verifier_confidence", sa.Float(), nullable=True),
        sa.Column("verifier_agrees", sa.Boolean(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="proposta"),
        sa.Column("classification_method", sa.String(80), nullable=False),
        sa.Column("classifier_model", sa.String(120), nullable=True),
        sa.Column("verifier_model", sa.String(120), nullable=True),
        sa.Column("evidence", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("ambiguity_reason", sa.Text(), nullable=True),
        sa.Column("classifier_payload", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("verifier_payload", sa.JSON(), nullable=True),
        sa.Column("source_hash", sa.String(64), nullable=False),
        sa.Column(
            "run_id",
            sa.String(64),
            sa.ForeignKey("taxonomy_classification_runs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "content_type",
            "content_id",
            "taxonomy_version",
            name="uq_content_taxonomy_item_version",
        ),
        sa.CheckConstraint(
            "content_type IN ('questao', 'caso_clinico', 'desafio_visual')",
            name="ck_content_taxonomy_content_type",
        ),
        sa.CheckConstraint(
            "status IN ('proposta', 'verificada', 'revisao_necessaria', 'aprovada', 'publicada')",
            name="ck_content_taxonomy_status",
        ),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="ck_content_taxonomy_confidence",
        ),
        sa.CheckConstraint(
            "classifier_confidence >= 0 AND classifier_confidence <= 1",
            name="ck_content_taxonomy_classifier_confidence",
        ),
        sa.CheckConstraint(
            "verifier_confidence IS NULL OR (verifier_confidence >= 0 AND verifier_confidence <= 1)",
            name="ck_content_taxonomy_verifier_confidence",
        ),
        sa.CheckConstraint(
            "specialty_code <> theme_code AND theme_code <> subject_code",
            name="ck_content_taxonomy_distinct_levels",
        ),
    )
    for column in ("content_type", "content_id", "taxonomy_version", "status", "source_hash", "run_id"):
        op.create_index(
            f"ix_content_taxonomy_classifications_{column}",
            "content_taxonomy_classifications",
            [column],
        )
    op.create_index(
        "ix_content_taxonomy_navigation",
        "content_taxonomy_classifications",
        [
            "taxonomy_version",
            "status",
            "specialty_code",
            "theme_code",
            "subject_code",
        ],
    )
    op.create_index(
        "ix_content_taxonomy_review_queue",
        "content_taxonomy_classifications",
        ["taxonomy_version", "status", "confidence"],
    )


def downgrade() -> None:
    op.drop_table("content_taxonomy_classifications")
    op.drop_table("taxonomy_classification_runs")
    op.drop_table("medical_taxonomy_nodes")
    op.drop_table("medical_taxonomy_versions")
