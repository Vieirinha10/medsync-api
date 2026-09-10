import os

bind = "0.0.0.0:10000"
# O plano atual possui 512 MB e 0,15 CPU. Dois workers mantêm concorrência sem
# replicar quatro vezes o SDK e os pools HTTP da Synapse.
workers = int(os.getenv("WEB_CONCURRENCY", "2"))
worker_class = "uvicorn.workers.UvicornWorker"
timeout = int(os.getenv("WORKER_TIMEOUT_SECONDS", "90"))
graceful_timeout = 30
keepalive = 5
accesslog = "-"
errorlog = "-"
capture_output = True
loglevel = os.getenv("LOG_LEVEL", "info")


def on_starting(server):
    """Aplica migrações uma única vez antes de iniciar os workers."""
    from services.database_bootstrap import prepare_database

    prepare_database()

    from services.question_quality_repair import run_requested_repair

    run_requested_repair()

    from services.question_quality_funnel import run_requested_quality_funnel

    run_requested_quality_funnel()

    from services.question_quality_taxonomy_resolution import (
        run_requested_taxonomy_resolution,
    )

    run_requested_taxonomy_resolution()

    from services.question_quality_clinical_review import (
        run_requested_clinical_review,
    )

    run_requested_clinical_review()

    from services.question_quality_visual_quarantine import (
        run_requested_visual_quarantine,
    )

    run_requested_visual_quarantine()

    # As agregações do catálogo são feitas uma vez no processo mestre. Os
    # workers herdam o cache pronto e não transferem esse custo ao primeiro aluno.
    from routers.questions import warm_question_catalog_cache

    warm_question_catalog_cache()

    # Evita que conexões abertas pelo processo mestre sejam compartilhadas
    # entre os workers após o fork; cada worker cria seu próprio pool.
    from database import engine

    engine.dispose()


def post_worker_init(worker):
    """Dispara, sem bloquear a API, uma auditoria interna explicitamente solicitada."""
    from services.question_catalog_audit import start_requested_audit

    start_requested_audit()
