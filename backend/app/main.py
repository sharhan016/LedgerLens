from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.ingestion import router as ingestion_router
from app.api.retrieval import router as retrieval_router
from app.api.system import router as system_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Authorization-aware banking knowledge and retrieval API.",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )
    application.include_router(system_router)
    application.include_router(auth_router)
    application.include_router(documents_router)
    application.include_router(ingestion_router)
    application.include_router(retrieval_router)
    return application


app = create_app()
