#!/bin/sh
# Production entrypoint: apply migrations, then serve with gunicorn.
set -e
python manage.py migrate --noinput
python manage.py createcachetable
exec gunicorn config.wsgi \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-3}" \
  --access-logfile - \
  --forwarded-allow-ips="*"
