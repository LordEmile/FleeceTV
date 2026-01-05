FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /worker

COPY  requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./worker