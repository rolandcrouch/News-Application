Testing Documentation
====================

The Django News Application includes a comprehensive test suite covering all aspects of the application.

Test Suite Overview
===================

The application includes 60+ test cases covering:

* **Model Tests**: User model, Article model, Newsletter model, Publisher model
* **Form Tests**: Registration forms, content creation forms, validation
* **View Tests**: Authentication views, CRUD operations, permissions
* **API Tests**: REST API endpoints, serialization, authentication
* **Integration Tests**: Twitter integration, email notifications
* **Security Tests**: Permission checks, role-based access control

Running Tests
=============

Basic Test Execution
--------------------

Run all tests:

.. code-block:: bash

    python run_tests.py

Run with verbose output:

.. code-block:: bash

    python run_tests.py --verbose

Run specific test class:

.. code-block:: bash

    python run_tests.py --specific UserModelTest

Run fast tests only (excludes integration tests):

.. code-block:: bash

    python run_tests.py --fast

Test Coverage
-------------

Run tests with coverage report:

.. code-block:: bash

    python run_tests.py --coverage

This generates:
- Console coverage report
- HTML coverage report in ``htmlcov/index.html``

Using Django's Test Runner
--------------------------

You can also use Django's built-in test runner:

.. code-block:: bash

    # Run all tests
    python manage.py test
    
    # Run specific app tests
    python manage.py test articles
    
    # Run specific test class
    python manage.py test articles.tests.UserModelTest
    
    # Run with verbose output
    python manage.py test --verbosity=2

Test Categories
===============

Model Tests
-----------

**UserModelTest**
Tests the custom User model functionality:

.. code-block:: python

    def test_create_reader_user(self):
        """Test creating a reader user"""
        user = User.objects.create_user(
            username="reader1",
            email="reader@test.com",
            password="testpass123",
            role=User.Roles.READER
        )
        self.assertEqual(user.role, User.Roles.READER)

**ArticleModelTest**
Tests Article model and relationships:

.. code-block:: python

    def test_create_article(self):
        """Test creating an article"""
        article = Article.objects.create(
            title="Test Article",
            body="Article content",
            author=self.journalist
        )
        self.assertEqual(article.title, "Test Article")
        self.assertFalse(article.is_approved)

**NewsletterModelTest**
Tests Newsletter model functionality:

.. code-block:: python

    def test_create_newsletter(self):
        """Test creating a newsletter"""
        newsletter = Newsletter.objects.create(
            subject="Test Newsletter",
            content="Newsletter content",
            author=self.journalist
        )
        self.assertEqual(newsletter.subject, "Test Newsletter")

**PublisherModelTest**
Tests Publisher model and constraints:

.. code-block:: python

    def test_create_publisher(self):
        """Test creating a publisher"""
        publisher = Publisher.objects.create(name="Test Publisher")
        self.assertEqual(publisher.name, "Test Publisher")

Form Tests
----------

**UserRegistrationFormTest**
Tests user registration form validation:

