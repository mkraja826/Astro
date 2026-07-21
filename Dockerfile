FROM python:3.12-slim

ARG JPL_EPHEMERIS_URL=https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp
ARG JPL_EPHEMERIS_SHA256=c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080 \
    JYOTHISYAM_REQUIRE_API_KEY=true \
    JYOTHISYAM_JPL_EPHEMERIS_PATH=/app/app/data/jpl/de440s.bsp \
    JYOTHISYAM_JPL_EPHEMERIS_SHA256=${JPL_EPHEMERIS_SHA256}

WORKDIR /app

RUN addgroup --system api && adduser --system --ingroup api api

COPY pyproject.toml README.md ./
COPY scripts/download_jpl_kernel.py ./scripts/download_jpl_kernel.py
COPY app ./app

RUN python scripts/download_jpl_kernel.py \
        --destination app/data/jpl/de440s.bsp \
        --url "${JPL_EPHEMERIS_URL}" \
        --sha256 "${JPL_EPHEMERIS_SHA256}" \
    && python -m pip install --no-cache-dir .

USER api

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8080') + '/health/ready', timeout=4).read()" || exit 1

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
