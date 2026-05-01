from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    headless: bool = True
    browser: str = "chromium"
    request_delay_ms: int = 1000
    user_agent: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
