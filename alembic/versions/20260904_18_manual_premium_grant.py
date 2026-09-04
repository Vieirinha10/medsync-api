"""Concede 30 dias de Premium a uma conta autorizada pelo administrador.

Revision ID: 20260904_18
Revises: 20260902_17
Create Date: 2026-09-04
"""

import hashlib
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

import sqlalchemy as sa
from sqlalchemy.engine import Connection

from alembic import op

revision: str = "20260904_18"
down_revision: str | None = "20260902_17"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TARGET_EMAIL_SHA256 = "66f4700ed81f69880490dcbb7339139b7d9212d85e6d1265cca54dd37a3acab7"
GRANT_DAYS = 30


def _email_digest(email: str) -> str:
    return hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()


def _grant_premium(
    bind: Connection,
    *,
    required: bool,
    now: datetime | None = None,
) -> datetime | None:
    users = sa.table(
        "users",
        sa.column("id", sa.Integer),
        sa.column("email", sa.String),
    )
    entitlements = sa.table(
        "user_entitlements",
        sa.column("id_usuario", sa.Integer),
        sa.column("plano_id", sa.String),
        sa.column("status", sa.String),
        sa.column("valido_ate", sa.DateTime(timezone=True)),
        sa.column("renovacao_automatica", sa.Boolean),
        sa.column("asaas_subscription_id", sa.String),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )

    user_id = next(
        (
            row.id
            for row in bind.execute(sa.select(users.c.id, users.c.email))
            if _email_digest(row.email) == TARGET_EMAIL_SHA256
        ),
        None,
    )
    if user_id is None:
        if required:
            raise RuntimeError(
                "A conta autorizada para o grant Premium não foi encontrada."
            )
        return None

    grant_started_at = now or datetime.now(UTC)
    current = bind.execute(
        sa.select(
            entitlements.c.status,
            entitlements.c.valido_ate,
        ).where(entitlements.c.id_usuario == user_id)
    ).one_or_none()

    if current is None:
        valid_until = grant_started_at + timedelta(days=GRANT_DAYS)
        bind.execute(
            sa.insert(entitlements).values(
                id_usuario=user_id,
                plano_id="avulso",
                status="ativo",
                valido_ate=valid_until,
                renovacao_automatica=False,
                asaas_subscription_id=None,
                updated_at=grant_started_at,
            )
        )
    else:
        current_expiry = current.valido_ate
        if current_expiry.tzinfo is None:
            current_expiry = current_expiry.replace(tzinfo=UTC)
        base = max(grant_started_at, current_expiry)
        valid_until = base + timedelta(days=GRANT_DAYS)
        bind.execute(
            sa.update(entitlements)
            .where(entitlements.c.id_usuario == user_id)
            .values(
                status="ativo",
                valido_ate=valid_until,
                updated_at=grant_started_at,
            )
        )

    return valid_until


def upgrade() -> None:
    bind = op.get_bind()
    valid_until = _grant_premium(
        bind,
        required=bind.dialect.name == "postgresql",
    )
    if valid_until is not None:
        print(
            "manual_premium_grant_applied "
            f"target={TARGET_EMAIL_SHA256[:12]} valid_until={valid_until.isoformat()}"
        )


def downgrade() -> None:
    # Grants de acesso não são revogados automaticamente por rollback de schema:
    # a conta pode ter recebido ou renovado uma assinatura após esta revisão.
    pass
