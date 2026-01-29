"""Configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    twitch_client_id: str
    twitch_client_secret: str

    # API configuration
    twitch_api_base_url: str = "https://api.twitch.tv/helix"
    twitch_auth_url: str = "https://id.twitch.tv/oauth2/token"

    # Rate limiting
    rate_limit_requests: int = 800
    rate_limit_period: int = 60  # seconds


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()
