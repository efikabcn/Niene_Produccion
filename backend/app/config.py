from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # PostgreSQL (our database)
    database_url: str = "postgresql://niene:niene_secure_2026@db:5432/niene_produccion"

    # SAGE MSSQL (read-only)
    sage_db_host: Optional[str] = None
    sage_db_instance: Optional[str] = None  # Named instance (e.g. CONTROL_SM)
    sage_db_port: int = 1433
    sage_db_name: Optional[str] = None
    sage_db_user: Optional[str] = None
    sage_db_password: Optional[str] = None

    # App
    app_env: str = "production"
    secret_key: str = "change-this-in-production"

    @property
    def sage_configured(self) -> bool:
        """Check if SAGE connection is configured."""
        return all([self.sage_db_host, self.sage_db_name, self.sage_db_user])

    class Config:
        env_file = ".env"


settings = Settings()
