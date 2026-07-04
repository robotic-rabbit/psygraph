from fastapi import APIRouter, Depends, HTTPException
from models.question import Question
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import get_db
from app.dependencies import get_scoring_service
from app.schemas.quiz import *
from app.services.scoring import ScoringService

router = APIRouter(prefix="/quiz", tags=["quiz"])

_VERSION_LABELS = {
    "quick": "Quick (14)",
    "recommended": "Recommended (36)",
    "long": "Long (100)",
}

@router.get("/versions", response_model=list[VersionOut])
def list_versions():
    settings = get_settings()
    return [VersionOut(key=k, label=_VERSION_LABELS.get(k, k), size(len(v)) for k, v in settings.QUIZ_VERSIONS.items()]

@router.get("/questions", response_model=QuestionsResponse)
async def get_questions(version: str, db: AsyncSession = Depends(get_db)):
    settings = get_settings()
    if version not in settings.QUIZ_VERSIONS:
        raise HTTPException(404, "Unknown version")
    
    q_ids = settings.QUIZ_VERSIONS[version]
    if not q_ids:
        return QuestionsResponse(version=version, items=[])
        
    result = await db.execute(select(Question).where(Question.id.in_(q_ids)))
    items = result.scalars().all()
    
    return QuestionsResponse(
        version=version,
        items=[ItemOut(id=q.id, pole_left=q.pole_left, pole_right=q.pole_right) for q in items]
    )

@router.post("/score", response_model=ScoreResponse)
async def score_quiz(req: ScoreRequest, scoring: ScoringService = Depends(get_scoring_service)):
    settings = get_settings()
    if req.version not in settings.QUIZ_VERSIONS:
        raise HTTPException(400, "Invalid version")

    version_items = settings.QUIZ_VERSIONS[req.version]
    answer_map = {a.question_id: a.value for a in req.answers}

    missing = set(version_items) - set(answer_map.keys())
    if missing:
        raise HTTPException(400, f"Missing answers for: {sorted(missing)}")

    ranked = scoring.score(answer_map, version_items)
    
    top_matches = []
    for eid, pct in ranked[:25]:
        if pct == -1: continue 
        meta = scoring.entity_meta.get(eid)
        top_matches.append(EntityMatch(
            entity_id=eid,
            name=meta["name"] if meta else str(eid),       # Safe mapping access
            entity_type=meta["entity_type"] if meta else "unknown",
            score_percent=round(float(pct), 2),
            universe=meta["universe"] if meta else None,
            image_url=meta["image_url"] if meta else None,
        ))

    return ScoreResponse(
        version=req.version,
        num_questions_answered=len(req.answers),
        top_matches=top_matches
    )
