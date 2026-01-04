FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /api
COPY requirements/api.txt apiRequirements.txt
COPY alembic.ini .
COPY alembic ./alembic

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r apiRequirements.txt

COPY src/api ./api