from pydantic import BaseModel
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class RunApp(BaseModel):
    host: str = '0.0.0.0'
    port: int = 8000


class ApiConfig(BaseModel):
    prefix: str = "/api"


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class Settings(BaseSettings):
    app: RunApp = RunApp()
    api: ApiConfig = ApiConfig()
    db: DatabaseConfig


settings = Settings()
