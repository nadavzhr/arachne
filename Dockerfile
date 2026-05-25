FROM mcr.microsoft.com/playwright/python:v1.59.0-jammy AS base

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

# Prune unused Playwright browsers to save space
RUN rm -rf /ms-playwright/firefox-* /ms-playwright/webkit-*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Ensure python 3.12 is available
RUN uv python install 3.12

# -----------------------------------------------------------------------------
# Development stage
# -----------------------------------------------------------------------------
FROM base AS dev
# For dev, we let docker-compose map volumes and install deps at runtime.
CMD ["bash"]

# -----------------------------------------------------------------------------
# Builder stage (for production)
# -----------------------------------------------------------------------------
FROM base AS builder

COPY pyproject.toml uv.lock ./
# Install dependencies with cache, but not the project code yet
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# -----------------------------------------------------------------------------
# Production stage
# -----------------------------------------------------------------------------
FROM base AS prod

COPY --from=builder /app/.venv /app/.venv
COPY . .

# Install project code into environment
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# We do not need to install chromium because it is already in the Microsoft base image.
# We pruned the unused ones in the base stage.

ENTRYPOINT ["arachne"]
CMD ["run"]
