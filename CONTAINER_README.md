# Django News Application - Container Setup

This document provides comprehensive information about the containerized deployment of the Django News Application.

## 🐳 Container Architecture

The application uses a multi-container architecture with the following services:

### Development Environment
- **web**: Django application server
- **db**: MySQL database
- **volumes**: Persistent data storage

### Production Environment
- **web**: Django application with Gunicorn
- **db**: PostgreSQL database
- **redis**: Redis for caching and sessions
- **nginx**: Reverse proxy and static file server
- **celery**: Background task worker
- **celery-beat**: Scheduled task scheduler

## 📁 Container Files Structure

```
├── Dockerfile                 # Multi-stage production-ready image
├── docker-compose.yml         # Development environment
├── docker-compose.prod.yml    # Production environment
├── .dockerignore             # Files to exclude from build
├── env.production.example    # Production environment template
├── nginx/                    # Nginx configuration
│   ├── nginx.conf           # Main nginx config
│   └── conf.d/
│       └── default.conf     # Server configuration
└── scripts/                 # Management scripts
    ├── docker-dev.sh        # Development management
    └── docker-prod.sh       # Production management
```

## 🚀 Quick Start

### Development Environment

1. **Start the development environment**:
   ```bash
   ./scripts/docker-dev.sh start
   ```

2. **Access the application**:
   - Web interface: http://localhost:8000
   - API documentation: http://localhost:8000/api/info/
   - Admin panel: http://localhost:8000/admin/

3. **Default credentials**:
   - Admin: `admin` / `admin123`
   - Test users available via `create_test_users.py`

### Production Environment

1. **Configure environment**:
   ```bash
   cp env.production.example .env.production
   # Edit .env.production with your settings
   ```

2. **Start production environment**:
   ```bash
   ./scripts/docker-prod.sh start
   ```

## 🛠 Management Scripts

### Development Script (`./scripts/docker-dev.sh`)

```bash
# Build environment
./scripts/docker-dev.sh build

# Start/stop services
./scripts/docker-dev.sh start
./scripts/docker-dev.sh stop
./scripts/docker-dev.sh restart

# View logs
./scripts/docker-dev.sh logs
./scripts/docker-dev.sh logs web

# Run Django commands
./scripts/docker-dev.sh manage makemigrations
./scripts/docker-dev.sh manage migrate
./scripts/docker-dev.sh manage createsuperuser

# Access shells
./scripts/docker-dev.sh shell      # Django shell
./scripts/docker-dev.sh dbshell    # Database shell

# Run tests
./scripts/docker-dev.sh test

# Create database backup
./scripts/docker-dev.sh backup

# Reset environment (destroys data)
./scripts/docker-dev.sh reset

# Show status
./scripts/docker-dev.sh status
```

### Production Script (`./scripts/docker-prod.sh`)

```bash
# Build and deploy
./scripts/docker-prod.sh build
./scripts/docker-prod.sh start

# Management
./scripts/docker-prod.sh manage collectstatic
./scripts/docker-prod.sh manage migrate

# Backup and restore
./scripts/docker-prod.sh backup
./scripts/docker-prod.sh restore backups/backup_20231219_120000.sql.gz

# Update application
./scripts/docker-prod.sh update

# Monitoring
./scripts/docker-prod.sh monitor
./scripts/docker-prod.sh health
./scripts/docker-prod.sh ssl-status

# View logs
./scripts/docker-prod.sh logs nginx
```

## 🔧 Configuration

### Environment Variables

Key environment variables for production:

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | ✅ |
| `DEBUG` | Debug mode (False for production) | ✅ |
| `ALLOWED_HOSTS` | Comma-separated allowed hostnames | ✅ |
| `DB_NAME` | Database name | ✅ |
| `DB_USER` | Database username | ✅ |
| `DB_PASSWORD` | Database password | ✅ |
| `REDIS_PASSWORD` | Redis password | ✅ |
| `EMAIL_HOST_USER` | SMTP username | ❌ |
| `EMAIL_HOST_PASSWORD` | SMTP password | ❌ |
| `TWITTER_CLIENT_ID` | Twitter API client ID | ❌ |
| `TWITTER_CLIENT_SECRET` | Twitter API client secret | ❌ |

### SSL Configuration

For production HTTPS:

1. **Add SSL certificates**:
   ```bash
   mkdir -p nginx/ssl
   # Copy your certificates to:
   # nginx/ssl/cert.pem
   # nginx/ssl/key.pem
   ```

