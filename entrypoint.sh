#!/bin/sh
set -e

echo "Waiting for Postgres at ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}..."
until pg_isready -h "${POSTGRES_HOST:-db}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-beanroute}" >/dev/null 2>&1; do
  sleep 1
done

python manage.py migrate --noinput || { echo "Migration failed"; exit 1; }
python manage.py seed
python manage.py collectstatic --noinput

exec gunicorn beanroute.wsgi:application --bind 0.0.0.0:8000
