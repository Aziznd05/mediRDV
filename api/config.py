from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    database_url: str = f"sqlite:///{RACINE / 'data' / 'medirdv.db'}"
    secret_key: str = "change-moi-en-production-secret-tres-long"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    app_name: str = "MédiRDV API"
    version: str = "1.0.0"

    model_config = SettingsConfigDict(
        env_file=str(RACINE / ".env"),
        extra="ignore",
    )


settings = Settings()