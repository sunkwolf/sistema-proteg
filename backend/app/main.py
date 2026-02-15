import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.exceptions import AppException, app_exception_handler, unhandled_exception_handler
from app.core.middleware import setup_middleware
from app.core.redis import close_redis

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando %s v%s", settings.APP_NAME, settings.APP_VERSION)
    yield
    await close_redis()
    logger.info("Deteniendo %s", settings.APP_NAME)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        lifespan=lifespan,
    )

    # Middleware
    setup_middleware(app)

    # Exception handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # Routers
    _include_routers(app)

    return app


def _include_routers(app: FastAPI):
    prefix = settings.API_V1_PREFIX

    from app.modules.auth.router import router as auth_router
    from app.modules.employees.router import router as employees_router
    from app.modules.clients.router import router as clients_router
    from app.modules.vehicles.router import router as vehicles_router
    from app.modules.coverages.router import router as coverages_router
    from app.modules.policies.router import router as policies_router
    from app.modules.payments.router import router as payments_router

    app.include_router(auth_router, prefix=f"{prefix}/auth", tags=["Auth"])
    app.include_router(employees_router, prefix=f"{prefix}/employees", tags=["Employees"])
    app.include_router(clients_router, prefix=f"{prefix}/clients", tags=["Clients"])
    app.include_router(vehicles_router, prefix=f"{prefix}/vehicles", tags=["Vehicles"])
    app.include_router(coverages_router, prefix=f"{prefix}/coverages", tags=["Coverages"])
    app.include_router(policies_router, prefix=f"{prefix}/policies", tags=["Policies"])
    app.include_router(payments_router, prefix=f"{prefix}/payments", tags=["Payments"])


app = create_app()
