from pydantic import BaseModel
from pydantic_settings import BaseSettings


class RunApp(BaseModel):
    host: str = '0.0.0.0'
    port: int = 8000


class ApiConfig(BaseModel):
    prefix: str = "/api"


class Settings(BaseSettings):
    app: RunApp = RunApp()
    api: ApiConfig = ApiConfig()


settings = Settings()
