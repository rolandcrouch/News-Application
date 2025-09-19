# 🐳 Docker Hub Deployment Guide

## Prerequisites

1. **Docker Desktop** installed and running
2. **Docker Hub account** (create at https://hub.docker.com)
3. **Command line access** to your project directory

## Step-by-Step Docker Hub Upload

### Step 1: Start Docker Desktop
```bash
# On macOS, start Docker Desktop application
# Or from command line:
open -a Docker

# Verify Docker is running
docker --version
docker info
```

### Step 2: Login to Docker Hub
```bash
# Login to your Docker Hub account
docker login

# Enter your Docker Hub username and password when prompted
```

### Step 3: Build the Docker Image
```bash
# Navigate to your project directory
cd "Django News Application 2"

# Build the image with a descriptive tag
docker build -t django-news-app .

# Verify the image was built successfully
docker images | grep django-news-app
```

### Step 4: Tag the Image for Docker Hub
```bash
# Replace 'yourusername' with your actual Docker Hub username
docker tag django-news-app yourusername/django-news-app:latest

# Create additional version tag (optional)
docker tag django-news-app yourusername/django-news-app:v1.0

# Verify tags
docker images | grep yourusername/django-news-app
```

### Step 5: Push to Docker Hub
```bash
# Push the latest tag
docker push yourusername/django-news-app:latest

# Push the version tag (if created)
docker push yourusername/django-news-app:v1.0
```

### Step 6: Verify Upload
```bash
# Check your Docker Hub repository at:
# https://hub.docker.com/r/yourusername/django-news-app
```

## Complete Command Sequence

Here's the full sequence to copy and paste:

```bash
# 1. Start Docker (if not running)
open -a Docker

# 2. Login to Docker Hub
docker login

# 3. Build the image
docker build -t django-news-app .

# 4. Tag for Docker Hub (replace 'yourusername')
docker tag django-news-app yourusername/django-news-app:latest
docker tag django-news-app yourusername/django-news-app:v1.0

# 5. Push to Docker Hub
docker push yourusername/django-news-app:latest
docker push yourusername/django-news-app:v1.0

# 6. Verify
docker images | grep yourusername/django-news-app
```

## Docker Hub Repository Setup

### Repository Description
Use this description for your Docker Hub repository:

```
📰 Professional Django News Application with role-based access (Reader/Journalist/Editor), Twitter/X integration for auto-posting, email notifications, content approval workflows, and modern responsive UI. Features Docker deployment, MySQL database, OAuth 2.0 authentication, and comprehensive user management.
```

### Repository Tags
- `latest` - Most recent stable version
- `v1.0` - Version 1.0 release
- `stable` - Production-ready version

### Usage Instructions for Docker Hub
Add this to your Docker Hub repository README:

```markdown
# Django News Application

## Quick Start

### Using Docker Compose (Recommended)
```bash
# Download docker-compose.yml
curl -O https://raw.githubusercontent.com/yourusername/django-news-app/main/docker-compose.yml

# Start the application
docker-compose up -d

# Access at http://localhost:8000
```

### Using Docker Run
```bash
# Start MySQL database
docker run -d --name news-db \
  -e MYSQL_DATABASE=newapp_db \
  -e MYSQL_USER=newsapp_user \
  -e MYSQL_PASSWORD=newsapp_password \
  -e MYSQL_ROOT_PASSWORD=root_password \
  -p 3306:3306 \
  mysql:8.0

# Start Django application
docker run -d --name news-app \
  --link news-db:db \
  -e DB_HOST=db \
  -e DB_NAME=newapp_db \
  -e DB_USER=newsapp_user \
  -e DB_PASSWORD=newsapp_password \
  -p 8000:8000 \
  yourusername/django-news-app:latest
```

### Test Accounts
- Reader: `reader1` / `password123`
- Journalist: `journalist1` / `password123`
- Editor: `editor1` / `password123`
```

## Environment Variables

The Docker image supports these environment variables:

```bash
# Database Configuration
DB_NAME=newapp_db
DB_USER=newsapp_user
DB_PASSWORD=newsapp_password
DB_HOST=db
DB_PORT=3306

# Django Configuration
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Twitter Integration (Optional)
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
TWITTER_REDIRECT_URI=http://localhost:8000/accounts/twitter/callback/

# Email Configuration (Optional)
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
```

## Image Information

- **Base Image**: python:3.13-slim
- **Size**: ~200MB (optimized)
- **Architecture**: linux/amd64
- **Python Version**: 3.13
- **Django Version**: 5.2.6
- **Database**: MySQL 8.0 compatible

## Security Features

- ✅ **Non-root user** execution
- ✅ **Environment variable** configuration
- ✅ **Health checks** included
- ✅ **Minimal attack surface** with slim base image
- ✅ **No sensitive data** in image layers

## Production Deployment

For production deployment, update these settings:

```bash
# Production environment variables
DEBUG=False
SECRET_KEY=your-very-secure-production-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_HOST=your-production-db-host

# Use production database
DB_NAME=your_production_db
DB_USER=your_production_user
DB_PASSWORD=your_secure_password
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find and kill process using port 8000
   lsof -ti:8000 | xargs kill -9
   ```

2. **Database Connection Failed**
   ```bash
   # Check database container status
   docker ps | grep mysql
   docker logs news-db
   ```

3. **Image Build Failed**
   ```bash
   # Clean Docker cache and rebuild
   docker system prune -a
   docker build --no-cache -t django-news-app .
   ```

### Support

- **GitHub Repository**: https://github.com/yourusername/django-news-app
- **Documentation**: See README.md in the repository
- **Issues**: Report bugs on GitHub Issues

---

**Ready to deploy your Django News Application anywhere Docker runs!** 🚀

