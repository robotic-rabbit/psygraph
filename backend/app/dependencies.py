from functools import lru_cache

from app.config import get_settings
from app.services.scoring import ScoringService


@lru_cache
def get_scoring_service() -> ScoringService:
    return ScoringService()
