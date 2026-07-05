from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

# NOTE: Some weird thing idk why it has to be like this please fix if reading this in the future
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DATABASE_PATH: Path = BASE_DIR / "data" / "psygraph.db"

    # TODO: move this to somewhere else later
    QUIZ_VERSIONS: dict[str, list[int]] = {
        "quick": list(range(1, 5)),  # Questions 1 to 4
        "recommended": list(range(1, 37)),
        "long": list(range(1, 101)),
    }
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    model_config = {"env_file": ".env"}


settings = Settings()


@lru_cache  # not sure if this improves performance
def get_settings():
    return Settings()
