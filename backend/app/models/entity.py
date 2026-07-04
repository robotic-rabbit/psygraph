from sqlalchemy import Boolean, Column, Integer, String

from app.db.base import Base


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)  # 'character', 'user', 'peer_report'
    universe = Column(String, nullable=True)  # default NULL for users
    image_url = Column(String, nullable=True)  # default NULL for users
    is_aggregated = Column(
        Boolean, default=False
    )  # True for characters (averaged data)
