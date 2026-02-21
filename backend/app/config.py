from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./bingo.db"
    CRAWLER_INTERVAL_MINUTES: int = 6
    CRAWLER_RELAX_TLS_STRICT: bool = False
    ENV: str = "development"

    model_config = {"env_file": ".env"}


settings = Settings()
