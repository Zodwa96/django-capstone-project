#!/usr/bin/env bash
# Container entrypoint: waits for the database (unless USE_SQLITE=1),
# applies migrations, sets up role groups/permissions, then starts
# the Django application with gunicorn.
set -e

if [ "$USE_SQLITE" != "1" ]; then
    echo "Waiting for database at ${DB_HOST:-localhost}:${DB_PORT:-3306}..."
    python <<'PYEOF'
import os
import socket
import time

host = os.getenv("DB_HOST", "localhost")
port = int(os.getenv("DB_PORT", "3306"))

for attempt in range(30):
    try:
        with socket.create_connection((host, port), timeout=2):
            break
    except OSError:
        time.sleep(2)
else:
    raise SystemExit(f"Could not connect to database at {host}:{port} after 60s")
PYEOF
    echo "Database is available."
fi

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Setting up groups and permissions..."
python manage.py setup_permissions

echo "Starting gunicorn..."
exec gunicorn newsproject.wsgi:application --bind 0.0.0.0:8000 --workers 3
