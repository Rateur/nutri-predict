import os
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Chemins absolus pour le chargement robuste du .env
current_dir = os.path.dirname(os.path.abspath(__file__)) # app/core/
backend_dir = os.path.dirname(os.path.dirname(current_dir)) # backend/
project_root = os.path.dirname(backend_dir)
env_path = os.path.join(project_root, ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=env_path,
        env_ignore_empty=True,
        extra="ignore"
    )

    # PROJECT
    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"

    # DATABASE
    DATABASE_URL: str

    # SECURITY
    ENCRYPTION_KEY: str
    API_KEY: str
    ALLOWED_ORIGINS: str = "http://localhost:8000,http://localhost:3000,http://127.0.0.1:5500"



settings = Settings()
