#!/bin/sh
set -e

# Wait for database to be ready
echo "Waiting for database..."
while ! python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_app.settings')
import django
django.setup()
from django.db import connection
try:
    connection.ensure_connection()
    print('Database is ready!')
except Exception as e:
    print(f'Database not ready: {e}')
    exit(1)
"; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
"

# Execute the main command
exec "$@"
