from importlib import metadata
from typing import Annotated

from pydantic import AfterValidator, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


def _set_default_driver_name(url: PostgresDsn) -> PostgresDsn:
    return PostgresDsn(
        str(
            make_url(url.unicode_string()).set(drivername="postgresql+asyncpg")
        )
    )


def _load_project_metadata(dist_name: str) -> tuple[str | None, str | None]:
    try:
        meta = metadata.metadata(dist_name)
    except metadata.PackageNotFoundError:
        return None, None
    return meta.get("Name"), meta.get("Version")


class Settings(BaseSettings):
    # SERVICE
    BIND: str = "0.0.0.0:8080"
    DEBUG: bool = False
    WORKERS: int = 1
    ROOT_PATH: str = "/api/v1"
    API_KEY: str = "test-api-key"

    # DB
    PG_URL: Annotated[PostgresDsn, AfterValidator(_set_default_driver_name)]

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )


DIST_NAME = "secundaapi"
_service_name, _api_version = _load_project_metadata(DIST_NAME)
SERVICE_NAME = _service_name or DIST_NAME
API_VERSION = _api_version or "0.0.0"

settings = Settings()
