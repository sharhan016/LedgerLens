from functools import lru_cache

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_prefix="LEDGERLENS_",
        extra="ignore",
    )

    app_name: str = "LedgerLens API"
    environment: str = Field(default="development", alias="LEDGERLENS_ENV")
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    cors_origins: tuple[str, ...] = (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    )
    database_url: str = "postgresql+asyncpg://ledgerlens:ledgerlens@db:5432/ledgerlens"
    jwt_secret: str = "development-only-secret-change-before-production"
    jwt_issuer: str = "ledgerlens"
    jwt_audience: str = "ledgerlens-api"
    jwt_access_token_minutes: int = 60
    max_upload_bytes: int = 10 * 1024 * 1024
    chunk_size_words: int = 180
    chunk_overlap_words: int = 30
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimensions: int = 384
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    retrieval_candidate_limit: int = 30
    retrieval_result_limit: int = 8
    rrf_constant: int = 60

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return tuple(origin.strip() for origin in value.split(",") if origin.strip())
        return value

    @model_validator(mode="after")
    def require_production_secret(self) -> "Settings":
        if self.environment == "production" and self.jwt_secret.startswith("development-"):
            raise ValueError("LEDGERLENS_JWT_SECRET must be configured in production")
        if len(self.jwt_secret) < 32:
            raise ValueError("LEDGERLENS_JWT_SECRET must contain at least 32 characters")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
