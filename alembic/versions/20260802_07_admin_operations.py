"""Cria a infraestrutura do centro administrativo."""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260802_07"
down_revision = "20260802_06"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    tables = inspector.get_table_names()

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    with op.batch_alter_table("users") as batch_op:
        if "last_login_at" not in user_columns:
            batch_op.add_column(sa.Column("last_login_at", sa.DateTime(timezone=True)))
            batch_op.create_index("ix_users_last_login_at", ["last_login_at"])

    case_columns = {
        column["name"] for column in inspector.get_columns("clinical_cases")
    }
    with op.batch_alter_table("clinical_cases") as batch_op:
        if "is_premium" not in case_columns:
            batch_op.add_column(
                sa.Column(
                    "is_premium",
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.false(),
                )
            )

    if "visual_challenges" not in tables:
        op.create_table(
            "visual_challenges",
            sa.Column("id", sa.String(120), primary_key=True),
            sa.Column("titulo", sa.String(240), nullable=False),
            sa.Column("especialidade", sa.String(120), nullable=False),
            sa.Column("dificuldade", sa.String(40), nullable=False),
            sa.Column("modalidade", sa.String(80), nullable=False),
            sa.Column("pergunta", sa.Text(), nullable=False),
            sa.Column("imagem_url", sa.String(1000), nullable=False),
            sa.Column("imagem_alt", sa.String(500), nullable=False),
            sa.Column("alternativas", sa.JSON(), nullable=False),
            sa.Column("alternativa_correta_id", sa.String(20), nullable=False),
            sa.Column("diagnostico_correto", sa.String(500), nullable=False),
            sa.Column("explicacao", sa.Text(), nullable=False),
            sa.Column("achados_chave", sa.JSON(), nullable=False),
            sa.Column("fonte_credito", sa.String(240), nullable=False),
            sa.Column("fonte_licenca", sa.String(120), nullable=False),
            sa.Column("fonte_url", sa.String(1000), nullable=False),
            sa.Column("status", sa.String(30), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index(
            "ix_visual_challenges_especialidade", "visual_challenges", ["especialidade"]
        )
        op.create_index(
            "ix_visual_challenges_dificuldade", "visual_challenges", ["dificuldade"]
        )
        op.create_index("ix_visual_challenges_status", "visual_challenges", ["status"])

    if "announcements" not in tables:
        op.create_table(
            "announcements",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("titulo", sa.String(180), nullable=False),
            sa.Column("mensagem", sa.Text(), nullable=False),
            sa.Column("tom", sa.String(30), nullable=False),
            sa.Column("link_texto", sa.String(100)),
            sa.Column("link_url", sa.String(500)),
            sa.Column("ativo", sa.Boolean(), nullable=False),
            sa.Column("inicia_em", sa.DateTime(timezone=True), nullable=False),
            sa.Column("termina_em", sa.DateTime(timezone=True)),
            sa.Column("criado_por", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["criado_por"], ["users.id"]),
        )
        op.create_index("ix_announcements_ativo", "announcements", ["ativo"])

    if "user_activities" not in tables:
        op.create_table(
            "user_activities",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("id_usuario", sa.Integer(), nullable=False),
            sa.Column("evento", sa.String(50), nullable=False),
            sa.Column("tipo_conteudo", sa.String(40)),
            sa.Column("id_conteudo", sa.String(120)),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["id_usuario"], ["users.id"], ondelete="CASCADE"),
        )
        op.create_index(
            "ix_user_activities_id_usuario", "user_activities", ["id_usuario"]
        )
        op.create_index("ix_user_activities_evento", "user_activities", ["evento"])
        op.create_index(
            "ix_user_activities_tipo_conteudo", "user_activities", ["tipo_conteudo"]
        )
        op.create_index(
            "ix_user_activities_created_at", "user_activities", ["created_at"]
        )

    op.execute(
        sa.text(
            "UPDATE clinical_cases SET is_premium = true WHERE nivel_dificuldade = 'Difícil'"
        )
    )


def downgrade() -> None:
    inspector = inspect(op.get_bind())
    tables = inspector.get_table_names()
    for table in ("user_activities", "announcements", "visual_challenges"):
        if table in tables:
            op.drop_table(table)

    case_columns = {
        column["name"] for column in inspector.get_columns("clinical_cases")
    }
    if "is_premium" in case_columns:
        with op.batch_alter_table("clinical_cases") as batch_op:
            batch_op.drop_column("is_premium")

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    if "last_login_at" in user_columns:
        with op.batch_alter_table("users") as batch_op:
            batch_op.drop_column("last_login_at")
