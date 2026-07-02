from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    llm_provider: str
    openai_api_key: str
    openai_model: str

    cors_allow_origins: list[str] = ["http://localhost:3000"]
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    cors_allow_credentials: bool = True

    oauth_redirect_base_url: str = "http://localhost:8000/api/v1/integrations/oauth"
    google_client_id: str = ""
    google_client_secret: str = ""
    meta_app_id: str = ""
    meta_app_secret: str = ""
    tiktok_client_key: str = ""
    tiktok_client_secret: str = ""
    pinterest_app_id: str = ""
    pinterest_app_secret: str = ""

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
