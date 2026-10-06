import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_documented_placeholder_jwt_secret() -> None:
    with pytest.raises(ValidationError, match="JWT_SECRET must be configured"):
        Settings(
            LEDGERLENS_ENV="production",
            jwt_secret="replace-with-at-least-32-random-characters",
            demo_auth_enabled=False,
            ml_mode="sentence_transformers",
            llm_provider="openrouter",
        )


def test_showcase_mode_keeps_demo_adapters_distinct_from_production() -> None:
    settings = Settings(
        LEDGERLENS_ENV="showcase",
        jwt_secret="showcase-secret-with-at-least-thirty-two-characters",
        demo_auth_enabled=True,
        ml_mode="deterministic_demo",
        llm_provider="demo_extractive",
        api_docs_enabled=False,
    )

    assert settings.environment == "showcase"
    assert settings.api_docs_enabled is False


def test_cors_origins_accept_comma_separated_deployment_value() -> None:
    settings = Settings(
        LEDGERLENS_ENV="showcase",
        jwt_secret="showcase-secret-with-at-least-thirty-two-characters",
        cors_origins="https://ledgerlens.sharhan.dev,https://admin.example.test",
    )

    assert settings.cors_origins == (
        "https://ledgerlens.sharhan.dev",
        "https://admin.example.test",
    )
