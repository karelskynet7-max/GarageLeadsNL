FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml ./
COPY README.md ./
COPY config.yaml ./
COPY .env.example ./.env.example
COPY garageleads ./garageleads

RUN pip install --upgrade pip && pip install .

CMD ["python", "-m", "garageleads", "run"]
