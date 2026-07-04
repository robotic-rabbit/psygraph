from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

# Find the backend folder automatically
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Pure, clean file path. No slashes to count.
    DATABASE_PATH: Path = BASE_DIR / "data" / "psygraph.db"

    QUIZ_VERSIONS: dict[str, list[int]] = {
        "quick": [],
        "recommended": [],
        "long": [],
    }
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    model_config = {"env_file": ".env"}


settings = Settings()


@lru_cache
def get_settings():
    return Settings()
