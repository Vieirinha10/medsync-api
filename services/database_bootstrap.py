"""Prepara o banco antes que a API aceite tráfego."""

from pathlib import Path
from threading import Lock

from alembic.config import Config

from alembic import command
from database import SessionLocal
from services.clinical_content import seed_clinical_content

_bootstrap_lock = Lock()
_bootstrap_completed = False


def prepare_database() -> None:
    """Aplica migrações e garante o catálogo clínico uma vez por processo."""
    global _bootstrap_completed

    if _bootstrap_completed:
        return

    with _bootstrap_lock:
        if _bootstrap_completed:
            return

        project_root = Path(__file__).resolve().parents[1]
        config = Config(str(project_root / "alembic.ini"))
        config.set_main_option("script_location", str(project_root / "alembic"))
        command.upgrade(config, "head")

        with SessionLocal() as db:
            seed_clinical_content(db)

        _bootstrap_completed = True
