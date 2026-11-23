# syntax=docker/dockerfile:1

# ---- base: Python + uv -------------------------------------------------------
FROM python:3.13-slim AS base
RUN pip install --no-cache-dir "uv>=0.11,<0.12"
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"
WORKDIR /app

# ---- deps: production dependencies only --------------------------------------
FROM base AS deps
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# ---- dev: used by docker compose ---------------------------------------------
FROM deps AS dev
RUN uv sync --frozen --no-install-project
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "tailwind", "runserver", "0.0.0.0:8000"]

# ---- build: compile CSS and collect static files -----------------------------
FROM deps AS build
COPY . .
RUN DJANGO_SETTINGS_MODULE=config.settings.dev python manage.py tailwind build \
 && DJANGO_SETTINGS_MODULE=config.settings.prod DJANGO_SECRET_KEY=build-only \
    python manage.py collectstatic --noinput \
 && rm -rf .django_tailwind_cli

# ---- prod: slim runtime image ------------------------------------------------
FROM python:3.13-slim AS prod
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.prod
RUN useradd --create-home --uid 1000 app
WORKDIR /app
COPY --from=deps /opt/venv /opt/venv
COPY --from=build --chown=app:app /app /app
USER app
EXPOSE 8000
CMD ["bin/start.sh"]
