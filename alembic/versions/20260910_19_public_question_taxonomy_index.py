"""Otimiza a navegação da taxonomia pública de questões.

Revision ID: 20260910_19
Revises: 20260908_18
Create Date: 2026-09-10
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260910_19"
down_revision: str | None = "20260908_18"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

INDEX_NAME = "ix_exam_questions_public_taxonomy"


def upgrade() -> None:
    indexes = {
        index["name"]
        for index in sa.inspect(op.get_bind()).get_indexes("exam_questions")
    }
    if INDEX_NAME not in indexes:
        op.create_index(
            INDEX_NAME,
            "exam_questions",
            [
                "catalog_version",
                "status",
                "quality_status",
                "especialidade",
                "tema",
                "subtema",
            ],
        )


def downgrade() -> None:
    indexes = {
        index["name"]
        for index in sa.inspect(op.get_bind()).get_indexes("exam_questions")
    }
    if INDEX_NAME in indexes:
        op.drop_index(INDEX_NAME, table_name="exam_questions")
