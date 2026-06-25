#!/bin/sh
set -e

DB_PATH="${DJANGO_DB_NAME:-/app/db.sqlite3}"
DB_DIR="$(dirname "$DB_PATH")"

mkdir -p "$DB_DIR"

if [ ! -f "$DB_PATH" ] && [ "$DB_PATH" != "/app/db.sqlite3" ] && [ -f /app/db.sqlite3 ]; then
    cp /app/db.sqlite3 "$DB_PATH"
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
