from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Base de données (SQLite en attendant PostgreSQL)
    database_url: str = f"sqlite:///{RACINE / 'data' / 'medirdv.db'}"

    # Sécurité
    secret_key: str = "change-moi-en-production-secret-tres-long"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8  # 8h

    # App
    app_name: str = "MédiRDV API"
    version: str = "1.0.0"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()