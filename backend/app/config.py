from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./bingo.db"
    CRAWLER_INTERVAL_MINUTES: int = 6
    CRAWLER_RELAX_TLS_STRICT: bool = False
    ENV: str = "development"
    BINGO_FIRST_DRAW_HOUR: int = 7
    BINGO_FIRST_DRAW_MINUTE: int = 5
    ALLOWED_ORIGINS: List[str] = []

    model_config = {"env_file": ".env"}


settings = Settings()
