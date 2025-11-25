from sqlalchemy import Column, Integer, String, Date,Enum, Float, ForeignKey
from ..db.base import Base
from datetime import date
from models.enum.category import EnumCategory
from sqlalchemy.orm import relationship

class episode(Base):
    __tablename__ = "episodes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    season_id = Column(Integer, ForeignKey(seasons.id))
    number = Column(Integer, nullable=False)

    season = relationship("season", back_populates="episodes")
    file = relationship("files", back_populates="episode")