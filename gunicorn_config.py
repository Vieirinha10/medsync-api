import os

bind = "0.0.0.0:10000"
# O plano atual possui 512 MB e 0,15 CPU. Dois workers mantêm concorrência sem
# replicar quatro vezes o SDK e os pools HTTP da Synapse.
workers = int(os.getenv("WEB_CONCURRENCY", "2"))
worker_class = "uvicorn.workers.UvicornWorker"
timeout = int(os.getenv("WORKER_TIMEOUT_SECONDS", "90"))
graceful_timeout = 30
keepalive = 5


def on_starting(server):
    """Aplica migrações uma única vez antes de iniciar os workers."""
    from services.database_bootstrap import prepare_database

    prepare_database()
