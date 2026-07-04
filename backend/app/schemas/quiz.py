from pydantic import BaseModel, Field


class VersionOut(BaseModel):
    key: str
    label: str
    size: int


class ItemOut(BaseModel):
    id: int
    pole_left: str
    pole_right: str


class QuestionsResponse(BaseModel):
    version: str
    items: list[ItemOut]


class AnswerIn(BaseModel):
    question_id: int = Field(..., ge=1)
    # might want to change the bounds of this later
    value: int = Field(..., ge=1, le=100)


class ScoreRequest(BaseModel):  # im not sure if we want to do it this way
    version: str
    answers: list[AnswerIn] = Field(..., min_length=1)


class EntityMatch(BaseModel):
    entity_id: int
    name: str
    entity_type: str
    score_percent: float = Field(..., ge=0.0, le=100.0)
    universe: str | None = None
    image_url: str | None = None


class ScoreResponse(BaseModel):
    version: str
    num_questions_answered: int
    top_matches: list[EntityMatch]
