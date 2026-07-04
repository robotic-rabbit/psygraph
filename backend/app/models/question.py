from sqlalchemy import Column, Integer, String

from app.db.base import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    pole_left = Column(String, nullable=False)
    pole_right = Column(String, nullable=False)
