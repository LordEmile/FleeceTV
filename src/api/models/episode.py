from sqlalchemy import Column, Integer, String, Date,Enum, Float, ForeignKey
from ..db.base import Base
from sqlalchemy.orm import relationship

class Episode(Base):
    __tablename__ = "episodes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    season_id = Column(Integer, ForeignKey("seasons.id"))
    number = Column(Integer, nullable=False)

    season = relationship("Season", back_populates="episode")
    file = relationship("File", back_populates="episode")