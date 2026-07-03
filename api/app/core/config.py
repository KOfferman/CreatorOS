from functools import lru_cache
from typing import Annotated

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", ".env.local"), extra="ignore")

    environment: str
    log_level: str
    auth_secret: str
    auth_url: str
    auth_enabled: bool = True
    auth_jwt_algorithm: str = "HS256"
    auth_access_token_exp_minutes: int = 60

    database_url: str
    celery_broker_url: str
    celery_result_backend: str
    api_rate_limit_per_minute: int = 120

    llm_provider: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    llm_model: str = ""
    openclaw_gateway_url: str = "http://127.0.0.1:18789"
    openclaw_gateway_token: str = ""
    openclaw_model: str = "openclaw/default"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "hermes3"
    openrouter_api_key: str = ""
    openrouter_model: str = "nousresearch/hermes-3-llama-3.1-70b"

    def resolved_llm_model(self) -> str:
        if self.llm_model.strip():
            return self.llm_model.strip()
        if self.llm_provider.strip().lower() == "openai":
            return self.openai_model
        if self.llm_provider.strip().lower() == "openclaw":
            return self.openclaw_model
        if self.llm_provider.strip().lower() in {"hermes", "hermes-local", "ollama"}:
            return self.ollama_model
        if self.llm_provider.strip().lower() == "openrouter":
            return self.openrouter_model
        return self.openai_model or "gpt-4o-mini"

    cors_allow_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]
    cors_allow_methods: Annotated[list[str], NoDecode] = ["*"]
    cors_allow_headers: Annotated[list[str], NoDecode] = ["*"]
    cors_allow_credentials: bool = True

    oauth_redirect_base_url: str = "http://localhost:8000/api/v1/integrations/oauth"
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = Field(
        default="http://localhost:8000/api/v1/integrations/oauth/youtube/callback",
        validation_alias=AliasChoices("GOOGLE_REDIRECT_URI", "GOOGLE_AUTH_REDIRECT_URI"),
    )
    meta_app_id: str = Field(default="", validation_alias=AliasChoices("META_APP_ID", "META_CLIENT_ID"))
    meta_app_secret: str = Field(
        default="", validation_alias=AliasChoices("META_APP_SECRET", "META_CLIENT_SECRET")
    )
    meta_redirect_uri: str = Field(
        default="http://localhost:8000/api/v1/integrations/oauth/instagram/callback",
        validation_alias=AliasChoices("META_REDIRECT_URI", "INSTAGRAM_REDIRECT_URI"),
    )
    instagram_config_id: str = ""
    tiktok_client_key: str = ""
    tiktok_client_secret: str = ""
    pinterest_app_id: str = ""
    pinterest_app_secret: str = ""

    def resolved_token_encryption_key(self) -> str:
        return self.auth_secret

    @field_validator("cors_allow_origins", "cors_allow_methods", "cors_allow_headers", mode="before")
    @classmethod
    def split_csv_to_list(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_key(cls, value: str) -> str:
        if value and len(value.strip()) < 16:
            raise ValueError("OPENAI_API_KEY looks invalid (too short).")
        return value

    @field_validator("auth_enabled", mode="before")
    @classmethod
    def enforce_auth_enabled(cls, value: object) -> bool:
        return True

    @model_validator(mode="after")
    def validate_security_settings(self):
        if len(self.auth_secret.strip()) < 24:
            raise ValueError("AUTH_SECRET must be at least 24 characters long.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
