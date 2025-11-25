from sqlalchemy import Column, Integer, String, Date,Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
from ..db.base import Base
from datetime import date

class Season(Base):
    __tablename__ = "seasons"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    serie_id = Column(Integer, ForeignKey(series.id))
    number = Column(Integer, nullable=False)
    tmdb_id = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    first_date = Column(Date, default=date.today)
    rating = Column(Float, nullable=False)
    poster_url = Column(String, nullable=False)
    updated_at = Column(Date, default=date.today)

    serie = relationship("serie", back_populates="seasons")
    season = relationship("season", back_populates="episodes")