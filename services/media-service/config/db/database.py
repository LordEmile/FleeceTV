import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

PIPELINEDB = os.getenv("PIPELINE_DB_URL")
MEDIADB = os.getenv("MEDIA_DB_URL")

#Bases
MediaBase = declarative_base()
PipelineBase = declarative_base()

#Engines
MediaEngine = create_engine(MEDIADB, future=True)
PipelineEngine = create_engine(PIPELINEDB, future=True)

#Sessions
MediaSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=MediaEngine
)
PipelineSession = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=PipelineEngine
)

