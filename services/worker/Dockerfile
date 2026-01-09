FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /worker

COPY  requirements.txt requirements.txt
COPY . ./worker

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "-m", "worker.main" ]