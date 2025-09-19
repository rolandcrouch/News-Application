Deployment Guide
================

This guide covers various deployment options for the Django News Application.

Production Deployment
=====================

Docker Deployment (Recommended)
-------------------------------

The application includes Docker support for easy deployment:

**Prerequisites:**
- Docker and Docker Compose installed
- Domain name configured (for production)
- SSL certificate (recommended)

**Steps:**

1. **Clone and Configure**:

.. code-block:: bash

    git clone <repository-url>
    cd django-news-application
    
    # Create production environment file
    cp .env.example .env.production

2. **Configure Environment**:

Edit ``.env.production``:

.. code-block:: bash

    # Django Settings
    SECRET_KEY=your-super-secret-key-here
    DEBUG=False
    ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
    
    # Database (PostgreSQL recommended for production)
    DATABASE_URL=postgresql://user:password@db:5432/newsapp
    
    # Email Configuration
    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_HOST_USER=your-email@gmail.com
    EMAIL_HOST_PASSWORD=your-app-password
    EMAIL_USE_TLS=True
    DEFAULT_FROM_EMAIL=your-email@gmail.com
    
    # Twitter Integration (Optional)
    TWITTER_CLIENT_ID=your_twitter_client_id
    TWITTER_CLIENT_SECRET=your_twitter_client_secret
    TWITTER_REDIRECT_URI=https://yourdomain.com/accounts/twitter/callback/

3. **Deploy with Docker Compose**:

.. code-block:: bash

    # Production deployment
    docker-compose -f docker-compose.prod.yml up -d
    
    # Check logs
    docker-compose -f docker-compose.prod.yml logs -f

4. **Initialize Database**:

.. code-block:: bash

    # Run migrations
    docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
    
    # Create superuser
    docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
    
    # Collect static files
    docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

Traditional Server Deployment
-----------------------------

**Prerequisites:**
- Linux server (Ubuntu/CentOS)
- Python 3.8+
- PostgreSQL
- Nginx
- SSL certificate

**Steps:**

1. **Server Setup**:

.. code-block:: bash

    # Update system
    sudo apt update && sudo apt upgrade -y
    
    # Install dependencies
    sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx certbot python3-certbot-nginx

2. **Database Setup**:

.. code-block:: bash

    # Create database and user
    sudo -u postgres psql
    CREATE DATABASE newsapp;
    CREATE USER newsapp_user WITH PASSWORD 'secure_password';
    GRANT ALL PRIVILEGES ON DATABASE newsapp TO newsapp_user;
    \q

3. **Application Setup**:

.. code-block:: bash

    # Create application user
    sudo useradd --system --home /opt/newsapp --shell /bin/bash newsapp
    
    # Clone application
    sudo git clone <repository-url> /opt/newsapp
    sudo chown -R newsapp:newsapp /opt/newsapp
    
    # Switch to application user
    sudo -u newsapp -s
    cd /opt/newsapp
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt gunicorn psycopg2-binary

4. **Configure Environment**:

.. code-block:: bash

    # Create environment file
    cat > .env << EOF
    SECRET_KEY=your-super-secret-key
    DEBUG=False
    ALLOWED_HOSTS=yourdomain.com
    DATABASE_URL=postgresql://newsapp_user:secure_password@localhost/newsapp
    EOF

5. **Initialize Application**:

.. code-block:: bash

    # Run migrations
    python manage.py migrate
    
    # Create superuser
    python manage.py createsuperuser
    
    # Collect static files
    python manage.py collectstatic --noinput

6. **Configure Gunicorn**:

Create ``/etc/systemd/system/newsapp.service``:

.. code-block:: ini

    [Unit]
    Description=Django News Application
    After=network.target
    
    [Service]
    User=newsapp
    Group=newsapp
    WorkingDirectory=/opt/newsapp
    ExecStart=/opt/newsapp/venv/bin/gunicorn --workers 3 --bind unix:/opt/newsapp/newsapp.sock news_app.wsgi:application
    Restart=always
    
    [Install]
    WantedBy=multi-user.target

7. **Configure Nginx**:

Create ``/etc/nginx/sites-available/newsapp``:

.. code-block:: nginx

    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        
        location = /favicon.ico { access_log off; log_not_found off; }
        
        location /static/ {
            root /opt/newsapp;
        }
        
        location /media/ {
            root /opt/newsapp;
        }
        
        location / {
            include proxy_params;
            proxy_pass http://unix:/opt/newsapp/newsapp.sock;
        }
    }

8. **Enable Services**:

.. code-block:: bash

    # Enable and start services
    sudo systemctl daemon-reload
    sudo systemctl enable newsapp
    sudo systemctl start newsapp
    
    # Enable Nginx site
    sudo ln -s /etc/nginx/sites-available/newsapp /etc/nginx/sites-enabled
    sudo nginx -t
    sudo systemctl restart nginx

9. **Setup SSL**:

.. code-block:: bash

    # Get SSL certificate
    sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

Cloud Platform Deployment
=========================

Heroku Deployment
-----------------

1. **Install Heroku CLI**:

.. code-block:: bash

    # Install Heroku CLI (macOS)
    brew tap heroku/brew && brew install heroku
    
    # Login
    heroku login

2. **Prepare Application**:

Create ``Procfile``:

.. code-block:: text

    web: gunicorn news_app.wsgi:application --port $PORT --bind 0.0.0.0
    release: python manage.py migrate

Create ``runtime.txt``:

.. code-block:: text

    python-3.11.0

3. **Deploy**:

