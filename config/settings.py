"""Application settings and configuration."""

from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MongoDB Configuration
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "finance_assets"
    mongodb_max_pool_size: int = 100
    mongodb_min_pool_size: int = 10

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # CORS Configuration
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000", description="Comma-separated list of allowed origins"
    )

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60

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

    @field_validator("allowed_origins", mode="after")
    @classmethod
    def validate_origins(cls, v: str) -> str:
        """Validate that allowed_origins is not empty or wildcard in production."""
        if not v or v.strip() == "*":
            raise ValueError("allowed_origins must be explicitly set and cannot be '*'")
        return v

    def get_allowed_origins(self) -> List[str]:
        """Get list of allowed origins."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")


settings = Settings()
