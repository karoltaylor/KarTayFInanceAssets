"""Application settings and configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MongoDB Configuration
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "finance_assets"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # Scheduler Configuration
    enable_scheduler: bool = True
    daily_run_hour: int = 1
    daily_run_minute: int = 0

    # External API Keys
    alpha_vantage_api_key: str = ""
    fred_api_key: str = ""

    # Data Configuration
    historical_years: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


settings = Settings()

