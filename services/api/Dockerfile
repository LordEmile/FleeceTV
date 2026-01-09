FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /api
COPY requirements.txt requirements.txt
COPY alembic.ini .
COPY config/alembic ./alembic
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]