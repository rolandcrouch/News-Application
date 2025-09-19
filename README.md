# Django News Application

A comprehensive news management system built with Django 5.2.6, featuring role-based access control, Twitter integration, email notifications, and a RESTful API.

## 🚀 Features

### Core Functionality
- **Role-Based User System**: Readers, Journalists, and Editors with distinct permissions
- **Content Management**: Articles and newsletters with approval workflows
- **Publisher System**: Multi-publisher support with editor affiliations
- **Subscription System**: Readers can follow journalists and subscribe to publishers
- **Personalized Newsfeed**: Content filtered based on user subscriptions
- **Email Notifications**: Automated notifications for approved content
- **Twitter Integration**: Automatic posting to Twitter when content is approved
- **RESTful API**: Complete API for third-party integrations

### User Roles

#### 👤 Reader
- Subscribe to publishers and follow journalists
- View personalized newsfeed with subscription-based filtering
- Manage subscriptions through dedicated interface

#### ✍️ Journalist
- Create and manage articles and newsletters
- Publish content independently or with publisher affiliation
- View all their published content

#### ✏️ Editor
- Approve articles and newsletters from their affiliated publisher
- Manage Twitter integration for automated posting
- Access to publisher-specific content management

## 🛠️ Technology Stack

- **Backend**: Django 5.2.6
- **Database**: MySQL/MariaDB
- **API**: Django REST Framework
- **Authentication**: Token-based authentication
- **Frontend**: Django Templates with Bootstrap 5.3.3
- **Email**: Gmail SMTP integration
- **Social Media**: Twitter (X) API integration
- **Environment**: Python 3.13+

## 📋 Prerequisites

- Python 3.13+
- MySQL/MariaDB database
- Twitter Developer Account (for social media integration)
- Gmail account with App Password (for email notifications)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd news_app
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:
```env
# Twitter API Credentials
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
TWITTER_REDIRECT_URI=http://localhost:8000/accounts/twitter/callback/

# Email Configuration
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password

# Database Configuration (if using different credentials)
DB_NAME=newapp_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 5. Database Setup
```bash
# Create database
mysql -u root -p
CREATE DATABASE newapp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Create Test Users
```bash
python create_test_users.py
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## 📁 Project Structure

```
news_app/
├── articles/                    # Main Django app
│   ├── models.py               # User, Publisher, Article, Newsletter models
│   ├── views.py                # Main application views
│   ├── api_views.py            # REST API views
│   ├── serializers.py          # API serializers
│   ├── forms.py                # Django forms
│   ├── urls.py                 # URL routing
│   ├── api_urls.py             # API URL routing
│   ├── templates/              # HTML templates
│   │   ├── articles/           # App-specific templates
│   │   └── registration/       # Authentication templates
│   ├── static/articles/        # CSS and static files
│   ├── functions/              # Utility functions
│   │   └── tweet.py            # Twitter API integration
│   └── integrations/           # External service integrations
├── news_app/                   # Django project settings
│   ├── settings.py             # Main configuration
│   └── urls.py                 # Root URL configuration
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔧 Configuration

### Database
The application is configured to use MySQL/MariaDB by default. To use SQLite for development:

1. Comment out the MySQL configuration in `settings.py`
2. Uncomment the SQLite configuration
3. Run `python manage.py migrate`

### Twitter/X API Integration

**Note**: Twitter integration is optional. The application works fully without it.

