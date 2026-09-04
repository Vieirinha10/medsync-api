import importlib.util
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
import sqlalchemy as sa

MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "20260904_18_manual_premium_grant.py"
)
SPEC = importlib.util.spec_from_file_location("manual_premium_grant", MIGRATION_PATH)
assert SPEC and SPEC.loader
migration = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(migration)


def _tables(metadata):
    users = sa.Table(
        "users",
        metadata,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String, nullable=False),
    )
    entitlements = sa.Table(
        "user_entitlements",
        metadata,
        sa.Column("id_usuario", sa.Integer, primary_key=True),
        sa.Column("plano_id", sa.String, nullable=False),
        sa.Column("status", sa.String, nullable=False),
        sa.Column("valido_ate", sa.DateTime(timezone=True), nullable=False),
        sa.Column("renovacao_automatica", sa.Boolean, nullable=False),
        sa.Column("asaas_subscription_id", sa.String),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    return users, entitlements


def test_grant_creates_thirty_day_entitlement_for_authorized_account():
    engine = sa.create_engine("sqlite:///:memory:")
    metadata = sa.MetaData()
    users, entitlements = _tables(metadata)
    metadata.create_all(engine)
    now = datetime(2026, 9, 4, 15, 0, tzinfo=UTC)

    with engine.begin() as connection:
        connection.execute(
            sa.insert(users),
            {"id": 10, "email": "LUCAS10_ABARE@HOTMAIL.COM"},
        )
        valid_until = migration._grant_premium(
            connection,
            required=True,
            now=now,
        )
        entitlement = connection.execute(sa.select(entitlements)).one()

    assert valid_until == now + timedelta(days=30)
    assert entitlement.id_usuario == 10
    assert entitlement.plano_id == "avulso"
    assert entitlement.status == "ativo"
    assert entitlement.renovacao_automatica is False
    assert entitlement.asaas_subscription_id is None


def test_grant_preserves_active_balance_and_adds_thirty_days():
    engine = sa.create_engine("sqlite:///:memory:")
    metadata = sa.MetaData()
    users, entitlements = _tables(metadata)
    metadata.create_all(engine)
    now = datetime(2026, 9, 4, 15, 0, tzinfo=UTC)
    previous_expiry = now + timedelta(days=7)

    with engine.begin() as connection:
        connection.execute(
            sa.insert(users),
            {"id": 11, "email": "lucas10_abare@hotmail.com"},
        )
        connection.execute(
            sa.insert(entitlements),
            {
                "id_usuario": 11,
                "plano_id": "recorrente",
                "status": "ativo",
                "valido_ate": previous_expiry,
                "renovacao_automatica": True,
                "asaas_subscription_id": "sub_test",
                "updated_at": now - timedelta(days=1),
            },
        )
        valid_until = migration._grant_premium(
            connection,
            required=True,
            now=now,
        )
        entitlement = connection.execute(sa.select(entitlements)).one()

    assert valid_until == previous_expiry + timedelta(days=30)
    assert entitlement.plano_id == "recorrente"
    assert entitlement.status == "ativo"
    assert entitlement.renovacao_automatica is True
    assert entitlement.asaas_subscription_id == "sub_test"


def test_required_grant_fails_when_authorized_account_does_not_exist():
    engine = sa.create_engine("sqlite:///:memory:")
    metadata = sa.MetaData()
    _tables(metadata)
    metadata.create_all(engine)

    with (
        engine.begin() as connection,
        pytest.raises(RuntimeError, match="não foi encontrada"),
    ):
        migration._grant_premium(connection, required=True)
