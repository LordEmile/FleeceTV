FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements/api.txt apiRequirements.txt

RUN apt-get update && apt-get install -y & rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r apiRequirements.txt

COPY api ./api