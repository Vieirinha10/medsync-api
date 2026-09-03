"""question_catalog_v2_fix_index

Revision ID: 20260902_17
Revises: 20260902_16
Create Date: 2026-09-02 21:40:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260902_17"
down_revision: str | None = "20260902_16"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing_indexes = {i["name"] for i in insp.get_indexes("exam_questions")}

    # 1. Remover índice isolado de random_rank se existir
    if "ix_exam_questions_random_rank" in existing_indexes:
        op.drop_index("ix_exam_questions_random_rank", table_name="exam_questions")

    # 2. Remover índice intermediário de 3 colunas se existir
    if "ix_exam_questions_catalog_status_rank" in existing_indexes:
        op.drop_index("ix_exam_questions_catalog_status_rank", table_name="exam_questions")

    # 3. Criar índice composto de 4 colunas (catalog_version, status, random_rank, id)
    if "ix_exam_questions_catalog_status_rank_id" not in existing_indexes:
        op.create_index(
            "ix_exam_questions_catalog_status_rank_id",
            "exam_questions",
            ["catalog_version", "status", "random_rank", "id"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing_indexes = {i["name"] for i in insp.get_indexes("exam_questions")}

    # 1. Remover índice composto de 4 colunas se existir
    if "ix_exam_questions_catalog_status_rank_id" in existing_indexes:
        op.drop_index("ix_exam_questions_catalog_status_rank_id", table_name="exam_questions")

    # 2. Restaurar estado histórico real da revisão 16 (índice isolado ix_exam_questions_random_rank)
    if "ix_exam_questions_random_rank" not in existing_indexes:
        op.create_index("ix_exam_questions_random_rank", "exam_questions", ["random_rank"])
