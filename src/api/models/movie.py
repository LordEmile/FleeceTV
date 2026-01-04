from sqlalchemy import Column, Integer, String, Date,Enum, Float
from ..db.base import Base
from datetime import date
from api.models.enum.category import EnumCategory
from sqlalchemy.orm import relationship

class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    tmdb_id = Column(String, nullable=False)
    category = Column(Enum(EnumCategory), nullable=False)
    description = Column(String, nullable=False)
    release_date = Column(Date, nullable=False, default=date.today)
    rating = Column(String, nullable=True)
    poster_url = Column(String, nullable=False)
    updated_at = Column(Date, nullable=False, default=date.today)

    file = relationship("File", back_populates="movie")
