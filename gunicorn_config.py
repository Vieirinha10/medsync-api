bind = "0.0.0.0:10000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"


def on_starting(server):
    """Aplica migrações uma única vez antes de iniciar os workers."""
    from services.database_bootstrap import prepare_database

    prepare_database()
