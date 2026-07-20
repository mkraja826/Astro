FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080 \
    JYOTHISYAM_JPL_EPHEMERIS_PATH=/app/app/data/jpl/de440s.bsp

WORKDIR /app

RUN addgroup --system api && adduser --system --ingroup api api

COPY pyproject.toml README.md ./
COPY app ./app

RUN python -m pip install --no-cache-dir .

USER api

EXPOSE 8080

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
