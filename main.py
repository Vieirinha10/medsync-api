from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from middleware import RateLimitMiddleware, SecurityAndObservabilityMiddleware
from routers import (
    admin,
    cases,
    error_notebook,
    learning_paths,
    progress,
    simulations,
    system,
    users,
)
from settings import cors_origins, rate_limit_enabled


def create_app() -> FastAPI:
    application = FastAPI(title="API MEDSYNC", version="0.4.0")
    origins = cors_origins()
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials="*" not in origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(
        RateLimitMiddleware,
        enabled=rate_limit_enabled(),
    )
    application.add_middleware(SecurityAndObservabilityMiddleware)

    application.include_router(system.router)
    application.include_router(users.router)
    application.include_router(cases.router)
    application.include_router(simulations.router)
    application.include_router(progress.router)
    application.include_router(error_notebook.router)
    application.include_router(learning_paths.router)
    application.include_router(admin.router)
    return application


app = create_app()
