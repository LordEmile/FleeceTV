from sqlalchemy import Column, Integer, String, Date,Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base
from models.enum.language import EnumLanguage

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=True)
    episode_id = Column(Integer, ForeignKey("episodes.id") , nullable=True)
    language = Column(Enum(EnumLanguage), nullable=False)
    file_path = Column(String, nullable=True)

    movie = relationship("Movie", back_populates="file")
    episode = relationship("Episode", back_populates="file")