.. code-block:: python

    def test_valid_reader_registration(self):
        """Test valid reader registration"""
        form_data = {
            'username': 'newreader',
            'email': 'reader@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'role': User.Roles.READER,
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

**ArticleFormTest**
Tests article creation form:

.. code-block:: python

    def test_valid_article_form(self):
        """Test valid article form"""
        form_data = {
            'title': 'Test Article',
            'body': 'This is a test article content.',
            'publisher': self.publisher.id
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid())

View Tests
----------

**AuthenticationViewTest**
Tests login, logout, and registration views:

.. code-block:: python

    def test_user_registration(self):
        """Test user registration view"""
        response = self.client.post('/accounts/register/', {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'role': User.Roles.READER,
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success

**ArticleViewTest**
Tests article CRUD operations:

.. code-block:: python

    def test_article_create_view_journalist(self):
        """Test article creation by journalist"""
        self.client.login(username='journalist1', password='testpass123')
        response = self.client.post('/accounts/articles/new/', {
            'title': 'New Article',
            'body': 'Article content',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Article.objects.filter(title='New Article').exists())

API Tests
---------

**APISerializerTests**
Tests REST API serialization:

.. code-block:: python

    def test_article_serializer(self):
        """Test article serializer"""
        serializer = ArticleSerializer(instance=self.article)
        data = serializer.data
        self.assertEqual(data['title'], self.article.title)
        self.assertEqual(data['author_username'], self.article.author.username)

**APIEndpointTests**
Tests API endpoints and authentication:

.. code-block:: python

    def test_articles_list_authenticated(self):
        """Test articles list with authentication"""
        response = self.client.get('/api/articles/', 
                                 HTTP_AUTHORIZATION=f'Token {self.token}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

Integration Tests
-----------------

**TwitterIntegrationTest**
Tests Twitter OAuth and posting functionality:

.. code-block:: python

    @patch('articles.functions.tweet.TwitterAPI')
    def test_twitter_post_creation(self, mock_twitter_api):
        """Test Twitter post creation"""
        mock_instance = mock_twitter_api.return_value
        mock_instance.post_tweet.return_value = {'id': '12345'}
        
        # Test Twitter posting logic
        result = post_to_twitter(self.article)
        self.assertTrue(result['success'])

**EmailNotificationTest**
Tests email notification system:

.. code-block:: python

    def test_article_approval_notification(self):
        """Test email notification on article approval"""
        # Subscribe reader to publisher
        self.reader.subscriptions_publishers.add(self.publisher)
        
        # Approve article
        self.article.is_approved = True
        self.article.save()
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.article.title, mail.outbox[0].subject)

Security Tests
--------------

**PermissionTest**
Tests role-based access control:

.. code-block:: python

    def test_reader_cannot_create_article(self):
        """Test that readers cannot create articles"""
        self.client.login(username='reader1', password='testpass123')
        response = self.client.get('/accounts/articles/new/')
        self.assertEqual(response.status_code, 403)  # Forbidden

    def test_journalist_can_edit_own_article(self):
        """Test that journalists can edit their own articles"""
        self.client.login(username='journalist1', password='testpass123')
        response = self.client.get(f'/accounts/articles/{self.article.id}/edit/')
        self.assertEqual(response.status_code, 200)

Test Data Setup
===============

The test suite uses factories and fixtures for consistent test data:

Test Users
----------

.. code-block:: python

    def setUp(self):
        """Set up test data"""
        self.publisher = Publisher.objects.create(name="Test Publisher")
        
        self.reader = User.objects.create_user(
            username='reader1',
            email='reader@test.com',
            password='testpass123',
            role=User.Roles.READER
        )
        
        self.journalist = User.objects.create_user(
            username='journalist1',
            email='journalist@test.com',
            password='testpass123',
            role=User.Roles.JOURNALIST
        )
        
        self.editor = User.objects.create_user(
            username='editor1',
            email='editor@test.com',
            password='testpass123',
            role=User.Roles.EDITOR,
            affiliated_publisher=self.publisher
        )

Test Content
------------

.. code-block:: python

    def create_test_article(self):
        """Create a test article"""
        return Article.objects.create(
            title="Test Article",
            body="This is a test article content.",
            author=self.journalist,
            publisher=self.publisher
        )

Test Configuration
==================

Test Settings
-------------

The application uses separate settings for testing:

.. code-block:: python

    # In settings.py or test_settings.py
    if 'test' in sys.argv:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        }
        
        EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
        
        # Disable migrations for faster tests
        MIGRATION_MODULES = {
            'articles': None,
        }

Test Database
-------------

Tests use an in-memory SQLite database for speed:

.. code-block:: bash

    # Test database is created automatically
    # No manual setup required

Mocking External Services
========================

Twitter API Mocking
-------------------

.. code-block:: python

    from unittest.mock import patch, MagicMock

    @patch('articles.functions.tweet.TwitterAPI')
    def test_twitter_integration(self, mock_twitter):
        """Test Twitter integration with mocked API"""
        mock_instance = mock_twitter.return_value
        mock_instance.authenticate.return_value = True
        mock_instance.post_tweet.return_value = {
            'data': {'id': '1234567890'}
        }
        
        # Test your Twitter integration code
        result = publish_to_twitter(self.article)
        self.assertTrue(result['success'])

Email Service Mocking
---------------------

.. code-block:: python

    from django.test import override_settings
    from django.core import mail

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_email_notification(self):
        """Test email notification"""
        send_notification_email(self.user, "Test Subject", "Test Message")
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Test Subject")

Continuous Integration
=====================

GitHub Actions
--------------

Create ``.github/workflows/test.yml``:

.. code-block:: yaml

    name: Tests
    
    on: [push, pull_request]
    
    jobs:
      test:
        runs-on: ubuntu-latest
        
        services:
          postgres:
            image: postgres:13
            env:
              POSTGRES_PASSWORD: postgres
            options: >-
              --health-cmd pg_isready
              --health-interval 10s
              --health-timeout 5s
              --health-retries 5
        
        steps:
        - uses: actions/checkout@v2
        
        - name: Set up Python
          uses: actions/setup-python@v2
          with:
            python-version: 3.9
        
        - name: Install dependencies
          run: |
            python -m pip install --upgrade pip
            pip install -r requirements.txt
        
        - name: Run tests
          run: |
            python run_tests.py --coverage
          env:
            DATABASE_URL: postgres://postgres:postgres@localhost/postgres

Test Automation
===============

Pre-commit Hooks
----------------

Install pre-commit hooks to run tests automatically:

.. code-block:: bash

    pip install pre-commit
    
    # Create .pre-commit-config.yaml
    cat > .pre-commit-config.yaml << EOF
    repos:
    -   repo: local
        hooks:
        -   id: django-test
            name: django-test
            entry: python run_tests.py --fast
            language: system
            pass_filenames: false
    EOF
    
    # Install hooks
    pre-commit install

Test Reporting
--------------

Generate test reports:

.. code-block:: bash

    # XML test report for CI
    python manage.py test --verbosity=2 --debug-mode --parallel 1 \
        --testrunner xmlrunner.extra.djangotestrunner.XMLTestRunner

Performance Testing
===================

Load Testing
-----------

Use tools like Apache Bench or Locust for load testing:

.. code-block:: bash

    # Simple load test with Apache Bench
    ab -n 1000 -c 10 http://localhost:8000/api/articles/

Database Performance
-------------------

Test database query performance:

.. code-block:: python

    from django.test import TestCase
    from django.test.utils import override_settings
    from django.db import connection

    class PerformanceTest(TestCase):
        def test_article_list_queries(self):
            """Test that article list doesn't have N+1 queries"""
            with self.assertNumQueries(3):  # Expected number of queries
                response = self.client.get('/api/articles/')
                self.assertEqual(response.status_code, 200)

Best Practices
==============

Test Organization
----------------

1. **One test per behavior**: Each test should test one specific behavior
2. **Descriptive names**: Use clear, descriptive test method names
3. **Setup and teardown**: Use setUp() and tearDown() methods properly
4. **Test isolation**: Tests should not depend on each other

Test Data
---------

1. **Use factories**: Create test data using factories or model methods
2. **Minimal data**: Create only the data needed for each test
3. **Clean state**: Ensure each test starts with a clean state

Assertions
----------

1. **Specific assertions**: Use the most specific assertion available
2. **Multiple assertions**: It's okay to have multiple assertions per test
3. **Error messages**: Provide helpful error messages for assertions

Coverage Goals
--------------

Aim for high test coverage:
- **Models**: 100% coverage
- **Views**: 90%+ coverage  
- **Forms**: 90%+ coverage
- **API**: 95%+ coverage
- **Utilities**: 90%+ coverage

Running Specific Tests
=====================

Test Selection
--------------

.. code-block:: bash

    # Run specific test method
    python manage.py test articles.tests.UserModelTest.test_create_reader_user
    
    # Run tests matching pattern
    python manage.py test articles.tests -k "test_create"
    
    # Run tests with tags
    python manage.py test --tag=slow

Test Debugging
--------------

.. code-block:: bash

    # Run with pdb debugger
    python manage.py test --debug-mode --verbosity=2
    
    # Keep test database for inspection
    python manage.py test --keepdb

This comprehensive test suite ensures the reliability and maintainability of the Django News Application.
