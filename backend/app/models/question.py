from sqlalchemy import Column, Integer, String

from app.db.base import Base


# i don't know if 'question' is the right way to phrase it but hm maybe attribute but that might be too vague so maybe this is fine
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    pole_left = Column(String, nullable=False)
    pole_right = Column(String, nullable=False)
