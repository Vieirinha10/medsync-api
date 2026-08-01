"""Adiciona casos, exames e rubricas clínicas versionadas."""

import sqlalchemy as sa

from alembic import op

revision = "20260801_02"
down_revision = "20260801_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "clinical_cases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("titulo", sa.String(length=200), nullable=False),
        sa.Column("especialidade", sa.String(length=120), nullable=False),
        sa.Column("nivel_dificuldade", sa.String(length=40), nullable=False),
        sa.Column("historia_clinica", sa.Text(), nullable=False),
        sa.Column("exame_fisico", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("versao_conteudo", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_clinical_cases_especialidade", "clinical_cases", ["especialidade"]
    )
    op.create_index(
        "ix_clinical_cases_nivel_dificuldade", "clinical_cases", ["nivel_dificuldade"]
    )
    op.create_index("ix_clinical_cases_status", "clinical_cases", ["status"])

    op.create_table(
        "clinical_exams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("id_caso", sa.Integer(), nullable=False),
        sa.Column("codigo", sa.String(length=80), nullable=False),
        sa.Column("nome", sa.String(length=240), nullable=False),
        sa.Column("resultado", sa.Text(), nullable=False),
        sa.Column("referencia_adequada", sa.Boolean(), nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["id_caso"], ["clinical_cases.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("id_caso", "codigo", name="uq_clinical_exam_case_code"),
    )
    op.create_index("ix_clinical_exams_id_caso", "clinical_exams", ["id_caso"])

    op.create_table(
        "clinical_rubrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("id_caso", sa.Integer(), nullable=False),
        sa.Column("versao", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("definicao", sa.JSON(), nullable=False),
        sa.Column("revisado_por", sa.String(length=160), nullable=True),
        sa.Column("revisado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["id_caso"], ["clinical_cases.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("id_caso", name="uq_clinical_rubrics_id_caso"),
    )
    op.create_index(
        "ix_clinical_rubrics_id_caso", "clinical_rubrics", ["id_caso"], unique=True
    )
    op.create_index("ix_clinical_rubrics_status", "clinical_rubrics", ["status"])


def downgrade() -> None:
    op.drop_table("clinical_rubrics")
    op.drop_table("clinical_exams")
    op.drop_table("clinical_cases")
