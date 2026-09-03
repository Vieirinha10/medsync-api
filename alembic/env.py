import os
from logging.config import fileConfig

from alembic import context
import database
from models import Base

config = context.config
target_db_url = os.getenv("DATABASE_URL") or database.DATABASE_URL
if target_db_url.startswith("postgres://"):
    target_db_url = target_db_url.replace("postgres://", "postgresql+psycopg://", 1)
elif target_db_url.startswith("postgresql://") and not target_db_url.startswith("postgresql+"):
    target_db_url = target_db_url.replace("postgresql://", "postgresql+psycopg://", 1)
config.set_main_option("sqlalchemy.url", target_db_url.replace("%", "%%"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import create_engine

    target_url = config.get_main_option("sqlalchemy.url") or database.DATABASE_URL
    if target_url.startswith("postgres://"):
        target_url = target_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif target_url.startswith("postgresql://") and not target_url.startswith("postgresql+"):
        target_url = target_url.replace("postgresql://", "postgresql+psycopg://", 1)
    connect_args = {"check_same_thread": False} if target_url.startswith("sqlite") else {}
    connectable = create_engine(target_url, connect_args=connect_args, pool_pre_ping=True)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
