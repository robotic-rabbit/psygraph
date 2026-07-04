from sqlalchemy import Column, Float, ForeignKey, Integer, UniqueConstraint

from app.db.base import Base


class Answer(Base):
    __tablename__ = "answers"
    __table_args__ = (
        UniqueConstraint("entity_id", "question_id", name="uq_entity_question"),
    )

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    value = Column(Float, nullable=False)  # 1.0 to 100.0
