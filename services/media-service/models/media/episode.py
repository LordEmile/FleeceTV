from config.db.database import MediaBase
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Date,Enum, Float, ForeignKey


class Episode(MediaBase):
    __tablename__ = "episodes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    season_id = Column(Integer, ForeignKey("seasons.id"))
    number = Column(Integer, nullable=False)

    season = relationship("Season", back_populates="episode")
    file = relationship("File", back_populates="episode")