2. **Update nginx configuration** in `nginx/conf.d/default.conf`
3. **Enable SSL redirect** in environment variables

### Database Configuration

#### Development (MySQL)
- Automatic setup with test data
- Data persisted in Docker volumes
- Accessible on port 3306

#### Production (PostgreSQL)
- Requires manual configuration
- Automated backups available
- Connection pooling recommended

## 🔍 Monitoring and Logging

### Health Checks

The application includes built-in health checks:

- **Application**: `/api/info/` endpoint
- **Database**: Connection test
- **Redis**: Ping test
- **Nginx**: Custom health endpoint

### Logging

Logs are available via:

```bash
# Application logs
./scripts/docker-prod.sh logs web

# Nginx logs
./scripts/docker-prod.sh logs nginx

# Database logs
./scripts/docker-prod.sh logs db

# All services
docker-compose -f docker-compose.prod.yml logs -f
```

### Monitoring

Use the monitoring command for overview:

```bash
./scripts/docker-prod.sh monitor
```

This shows:
- Container status
- Resource usage (CPU, memory, network)
- Volume usage
- Recent error logs

## 🔒 Security Features

### Container Security
- **Non-root user**: Application runs as `appuser`
- **Multi-stage build**: Smaller production images
- **Minimal dependencies**: Only runtime dependencies in production
- **Security headers**: Configured in Nginx
- **Rate limiting**: API and login endpoints

### Network Security
- **Internal networks**: Services communicate on private network
- **Exposed ports**: Only necessary ports exposed
- **SSL/TLS**: HTTPS enforcement in production
- **HSTS**: HTTP Strict Transport Security headers

## 🚨 Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check logs
./scripts/docker-dev.sh logs web

# Check container status
./scripts/docker-dev.sh status

# Rebuild if needed
./scripts/docker-dev.sh reset
```

#### Database Connection Errors
```bash
# Check database status
./scripts/docker-dev.sh logs db

# Verify database is healthy
docker-compose ps db

# Reset database if needed
docker-compose down -v
```

#### Permission Errors
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x scripts/*.sh
```

#### Out of Disk Space
```bash
# Clean up Docker resources
docker system prune -a

# Remove unused volumes
docker volume prune
```

### Performance Issues

#### High Memory Usage
- Increase container memory limits
- Optimize Django settings
- Check for memory leaks in logs

#### Slow Response Times
- Check database query performance
- Enable Redis caching
- Optimize nginx configuration
- Scale with multiple web containers

## 🔄 Backup and Recovery

### Automated Backups

Production script includes automated backup:

```bash
# Create backup
./scripts/docker-prod.sh backup

# Backups are stored in backups/ directory
# Old backups are automatically cleaned (7 days retention)
```

### Manual Backup

```bash
# Database backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U newsapp_user newsapp_prod > backup.sql

# Media files backup
docker-compose -f docker-compose.prod.yml exec web tar -czf /tmp/media.tar.gz /app/media/
docker cp container_name:/tmp/media.tar.gz ./media_backup.tar.gz
```

### Recovery

```bash
# Restore database
./scripts/docker-prod.sh restore backups/backup_20231219_120000.sql.gz

# Restore media files
docker cp media_backup.tar.gz container_name:/tmp/
docker-compose -f docker-compose.prod.yml exec web tar -xzf /tmp/media.tar.gz -C /app/
```

## 🚀 Scaling and Performance

### Horizontal Scaling

Scale web containers:

```bash
docker-compose -f docker-compose.prod.yml up -d --scale web=3
```

### Load Balancing

Nginx is configured to load balance across multiple web containers automatically.

### Database Optimization

For high-traffic deployments:

1. **Connection Pooling**: Use pgbouncer
2. **Read Replicas**: Configure read-only database replicas
3. **Indexing**: Optimize database indexes
4. **Caching**: Enable Redis caching for database queries

### CDN Integration

For static files and media:

1. Configure CDN URLs in environment
2. Update nginx configuration
3. Set appropriate cache headers

## 🔧 Advanced Configuration

### Custom Django Settings

Create custom settings for containers:

```python
# settings/docker.py
from .base import *

# Container-specific settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

# Redis cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### Custom Nginx Configuration

Modify `nginx/conf.d/default.conf` for:
- Custom domains
- SSL configuration
- Rate limiting rules
- Cache settings
- Security headers

This container setup provides a robust, scalable, and secure deployment solution for the Django News Application.
