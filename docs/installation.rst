Installation Guide
==================

This guide will help you set up the Django News Application in different environments.

System Requirements
===================

* Python 3.8 or higher
* pip (Python package installer)
* Git
* SQLite (included with Python) or PostgreSQL (for production)

Development Setup
=================

1. Clone the Repository
-----------------------

.. code-block:: bash

    git clone <repository-url>
    cd django-news-application

2. Create Virtual Environment
-----------------------------

.. code-block:: bash

    python -m venv venv
    
    # On Windows
    venv\Scripts\activate
    
    # On macOS/Linux
    source venv/bin/activate

3. Install Dependencies
-----------------------

.. code-block:: bash

    pip install -r requirements.txt

4. Environment Configuration
----------------------------

Create a ``.env`` file in the project root (optional for development):

.. code-block:: bash

    # Database (optional - defaults to SQLite)
    DATABASE_URL=sqlite:///db.sqlite3
    
    # Twitter Integration (optional)
    TWITTER_CLIENT_ID=your_twitter_client_id
    TWITTER_CLIENT_SECRET=your_twitter_client_secret
    TWITTER_REDIRECT_URI=http://localhost:8000/accounts/twitter/callback/
    
    # Email Configuration (optional)
    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_HOST_USER=your_email@gmail.com
    EMAIL_HOST_PASSWORD=your_app_password
    EMAIL_USE_TLS=True

5. Database Setup
-----------------

.. code-block:: bash

    # Apply migrations
    python manage.py migrate
    
    # Create superuser account
    python manage.py createsuperuser
    
    # (Optional) Create test users
    python create_test_users.py

6. Run Development Server
-------------------------

.. code-block:: bash

    python manage.py runserver

The application will be available at:

* **Web Interface**: http://localhost:8000
* **API Root**: http://localhost:8000/api/
* **Admin Panel**: http://localhost:8000/admin/

Production Setup
================

Docker Deployment
-----------------

The application includes Docker support for easy deployment:

.. code-block:: bash

    # Build and run with Docker Compose
    docker-compose up --build
    
    # Run in detached mode
    docker-compose up -d

Manual Production Setup
-----------------------

1. **Install Production Dependencies**:

.. code-block:: bash

    pip install -r requirements.txt gunicorn psycopg2-binary

2. **Configure Environment Variables**:

.. code-block:: bash

    export DJANGO_SETTINGS_MODULE=news_app.settings
    export SECRET_KEY=your-secret-key
    export DEBUG=False
    export ALLOWED_HOSTS=your-domain.com
    export DATABASE_URL=postgresql://user:pass@localhost/dbname

3. **Database Setup**:

.. code-block:: bash

    python manage.py collectstatic --noinput
    python manage.py migrate
    python manage.py createsuperuser

4. **Run with Gunicorn**:

.. code-block:: bash

    gunicorn news_app.wsgi:application --bind 0.0.0.0:8000

Configuration Options
=====================

Django Settings
---------------

Key settings that can be customized:

* ``SECRET_KEY``: Django secret key (required in production)
* ``DEBUG``: Debug mode (set to False in production)
* ``ALLOWED_HOSTS``: Allowed hostnames
* ``DATABASE_URL``: Database connection string
* ``EMAIL_*``: Email configuration for notifications

Twitter Integration
-------------------

To enable Twitter integration:

1. **Create Twitter App**: Visit https://developer.twitter.com/
2. **Get Credentials**: Obtain Client ID and Client Secret
3. **Configure OAuth**: Set redirect URI to your domain + ``/accounts/twitter/callback/``
4. **Set Environment Variables**:

.. code-block:: bash

    TWITTER_CLIENT_ID=your_client_id
    TWITTER_CLIENT_SECRET=your_client_secret
    TWITTER_REDIRECT_URI=https://yourdomain.com/accounts/twitter/callback/

Email Configuration
-------------------

For email notifications, configure SMTP settings:

.. code-block:: python

    # Gmail example
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'your_email@gmail.com'
    EMAIL_HOST_PASSWORD = 'your_app_password'
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = 'your_email@gmail.com'

Testing the Installation
========================

1. **Run Test Suite**:

.. code-block:: bash

    python run_tests.py

2. **Test API Endpoints**:

.. code-block:: bash

    # Get API information
    curl http://localhost:8000/api/info/
    
    # Test authentication
    curl -X POST http://localhost:8000/api/auth/token/ \
         -H "Content-Type: application/json" \
         -d '{"username": "testuser", "password": "testpass123"}'

3. **Access Web Interface**:

Visit http://localhost:8000 and test:
* User registration
* Login/logout
* Content creation (if you have journalist/editor accounts)
* Subscription management

Troubleshooting
===============

Common Issues
-------------

**Import Errors**
    Make sure your virtual environment is activated and all dependencies are installed.

**Database Errors**
    Run ``python manage.py migrate`` to apply database migrations.

**Permission Errors**
    Ensure the application has write permissions to the database file and media directories.

**Twitter Integration Issues**
    Verify your Twitter app credentials and redirect URI configuration.

**Email Not Working**
    Check your SMTP settings and ensure "Less secure app access" is enabled for Gmail.

Getting Help
============

* **Documentation**: Full documentation available in the ``docs/`` directory
* **API Documentation**: Available at ``/api/info/`` endpoint
* **Test Examples**: See ``articles/test_api.py`` for API usage examples
* **Deployment Guide**: Check ``DEPLOYMENT_GUIDE.md`` for detailed deployment instructions

Development Tools
=================

The project includes several helpful development tools:

* **Test Runner**: ``python run_tests.py`` with various options
* **Test User Creator**: ``python create_test_users.py``
* **API Testing**: Postman collection available
* **Docker Support**: Multi-stage builds for development and production
* **Documentation**: Sphinx-based documentation system
