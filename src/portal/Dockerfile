FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements/portal.txt portalRequirements.txt

RUN apt-get update && apt-get install -y & rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r portalRequirements.txt

COPY portal ./portal