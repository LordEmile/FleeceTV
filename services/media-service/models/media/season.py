from sqlalchemy import Column, Integer, String, Date,Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
from config.db.database import MediaBase 
from datetime import date

class Season(MediaBase):
    __tablename__ = "seasons"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    serie_id = Column(Integer, ForeignKey("series.id"))
    number = Column(Integer, nullable=False)
    tmdb_id = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    first_date = Column(Date, default=date.today)
    rating = Column(Float, nullable=False)
    poster_url = Column(String, nullable=False)
    updated_at = Column(Date, default=date.today)

    serie = relationship("Serie", back_populates="season")
    episode = relationship("Episode", back_populates="season")