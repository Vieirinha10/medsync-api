bind = "0.0.0.0:10000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"


def on_starting(server):
    """Aplica migrações uma única vez antes de iniciar os workers."""
    from alembic.config import Config

    from alembic import command

    command.upgrade(Config("alembic.ini"), "head")

    from database import SessionLocal
    from services.clinical_content import seed_clinical_content

    with SessionLocal() as db:
        seed_clinical_content(db)
