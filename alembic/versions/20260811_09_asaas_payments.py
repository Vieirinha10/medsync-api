"""Adiciona pedidos, acesso Premium e eventos da Asaas."""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260811_09"
down_revision = "20260811_08"
branch_labels = None
depends_on = None


def upgrade() -> None:
    tables = inspect(op.get_bind()).get_table_names()

    if "payment_orders" not in tables:
        op.create_table(
            "payment_orders",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("id_usuario", sa.Integer(), nullable=False),
            sa.Column("plano_id", sa.String(40), nullable=False),
            sa.Column("valor_centavos", sa.Integer(), nullable=False),
            sa.Column("moeda", sa.String(3), nullable=False),
            sa.Column("tipo_cobranca", sa.String(30), nullable=False),
            sa.Column("forma_pagamento", sa.String(30), nullable=False),
            sa.Column("status", sa.String(30), nullable=False),
            sa.Column("asaas_checkout_id", sa.String(120), unique=True),
            sa.Column("checkout_url", sa.String(1000)),
            sa.Column("ultimo_pagamento_asaas_id", sa.String(120)),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("paid_at", sa.DateTime(timezone=True)),
            sa.ForeignKeyConstraint(["id_usuario"], ["users.id"], ondelete="CASCADE"),
        )
        op.create_index(
            "ix_payment_orders_id_usuario", "payment_orders", ["id_usuario"]
        )
        op.create_index("ix_payment_orders_plano_id", "payment_orders", ["plano_id"])
        op.create_index("ix_payment_orders_status", "payment_orders", ["status"])
        op.create_index(
            "ix_payment_orders_asaas_checkout_id",
            "payment_orders",
            ["asaas_checkout_id"],
            unique=True,
        )

    if "user_entitlements" not in tables:
        op.create_table(
            "user_entitlements",
            sa.Column("id_usuario", sa.Integer(), primary_key=True),
            sa.Column("plano_id", sa.String(40), nullable=False),
            sa.Column("status", sa.String(30), nullable=False),
            sa.Column("valido_ate", sa.DateTime(timezone=True), nullable=False),
            sa.Column("renovacao_automatica", sa.Boolean(), nullable=False),
            sa.Column("asaas_subscription_id", sa.String(120)),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["id_usuario"], ["users.id"], ondelete="CASCADE"),
        )
        op.create_index("ix_user_entitlements_status", "user_entitlements", ["status"])
        op.create_index(
            "ix_user_entitlements_valido_ate", "user_entitlements", ["valido_ate"]
        )
        op.create_index(
            "ix_user_entitlements_asaas_subscription_id",
            "user_entitlements",
            ["asaas_subscription_id"],
        )

    if "payment_grants" not in tables:
        op.create_table(
            "payment_grants",
            sa.Column("asaas_payment_id", sa.String(120), primary_key=True),
            sa.Column("pedido_id", sa.String(36), nullable=False),
            sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(
                ["pedido_id"], ["payment_orders.id"], ondelete="CASCADE"
            ),
        )
        op.create_index("ix_payment_grants_pedido_id", "payment_grants", ["pedido_id"])

    if "asaas_webhook_events" not in tables:
        op.create_table(
            "asaas_webhook_events",
            sa.Column("id", sa.String(160), primary_key=True),
            sa.Column("tipo", sa.String(80), nullable=False),
            sa.Column("payload", sa.JSON(), nullable=False),
            sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index(
            "ix_asaas_webhook_events_tipo", "asaas_webhook_events", ["tipo"]
        )


def downgrade() -> None:
    tables = inspect(op.get_bind()).get_table_names()
    for table in (
        "asaas_webhook_events",
        "payment_grants",
        "user_entitlements",
        "payment_orders",
    ):
        if table in tables:
            op.drop_table(table)
