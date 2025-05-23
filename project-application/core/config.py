import os
from dataclasses import field
from functools import cached_property
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).resolve().parent.parent

class RunApp(BaseModel):
    host: str = '0.0.0.0'
    port: int = 8000
    templates: str = os.path.join(BASE_DIR, "templates/common")
    super_admin: int = 999999999

class ApiV1Config(BaseModel):
    prefix: str = "/v1"
    users: str = "/users"

class ApiConfig(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Config = ApiV1Config()

class WebAppConfig(BaseModel):
    url: str = ""
    users_url: str = ""
    templates: str = os.path.join(BASE_DIR, "templates/web")
    host: str = '0.0.0.0'
    port: int = 8008

class DatabaseConfig(BaseModel):
    path: str
    echo: bool = False
    echo_pool: bool = False
    persistence: str = os.path.join(BASE_DIR, "var/db/persistence.pkl")

    def resolve_dsn(self, base_dir: Path) -> str:
        return f"sqlite+aiosqlite:///{(base_dir / self.path).resolve()}"

    # лениво получаем dsn без передачи вручную
    @cached_property
    def dsn(self) -> str:
        return self.resolve_dsn(BASE_DIR)

    naming_convention: dict[str, str] = field(default_factory=lambda: {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })


class BotConfig(BaseModel):
    token: str = ''
    templates: str = os.path.join(BASE_DIR, "templates/bot")
    builder: dict[str, float] = field(default_factory=lambda: {
        'connect': 3.0,
        'read': 10.0,
        'write': 10.0,
        'pool': 2.0,
    })

class ImageConfig(BaseModel):
    path: str = os.path.join(BASE_DIR, "var/images")

class LoggerConfig(BaseModel):
    path: str = os.path.join(BASE_DIR, "var/logs")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(os.path.join(BASE_DIR, ".env"), os.path.join(BASE_DIR, ".env.advanced")),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__"
    )
    app: RunApp = RunApp()
    api: ApiConfig = ApiConfig()
    db: DatabaseConfig
    bot: BotConfig = BotConfig()
    logs: LoggerConfig = LoggerConfig()
    images: ImageConfig = ImageConfig()
    web_app: WebAppConfig = WebAppConfig()


settings = Settings()
