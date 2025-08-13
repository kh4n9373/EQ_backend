from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    frontend_url: str = "http://localhost:3001/"
    database_url: str = "postgresql://eq_user:eq_pass@localhost:5432/eq_test"
    redis_url: str = "redis://localhost:6379/0"

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 30

    google_client_id: str
    google_client_secret: str

    openai_api_key: str
    openai_base_url: str

    cors_extra_origins: List[str] = Field(default=[], alias="CORS_ORIGINS")

    @property
    def cors_origin(self) -> List[str]:
        base_origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
        ]
        return list(set(base_origins + self.cors_extra_origins))

    environment: str = "dev"

    @property
    def debug(self) -> bool:
        return self.environment == "dev"

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore"
    )


settings = Settings()
