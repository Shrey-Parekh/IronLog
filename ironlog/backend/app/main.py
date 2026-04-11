from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title="IronLog API", version="1.0.0")

    # Parse CORS origins from comma-separated string
    cors_origins = [origin.strip() for origin in settings.cors_origins.split(",")]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    from app.api.router import api_router
    app.include_router(api_router, prefix="/api")

    return app


app = create_app()
