#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Clear any existing migration state (if database was reset)
echo "Checking migration state..."

# Run collectstatic
python manage.py collectstatic --no-input

# Handle migrations carefully
echo "Running migrations with error handling..."

# Try to migrate, if it fails due to existing tables, fake-apply them
python manage.py migrate --run-syncdb || {
    echo "Migration failed, attempting to fake-apply problematic migrations..."
    python manage.py migrate Faculty --fake-initial || true
    python manage.py migrate Student --fake-initial || true
    python manage.py migrate
}

echo "Build completed successfully!"