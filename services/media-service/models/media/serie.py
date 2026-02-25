from sqlalchemy import Column, Integer, String, Date,Enum, Float
from config.db.database import MediaBase
from datetime import date
from models.enums.category import EnumCategory
from sqlalchemy.orm import relationship

class Serie(MediaBase):
    __tablename__ = "series"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    tmdb_id = Column(String, nullable=False)
    category = Column(Enum(EnumCategory), nullable=False)
    description = Column(String, nullable=False)
    first_date = Column(Date, nullable=False, default=date.today)
    rating = Column(Float, nullable=False)
    poster_url = Column(String, nullable=False)
    updated_at = Column(Date, nullable=False, default=date.today)

    season = relationship("Season", back_populates="serie")