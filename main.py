from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from middleware import RateLimitMiddleware, SecurityAndObservabilityMiddleware
from routers import (
    admin,
    cases,
    content,
    error_notebook,
    learning_paths,
    payments,
    progress,
    questions,
    simulations,
    system,
    users,
)
from services.database_bootstrap import prepare_database
from settings import cors_origins, rate_limit_enabled


@asynccontextmanager
async def lifespan(_: FastAPI):
    prepare_database()
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title="API MEDSYNC",
        version="0.5.0",
        lifespan=lifespan,
    )
    origins = cors_origins()
    application.add_middleware(
        SecurityAndObservabilityMiddleware,
    )
    application.add_middleware(
        RateLimitMiddleware,
        enabled=rate_limit_enabled(),
    )
    # O CORS deve ser a camada externa para incluir os cabeçalhos também
    # quando uma rota falhar antes de produzir uma resposta normal.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials="*" not in origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(system.router)
    application.include_router(users.router)
    application.include_router(cases.router)
    application.include_router(content.router)
    application.include_router(simulations.router)
    application.include_router(progress.router)
    application.include_router(error_notebook.router)
    application.include_router(learning_paths.router)
    application.include_router(payments.router)
    application.include_router(questions.router)
    application.include_router(admin.router)
    return application


app = create_app()
