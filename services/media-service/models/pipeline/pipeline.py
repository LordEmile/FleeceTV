from sqlalchemy import Column, Integer, String, DateTime, Enum, Float, ForeignKey
from config.db.database import PipelineBase
from models.enums.status import EnumStatus
from sqlalchemy.orm import relationship
from datetime import datetime

class Pipeline(PipelineBase):
    __tablename__ = "pipelines"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    target_id = Column(Integer, nullable=False) 
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime,  nullable=False, default=datetime.now, onupdate=datetime.now)
    status = Column(Enum(EnumStatus), nullable=False)

    steps = relationship("Step", back_populates="pipeline")