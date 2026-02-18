from sqlalchemy import Column, Integer, String, Date,Enum, Float, ForeignKey
from sqlalchemy.orm import relationship
from config.db.database import MediaBase
from models.enums.language import EnumLanguage

class File(MediaBase):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=True)
    episode_id = Column(Integer, ForeignKey("episodes.id") , nullable=True)
    language = Column(Enum(EnumLanguage), nullable=False)
    video_path = Column(String, nullable=True)
    sub_path = Column(String, nullable=True)

    movie = relationship("Movie", back_populates="file")
    episode = relationship("Episode", back_populates="file")