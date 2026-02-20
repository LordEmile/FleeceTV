from sqlalchemy import Column, Integer, String, DateTime, Enum, Float, ForeignKey
from config.db.database import PipelineBase
from models.enums.status import EnumStatus
from models.enums.job import EnumJob
from sqlalchemy.orm import relationship
from datetime import datetime

class Step(PipelineBase):
    __tablename__ = "steps"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False, index=True)
    order_index = Column(Integer, nullable=False)
    job_type = Column(Enum(EnumJob), nullable=False)
    status = Column(Enum(EnumStatus), nullable=False)
    retry_count = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    pipeline = relationship("Pipeline", back_populates="steps")