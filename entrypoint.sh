#!/bin/bash
set -e

# Wait for database to be ready
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "\q"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create default superuser
python manage.py create_default_superuser

# Collect static files
python manage.py collectstatic --noinput

# Execute the main command
exec "$@"