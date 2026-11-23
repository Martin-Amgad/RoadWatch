from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .app_services import AppServices
from .config import Settings
from .constants import API_PREFIX, API_VERSION, STAFF_API_KEY_HEADER
from .errors import register_error_handlers
from .routes import analyze, health, reports

ServicesFactory = Callable[[Settings], AppServices]

ALLOWED_METHODS = ["GET", "POST", "PATCH"]
ALLOWED_HEADERS = [STAFF_API_KEY_HEADER, "Content-Type"]


def create_app(settings: Settings, build_services: ServicesFactory) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        services = build_services(settings)
        services.detector.warm_up()
        app.state.services = services
        try:
            yield
        finally:
            services.shutdown()

    app = FastAPI(title="RoadWatch API", version=API_VERSION, lifespan=lifespan)
    app.state.settings = settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.dashboard_origin],
        allow_methods=ALLOWED_METHODS,
        allow_headers=ALLOWED_HEADERS,
    )
    register_error_handlers(app)
    for router in (health.router, analyze.router, reports.router):
        app.include_router(router, prefix=API_PREFIX)
    return app


def create_production_app() -> FastAPI:
    from .wiring import build_production_services

    return create_app(Settings.from_env(), build_production_services)
