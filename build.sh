#!/usr/bin/env bash
# exit on error
set -o errexit

echo "=== Installing dependencies ==="
pip install -r requirements.txt

echo "=== Checking migration state ==="

# Collect static files
echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

# Apply migrations with smart error handling
echo "=== Running migrations with error handling ==="
python manage.py migrate --run-syncdb || {
    echo "Migration failed — attempting to fake-initialize existing tables..."
    python manage.py migrate --fake-initial
    python manage.py migrate
}

echo "=== Build completed successfully! ==="
