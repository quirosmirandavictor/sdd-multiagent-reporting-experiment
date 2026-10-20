FROM ghcr.io/astral-sh/uv:0.12.23@sha256:61d393e44e249f2e4b526b6c7ddcecce245946826e608e11c93ad4f5bba55b21 AS uv_binary

FROM python:3.12-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258 AS base

COPY --from=uv_binary /uv /usr/local/bin/uv

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_SYSTEM_CERTS=true \
    UV_LINK_MODE=copy \
    UVICORN_HOST=0.0.0.0 \
    UVICORN_PORT=8000

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev \
    && groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid 10001 --create-home appuser

COPY app.py ./

USER 10001:10001

EXPOSE 8000

CMD ["uv", "run", "--locked", "--no-sync", "--no-dev", "python", "-m", "uvicorn", "app:app"]

FROM base AS test

USER root
RUN uv sync --locked
COPY tests/ ./tests/

USER 10001:10001

CMD ["uv", "run", "--locked", "--no-sync", "python", "-m", "pytest", "-q", "-p", "no:cacheprovider"]

FROM base AS runtime
