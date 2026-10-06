from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict
from sqlalchemy.engine import URL, make_url


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
    api_docs_enabled: bool = True
    log_level: str = "INFO"
    cors_origins: Annotated[tuple[str, ...], NoDecode] = (
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    )
    database_url: str | None = None
    database_host: str = "db"
    database_port: int = 5432
    database_name: str = "ledgerlens"
    database_user: str = "ledgerlens"
    database_password: str = "ledgerlens"
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
    ml_mode: str = "sentence_transformers"
    retrieval_candidate_limit: int = 30
    retrieval_result_limit: int = 8
    rrf_constant: int = 60
    llm_provider: str = "local_openai"
    llm_base_url: str = "http://host.docker.internal:11434/v1"
    llm_api_key: str | None = None
    llm_model: str = "qwen2.5:7b-instruct"
    llm_timeout_seconds: float = 45.0
    context_max_characters: int = 14_000
    regulatory_api_mode: str = "fixture"
    regulatory_api_url: str | None = None
    regulatory_fixture_path: str = "../data/sample/api/regulatory-bulletins.json"
    regulatory_api_timeout_seconds: float = 5.0
    semantic_cache_similarity_threshold: float = 0.92
    semantic_cache_ttl_minutes: int = 60
    demo_auth_enabled: bool = True
    demo_seed_enabled: bool = False
    demo_data_path: str = "../data/sample/banking"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return tuple(origin.strip() for origin in value.split(",") if origin.strip())
        return value

    @property
    def database_connection_url(self) -> URL:
        if self.database_url:
            return make_url(self.database_url)
        return URL.create(
            "postgresql+asyncpg",
            username=self.database_user,
            password=self.database_password,
            host=self.database_host,
            port=self.database_port,
            database=self.database_name,
        )

    @model_validator(mode="after")
    def require_production_secret(self) -> "Settings":
        insecure_secrets = {
            "development-only-secret-change-before-production",
            "replace-with-at-least-32-random-characters",
        }
        if self.environment == "production" and self.jwt_secret in insecure_secrets:
            raise ValueError("LEDGERLENS_JWT_SECRET must be configured in production")
        if self.environment == "production" and self.demo_auth_enabled:
            raise ValueError("LEDGERLENS_DEMO_AUTH_ENABLED must be false in production")
        if self.environment == "production" and self.ml_mode == "deterministic_demo":
            raise ValueError("deterministic demo ML cannot be used in production")
        if self.environment == "production" and self.llm_provider == "demo_extractive":
            raise ValueError("demo extractive generation cannot be used in production")
        if self.ml_mode not in {"sentence_transformers", "deterministic_demo"}:
            raise ValueError("LEDGERLENS_ML_MODE must be sentence_transformers or deterministic_demo")
        if len(self.jwt_secret) < 32:
            raise ValueError("LEDGERLENS_JWT_SECRET must contain at least 32 characters")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
