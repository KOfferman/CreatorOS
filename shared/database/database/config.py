from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_API_DIR = Path(__file__).resolve().parents[3] / "api"


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(_API_DIR / ".env"), str(_API_DIR / ".env.local")),
        extra="ignore",
    )

    database_url: str = "mysql+pymysql://creatoros:creatoros@localhost:3306/creatoros"

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_mysql_url(cls, value: str) -> str:
        if isinstance(value, str) and value.startswith("mysql://"):
            return value.replace("mysql://", "mysql+pymysql://", 1)
        return value
