from typing import List, Optional

from pydantic import BaseModel


class SliderAnswer(BaseModel):
    question_id: int
    score: float


# we might want to change this later but for now this works
class UserSubmission(BaseModel):
    user_id: str
    answers: List[SliderAnswer]
