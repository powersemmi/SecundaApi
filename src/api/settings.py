from typing import Annotated

from pydantic import PostgresDsn, AfterValidator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


def set_default_driver_name(url: PostgresDsn) -> PostgresDsn:
    return PostgresDsn(
        str(
            make_url(url.unicode_string()).set(drivername="postgresql+asyncpg")
        )
    )


class Settings(BaseSettings):
    # SERVICE
    BIND: str = "0.0.0.0:8080"
    DEBUG: bool = False
    WORKERS: int = 1
    ROOT_PATH: str = "/api/v1"

    # DB
    PG_URL: Annotated[PostgresDsn, AfterValidator(set_default_driver_name)]

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )


settings = Settings()
