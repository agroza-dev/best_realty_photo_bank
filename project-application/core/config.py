import os
from pathlib import Path

from pydantic import BaseModel
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunApp(BaseModel):
    host: str = '0.0.0.0'
    port: int = 8000


class ApiV1Config(BaseModel):
    prefix: str = "/v1"
    users: str = "/users"


class ApiConfig(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Config = ApiV1Config()


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    model_config = SettingsConfigDict(
        env_file=(os.path.join(BASE_DIR, ".env.template"), os.path.join(BASE_DIR, ".env")),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__"
    )
    app: RunApp = RunApp()
    api: ApiConfig = ApiConfig()
    db: DatabaseConfig


settings = Settings()