#### Step 1: Create Twitter Developer Account
1. Visit [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Apply for a developer account (may require approval)
3. Once approved, create a new project and app

#### Step 2: Configure Twitter App Settings
1. In your Twitter app, go to **Settings** → **Authentication settings**
2. **Enable OAuth 2.0** (critical - must be turned ON)
3. Set **App permissions** to:
   - ✅ Read
   - ✅ Write
   - ❌ Direct Messages (not needed)
4. Set **Type of App**: Web App, Automated App or Bot
5. Add **Callback URL**: `http://localhost:8000/accounts/twitter/callback/`
   - ⚠️ **IMPORTANT**: Must include trailing slash and exact path
   - ⚠️ **IMPORTANT**: Must match your `.env` file exactly

#### Step 3: Get OAuth 2.0 Credentials
1. Go to **Keys and tokens** tab
2. Find **"OAuth 2.0 Client ID and Client Secret"** section
   - ❌ **DON'T use**: Consumer Keys (API v1.1)
   - ✅ **DO use**: OAuth 2.0 Client ID and Client Secret
3. Copy the **Client ID** (typically 15-25 characters, alphanumeric)
4. Copy the **Client Secret** (longer string, 50+ characters)

#### Step 4: Add to Environment Variables
Add to your `.env` file (without quotes):
```env
TWITTER_CLIENT_ID=your_oauth2_client_id_here
TWITTER_CLIENT_SECRET=your_oauth2_client_secret_here
TWITTER_REDIRECT_URI=http://localhost:8000/accounts/twitter/callback/
```

#### Step 5: Connect Twitter in Application
1. Start your Django server: `python manage.py runserver`
2. Login as an **Editor** (only editors can connect Twitter)
3. Look for **"Connect Twitter"** button in navigation
4. Complete OAuth flow by authorizing your Twitter account
5. Verify **"✓ Twitter Connected"** appears

#### Troubleshooting Twitter Integration

**Problem**: "Twitter Unavailable" (gray badge)
- **Cause**: Missing or invalid environment variables
- **Solution**: Check your `.env` file has correct `TWITTER_CLIENT_ID` and `TWITTER_CLIENT_SECRET`

**Problem**: "Something went wrong" during OAuth
- **Cause**: Usually callback URL mismatch or wrong credential type
- **Solutions**:
  1. Verify callback URL in Twitter app exactly matches: `http://localhost:8000/accounts/twitter/callback/`
  2. Ensure you're using OAuth 2.0 credentials, not Consumer Keys
  3. Check OAuth 2.0 is enabled in Twitter app settings

**Problem**: "OAuth 2 MUST utilize https" error
- **Cause**: OAuth library enforces HTTPS by default
- **Solution**: Already handled in code for local development

**Problem**: Client ID looks like base64 (e.g., `RldoY3NyV0...`)
- **Cause**: Using wrong credential type (Consumer Key instead of OAuth 2.0 Client ID)
- **Solution**: Get credentials from "OAuth 2.0 Client ID and Client Secret" section

**Problem**: "unauthorized_client" error
- **Cause**: Haven't completed OAuth flow yet
- **Solution**: Click "Connect Twitter" and complete authorization

#### Twitter Integration Features
- **Automatic posting**: When editors approve content, it's automatically posted to Twitter
- **Connection status**: Visible in navigation for editors
- **Disconnect option**: Editors can disconnect Twitter anytime
- **Error handling**: Graceful fallback if Twitter is unavailable

### Email Configuration
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password
3. Add credentials to your `.env` file

## 🚀 API Documentation

The application includes a comprehensive REST API. See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for detailed information.

### Quick API Start
```bash
# Get authentication token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "reader1", "password": "testpass123"}'

# Use token to access protected endpoints
curl -X GET http://localhost:8000/api/articles/ \
  -H "Authorization: Token your_token_here"
```

## 🧪 Testing

The application includes **comprehensive test coverage** with 60+ test cases covering models, views, forms, APIs, integrations, and permissions.

### Quick Test Commands

```bash
# Run all tests with our custom test runner
python run_tests.py

# Run tests with coverage report
python run_tests.py --coverage

# Run only fast tests (models, forms, serializers)
python run_tests.py --fast

# Run specific test class
python run_tests.py --specific UserModelTest

# Show test suite summary
python run_tests.py --summary

# Run with verbose output
python run_tests.py --verbose
```

### Standard Django Test Commands

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test articles

# Run with verbose output
python manage.py test --verbosity=2

# Run specific test class
python manage.py test articles.tests.UserModelTest

# Stop on first failure
python manage.py test --failfast
```

### Test Coverage Areas

- **📊 Model Tests**: User roles, Article/Newsletter models, Publisher constraints
- **📝 Form Tests**: Registration validation, content creation forms
- **🌐 View Tests**: Authentication, CRUD operations, role-based access
- **🔗 Integration Tests**: Twitter OAuth, email notifications
- **🔐 Security Tests**: Permission systems, role-based access control
- **📡 API Tests**: Serializer functionality and data validation

### Docker Testing

```bash
# Run tests in Docker container
docker-compose exec web python run_tests.py

# Run tests with coverage in Docker
docker-compose exec web python run_tests.py --coverage
```

### Coverage Report

After running tests with `--coverage`, view the HTML coverage report:
- **Local**: Open `htmlcov/index.html` in your browser
- **Expected Coverage**: 85%+ across all modules

### API Testing
```bash
# Test API endpoints
python test_api_demo.py

# Test authentication
python test_auth.py
```

## 📊 User Model Architecture

The application uses a custom User model with role-based field assignment:

### Reader Role
- `subscriptions_publishers`: Publishers the user follows
- `subscriptions_journalists`: Journalists the user follows
- Methods: `get_subscribed_publishers()`, `get_subscribed_journalists()`

### Journalist Role
- Methods: `get_independent_articles()`, `get_independent_newsletters()`
- Can create articles and newsletters independently or with publisher affiliation

### Editor Role
- `affiliated_publisher`: Publisher the editor is affiliated with
- Can approve content from their affiliated publisher
- Manages Twitter integration

## 🔐 Security Features

- **Role-based permissions**: Users can only access features appropriate to their role
- **Content approval workflow**: All content requires editor approval
- **Publisher restrictions**: Editors can only approve content from their affiliated publisher
- **Token authentication**: Secure API access
- **Password validation**: Django's built-in password validators
- **CSRF protection**: Built-in Django CSRF middleware

## 📧 Email Notifications

When an editor approves content:
1. Content is automatically posted to Twitter (if connected)
2. Email notifications are sent to all subscribers of the publisher
3. Notifications include article details and links

## 🐦 Twitter Integration

- **OAuth 2.0 PKCE flow** for secure authentication
- **Automatic posting** when content is approved
- **Connection status** displayed in navigation
- **Manual disconnect** functionality

## 🚀 Deployment

### Docker Deployment (Recommended)

#### Quick Start with Docker Compose
```bash
# Clone and navigate to project
git clone <repository-url>
cd news_app

# Start all services (database + web app)
docker-compose up -d

# View logs
docker-compose logs -f web

# Access application
open http://localhost:8000
```

#### Docker Environment Configuration
Create a `.env` file for Docker deployment:
```env
# Twitter API (optional)
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
TWITTER_REDIRECT_URI=http://localhost:8000/accounts/twitter/callback/

# Email Configuration (optional)
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password

# Production Settings (for production deployment)
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

#### Docker Commands
```bash
# Build and start services
docker-compose up --build -d

# View application logs
docker-compose logs -f web

# View database logs
docker-compose logs -f db

# Stop services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Access Django shell in container
docker-compose exec web python manage.py shell

# Run migrations manually
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

#### What Docker Provides
- **✅ Consistent Environment**: Same setup across development, staging, and production
- **✅ MySQL Database**: Automatically configured and connected
- **✅ Dependency Management**: All Python packages pre-installed
- **✅ Test Data**: Automatically creates test users on startup
- **✅ Static Files**: Properly collected and served
- **✅ Health Checks**: Monitors application and database health
- **✅ Data Persistence**: Database data persists between container restarts

### Manual Production Deployment

#### Production Checklist
1. Set `DEBUG = False` in settings
2. Configure `ALLOWED_HOSTS`
3. Use production database
4. Set up static file serving
5. Configure email backend
6. Set up proper logging
7. Use environment variables for secrets

#### Environment Variables
```env
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=mysql://user:password@host:port/database
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the documentation
2. Review the API documentation
3. Check existing issues
4. Create a new issue with detailed information

## 🔄 Recent Updates

- ✅ Implemented role-based user model with proper field assignment
- ✅ Added comprehensive REST API with authentication
- ✅ Integrated Twitter posting for approved content
- ✅ Added email notifications for subscribers
- ✅ Implemented subscription-based content filtering
- ✅ Added publisher affiliation system for editors
- ✅ Created comprehensive test suite

## 📈 Future Enhancements

- [ ] Real-time notifications using WebSockets
- [ ] Advanced content analytics
- [ ] Multi-language support
- [ ] Mobile app integration
- [ ] Advanced search functionality
- [ ] Content recommendation system
- [ ] Social media integration (Facebook, LinkedIn)
- [ ] Advanced reporting and analytics dashboard

---

**Built with ❤️ using Django and modern web technologies**

