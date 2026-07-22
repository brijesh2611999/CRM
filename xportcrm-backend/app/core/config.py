 # Settings (env vars)
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    SECRET_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()