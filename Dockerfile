# Multi-stage build for optimized production image
# Stage 1: Build dependencies
FROM python:3.13-slim as builder

# Set environment variables for build stage
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
        git \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt

# Stage 2: Production image
FROM python:3.13-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=news_app.settings
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies only
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
        curl \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create non-root user first
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Create directories with proper permissions
RUN mkdir -p /app/staticfiles /app/media /app/var /app/logs \
    && chown -R appuser:appuser /app

# Copy project files
COPY --chown=appuser:appuser . /app/

# Switch to non-root user
USER appuser

# Collect static files (will be overridden in production)
RUN python manage.py collectstatic --noinput --clear

# Create entrypoint script
COPY --chown=appuser:appuser <<EOF /app/entrypoint.sh
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
exec "\$@"
EOF

RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Health check with better endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/info/ || exit 1

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command for development
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

