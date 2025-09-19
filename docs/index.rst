Django News Application Documentation
=====================================

Welcome to the Django News Application documentation! This comprehensive guide covers
all aspects of the news application, from installation to API usage.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   installation
   api/index
   modules/index
   deployment
   testing

Overview
========

The Django News Application is a comprehensive news management system that supports
multiple user roles (Readers, Editors, Journalists) with features including:

* **Multi-role User System**: Readers, Editors, and Journalists with different permissions
* **Content Management**: Articles and newsletters with approval workflows
* **Publisher System**: Publishers can have affiliated editors and journalists
* **Subscription System**: Readers can follow journalists and subscribe to publishers
* **REST API**: Complete API for all functionality
* **Twitter Integration**: OAuth2-based Twitter posting for approved content
* **Email Notifications**: Automated notifications for new content

Key Features
============

User Roles
----------

* **Readers**: Can subscribe to publishers and follow journalists
* **Journalists**: Can create articles and newsletters, work independently or with publishers
* **Editors**: Can approve/reject content, manage publishers, and publish to Twitter

Content Types
-------------

* **Articles**: News articles with title, body, author, and optional publisher
* **Newsletters**: Email newsletters with subject, content, author, and optional publisher

Technical Stack
===============

* **Backend**: Django 5.2.6 with Django REST Framework
* **Database**: SQLite (development) / PostgreSQL (production)
* **Authentication**: Django's built-in auth with custom user model
* **API**: RESTful API with token authentication
* **Documentation**: Sphinx with Read the Docs theme
* **Testing**: Comprehensive test suite with 60+ test cases
* **Deployment**: Docker support with multi-stage builds

Quick Start
===========

1. **Installation**::

    git clone <repository-url>
    cd django-news-application
    pip install -r requirements.txt

2. **Database Setup**::

    python manage.py migrate
    python manage.py createsuperuser

3. **Run Development Server**::

    python manage.py runserver

4. **Access the Application**:
   
   * Web Interface: http://localhost:8000
   * API Root: http://localhost:8000/api/
   * Admin Panel: http://localhost:8000/admin/

API Quick Reference
===================

Authentication
--------------

All API endpoints require authentication. Get your token::

    POST /api/auth/token/
    {
        "username": "your_username",
        "password": "your_password"
    }

Main Endpoints
--------------

* **Articles**: ``/api/articles/`` (GET, POST)
* **Newsletters**: ``/api/newsletters/`` (GET, POST)
* **Publishers**: ``/api/publishers/`` (GET)
* **Journalists**: ``/api/journalists/`` (GET)
* **Subscriptions**: ``/api/subscriptions/`` (GET, POST, DELETE)
* **Feed**: ``/api/feed/`` (GET) - Combined articles and newsletters

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`