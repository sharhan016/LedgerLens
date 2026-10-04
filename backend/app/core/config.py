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

    @model_validator(mode="after")
    def require_production_secret(self) -> "Settings":
        if self.environment == "production" and self.jwt_secret.startswith("development-"):
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