.. code-block:: bash

    # Create Heroku app
    heroku create your-news-app
    
    # Add PostgreSQL
    heroku addons:create heroku-postgresql:hobby-dev
    
    # Set environment variables
    heroku config:set SECRET_KEY=your-secret-key
    heroku config:set DEBUG=False
    heroku config:set ALLOWED_HOSTS=your-news-app.herokuapp.com
    
    # Deploy
    git push heroku main
    
    # Create superuser
    heroku run python manage.py createsuperuser

AWS EC2 Deployment
------------------

1. **Launch EC2 Instance**:
   - Choose Ubuntu 20.04 LTS
   - Configure security groups (HTTP, HTTPS, SSH)
   - Create or use existing key pair

2. **Connect and Setup**:

.. code-block:: bash

    # Connect to instance
    ssh -i your-key.pem ubuntu@your-ec2-ip
    
    # Follow traditional server deployment steps above

3. **Configure Load Balancer** (Optional):
   - Create Application Load Balancer
   - Configure target groups
   - Setup health checks

DigitalOcean Deployment
----------------------

1. **Create Droplet**:
   - Choose Ubuntu 20.04
   - Select appropriate size
   - Add SSH keys

2. **Setup Domain**:
   - Configure DNS records
   - Point A record to droplet IP

3. **Deploy**:
   - Follow traditional server deployment steps

Monitoring and Maintenance
==========================

Health Checks
-------------

Create ``/opt/newsapp/healthcheck.py``:

.. code-block:: python

    #!/usr/bin/env python
    import os
    import sys
    import django
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_app.settings')
    django.setup()
    
    from django.db import connection
    from django.core.cache import cache
    
    def check_database():
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    def check_application():
        try:
            from articles.models import User
            User.objects.count()
            return True
        except Exception:
            return False
    
    if __name__ == "__main__":
        checks = [
            ("Database", check_database),
            ("Application", check_application),
        ]
        
        all_passed = True
        for name, check_func in checks:
            try:
                result = check_func()
                status = "PASS" if result else "FAIL"
                print(f"{name}: {status}")
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"{name}: ERROR - {e}")
                all_passed = False
        
        sys.exit(0 if all_passed else 1)

Logging Configuration
--------------------

Add to ``settings.py``:

.. code-block:: python

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': '/opt/newsapp/logs/django.log',
                'formatter': 'verbose',
            },
        },
        'root': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    }

Backup Strategy
--------------

Create backup script ``/opt/newsapp/backup.sh``:

.. code-block:: bash

    #!/bin/bash
    
    # Configuration
    BACKUP_DIR="/opt/newsapp/backups"
    DB_NAME="newsapp"
    DB_USER="newsapp_user"
    DATE=$(date +"%Y%m%d_%H%M%S")
    
    # Create backup directory
    mkdir -p $BACKUP_DIR
    
    # Database backup
    pg_dump -U $DB_USER -h localhost $DB_NAME > "$BACKUP_DIR/db_backup_$DATE.sql"
    
    # Media files backup
    tar -czf "$BACKUP_DIR/media_backup_$DATE.tar.gz" /opt/newsapp/media/
    
    # Clean old backups (keep last 7 days)
    find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
    find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
    
    echo "Backup completed: $DATE"

Add to crontab:

.. code-block:: bash

    # Daily backup at 2 AM
    0 2 * * * /opt/newsapp/backup.sh >> /opt/newsapp/logs/backup.log 2>&1

Performance Optimization
========================

Database Optimization
---------------------

1. **Database Indexing**:

.. code-block:: sql

    -- Add indexes for common queries
    CREATE INDEX IF NOT EXISTS idx_article_created_at ON articles_article(created_at);
    CREATE INDEX IF NOT EXISTS idx_article_author ON articles_article(author_id);
    CREATE INDEX IF NOT EXISTS idx_article_publisher ON articles_article(publisher_id);
    CREATE INDEX IF NOT EXISTS idx_article_approved ON articles_article(is_approved);

2. **Connection Pooling**:

Install and configure pgbouncer for PostgreSQL connection pooling.

Caching
-------

Add Redis for caching:

.. code-block:: python

    # settings.py
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/1',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

Static Files
-----------

Use CDN for static files in production:

.. code-block:: python

    # settings.py
    if not DEBUG:
        STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
        STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

Security Considerations
======================

Environment Security
--------------------

1. **Environment Variables**: Never commit secrets to version control
2. **File Permissions**: Restrict access to configuration files
3. **Database Security**: Use strong passwords and restrict access
4. **SSL/TLS**: Always use HTTPS in production
5. **Firewall**: Configure firewall to allow only necessary ports

Django Security
---------------

1. **Security Middleware**: Ensure all security middleware is enabled
2. **CSRF Protection**: Verify CSRF tokens are working
3. **XSS Protection**: Use Django's built-in XSS protection
4. **SQL Injection**: Use Django ORM to prevent SQL injection
5. **Authentication**: Implement proper session management

Regular Updates
--------------

1. **System Updates**: Keep OS and packages updated
2. **Python Dependencies**: Regularly update Python packages
3. **Security Patches**: Monitor and apply security patches
4. **Django Updates**: Keep Django updated to latest stable version

Troubleshooting
===============

Common Issues
------------

**Static Files Not Loading**:
- Run ``python manage.py collectstatic``
- Check Nginx configuration
- Verify file permissions

**Database Connection Errors**:
- Check database credentials
- Verify database is running
- Check network connectivity

**502 Bad Gateway**:
- Check Gunicorn is running
- Verify socket file permissions
- Check Nginx configuration

**High Memory Usage**:
- Monitor database queries
- Check for memory leaks
- Consider adding more workers

Log Files
---------

Important log locations:
- Application logs: ``/opt/newsapp/logs/django.log``
- Nginx logs: ``/var/log/nginx/``
- System logs: ``/var/log/syslog``
- Gunicorn logs: ``journalctl -u newsapp``
