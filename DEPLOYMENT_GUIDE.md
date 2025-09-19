# 🚀 Django News Application - Deployment Guide

## Prerequisites

### Required Software
- **Git** - for cloning the repository
- **Docker & Docker Compose** (recommended) - for containerized deployment
- **Python 3.13+** (if running manually) - for local development
- **MySQL 8.0+** (if running manually) - for database

## 📋 Quick Start with Docker (Recommended)

### Step 1: Clone the Repository
```bash
git clone <your-github-repository-url>
cd django-news-application
```

### Step 2: Environment Configuration (Optional)
Create a `.env` file for Twitter and email integration:
```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your credentials
nano .env
```

**Example `.env` file:**
```env
# Twitter API (optional - for social media posting)
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
TWITTER_REDIRECT_URI=http://localhost:8000/accounts/twitter/callback/

# Email Configuration (optional - for notifications)
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password

# Production Settings (change for production deployment)
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Step 3: Start the Application
```bash
# Build and start all services (database + web app)
docker-compose up --build -d

# View logs to monitor startup
docker-compose logs -f web
```

### Step 4: Access the Application
- **Web Application**: http://localhost:8000
- **Login with test accounts**:
  - Reader: `reader1` / `password123`
  - Journalist: `journalist1` / `password123`
  - Editor: `editor1` / `password123`

### Step 5: Useful Docker Commands
```bash
# View application logs
docker-compose logs -f web

# View database logs
docker-compose logs -f db

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Access Django shell
docker-compose exec web python manage.py shell

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run migrations manually
docker-compose exec web python manage.py migrate
```

---

## 🛠️ Manual Setup (Alternative)

If you prefer to run without Docker:

### Step 1: Clone and Navigate
```bash
git clone <your-github-repository-url>
cd django-news-application
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Database Setup
```bash
# Install MySQL and create database
mysql -u root -p
CREATE DATABASE newapp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'newsapp_user'@'localhost' IDENTIFIED BY 'newsapp_password';
GRANT ALL PRIVILEGES ON newapp_db.* TO 'newsapp_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 5: Environment Configuration
```bash
# Create environment file
cp .env.example .env

# Edit with your database and API credentials
nano .env
```

**Example `.env` file for manual setup:**
```env
# Database
DB_NAME=newapp_db
DB_USER=newsapp_user
DB_PASSWORD=newsapp_password
DB_HOST=localhost
DB_PORT=3306

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Twitter API (optional)
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
TWITTER_REDIRECT_URI=http://localhost:8000/accounts/twitter/callback/

# Email (optional)
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
```

### Step 6: Django Setup
```bash
# Run migrations
python manage.py migrate

# Create test users
python create_test_users.py

# Collect static files
python manage.py collectstatic

# Create superuser (optional)
python manage.py createsuperuser
```

### Step 7: Run the Server
```bash
python manage.py runserver
```

Access at: http://localhost:8000

---

## 🔧 Configuration Options

### Twitter Integration Setup
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new app with OAuth 2.0
3. Set callback URL: `http://localhost:8000/accounts/twitter/callback/`
4. Copy Client ID and Client Secret to `.env`

### Gmail Integration Setup
1. Enable 2-Factor Authentication on Gmail
2. Generate App Password: Google Account → Security → App Passwords
3. Use your email and app password in `.env`

### Production Deployment
1. Set `DEBUG=False`
2. Configure proper `ALLOWED_HOSTS`
3. Use environment variables for secrets
4. Set up proper web server (nginx + gunicorn)
5. Configure SSL certificates

---

## 📊 Test Accounts

The application comes with pre-created test accounts:

| Role | Username | Password | Permissions |
|------|----------|----------|-------------|
| Reader | `reader1` | `password123` | View articles, subscribe to publishers |
| Journalist | `journalist1` | `password123` | Create articles, connect Twitter |
| Editor | `editor1` | `password123` | Approve content, manage all articles |

---

## 🚨 Troubleshooting

### Docker Issues
```bash
# If port 8000 is busy
docker-compose down
lsof -ti:8000 | xargs kill -9
docker-compose up -d

# If database connection fails
docker-compose logs db
docker-compose restart db
```

### Manual Setup Issues
```bash
# If migrations fail
python manage.py migrate --fake-initial

# If port is busy
lsof -ti:8000 | xargs kill -9
python manage.py runserver 8001

# If MySQL connection fails
pip install mysqlclient
# or
pip install PyMySQL
```

### Twitter Integration Issues
- Ensure callback URL exactly matches in Twitter app settings
- Client ID should be OAuth 2.0 Client ID (not Consumer Key)
- Restart Django server after changing `.env`

---

## 📁 Project Structure

```
django-news-application/
├── articles/                 # Main Django app
├── news_app/                # Django project settings
├── static/                  # Static files (CSS, JS, images)
├── templates/               # HTML templates
├── requirements.txt         # Python dependencies
├── manage.py               # Django management script
├── create_test_users.py    # Test data script
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Multi-service setup
├── .dockerignore          # Docker ignore rules
├── init.sql               # Database initialization
└── README.md              # Project documentation
```

---

## 🎯 Next Steps

1. **Customize the application** - Modify templates, add features
2. **Set up production deployment** - Use proper web server, SSL
3. **Configure monitoring** - Add logging, error tracking
4. **Scale the application** - Use load balancers, multiple instances
5. **Add more integrations** - Facebook, LinkedIn, etc.

For more detailed information, see the main [README.md](README.md) file.

