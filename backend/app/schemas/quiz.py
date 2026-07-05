from pydantic import BaseModel, Field


class VersionOut(BaseModel):
    key: str
    label: str
    size: int


class QuestionOut(BaseModel):
    id: int
    pole_left: str
    pole_right: str


class QuizResponse(BaseModel):
    version: str
    items: list[QuestionOut]


class AnswerIn(BaseModel):
    question_id: int = Field(..., ge=1)
    # might want to change the bounds of this later
    value: int = Field(..., ge=1, le=100)


class QuizSubmit(BaseModel):  # im not sure if we want to do it this way
    version: str
    answers: list[AnswerIn] = Field(..., min_length=1)


# TODO: refactor entity and add coordinates maybe or maybe have that as a seperate schema? idk
class Entity(BaseModel):
    entity_id: int
    name: str
    entity_type: str
    universe: str | None = None
    image_url: str | None = None


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
