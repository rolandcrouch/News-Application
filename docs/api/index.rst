API Documentation
=================

The Django News Application provides a comprehensive REST API for all functionality.
This section covers authentication, endpoints, and usage examples.

.. toctree::
   :maxdepth: 2

   authentication
   endpoints
   examples

API Overview
============

The API is built using Django REST Framework and provides:

* **RESTful Design**: Standard HTTP methods and status codes
* **JSON Format**: All requests and responses use JSON
* **Token Authentication**: Secure token-based authentication
* **Role-based Access**: Different endpoints available based on user role
* **Comprehensive Coverage**: All web functionality available via API

Base URL
========

All API endpoints are prefixed with ``/api/``

* **Development**: ``http://localhost:8000/api/``
* **Production**: ``https://yourdomain.com/api/``

Quick Start
===========

1. **Get Authentication Token**:

.. code-block:: bash

    curl -X POST http://localhost:8000/api/auth/token/ \
         -H "Content-Type: application/json" \
         -d '{"username": "your_username", "password": "your_password"}'

2. **Use Token in Requests**:

.. code-block:: bash

    curl -H "Authorization: Token your_token_here" \
         http://localhost:8000/api/articles/

3. **Get API Information**:

.. code-block:: bash

    curl http://localhost:8000/api/info/

Available Endpoints
===================

Authentication
--------------

* ``POST /api/auth/token/`` - Get authentication token

Articles
--------

* ``GET /api/articles/`` - List articles (filtered by user role)
* ``GET /api/articles/{id}/`` - Get specific article

Newsletters
-----------

* ``GET /api/newsletters/`` - List newsletters (filtered by user role)
* ``GET /api/newsletters/{id}/`` - Get specific newsletter

Publishers
----------

* ``GET /api/publishers/`` - List all publishers
* ``GET /api/publishers/{id}/`` - Get specific publisher

Journalists
-----------

* ``GET /api/journalists/`` - List all journalists

Subscriptions
-------------

* ``GET /api/subscriptions/`` - Get user's current subscriptions
* ``POST /api/subscriptions/`` - Add subscription (journalist or publisher)
* ``DELETE /api/subscriptions/`` - Remove subscription

Feed
----

* ``GET /api/feed/`` - Get combined articles and newsletters feed

Utility
-------

* ``GET /api/info/`` - Get API information and available endpoints

Response Format
===============

All API responses follow a consistent format:

Success Response
----------------

.. code-block:: json

    {
        "id": 1,
        "title": "Article Title",
        "body": "Article content...",
        "author_username": "journalist1",
        "publisher_name": "Tech News",
        "is_approved": true,
        "created_at_formatted": "2025-01-19 10:30:00"
    }

Error Response
--------------

.. code-block:: json

    {
        "error": "Authentication credentials were not provided."
    }

Or for validation errors:

.. code-block:: json

    {
        "field_name": [
            "This field is required."
        ]
    }

HTTP Status Codes
=================

The API uses standard HTTP status codes:

* ``200 OK`` - Request successful
* ``201 Created`` - Resource created successfully
* ``400 Bad Request`` - Invalid request data
* ``401 Unauthorized`` - Authentication required
* ``403 Forbidden`` - Permission denied
* ``404 Not Found`` - Resource not found
* ``500 Internal Server Error`` - Server error

Rate Limiting
=============

Currently, there are no rate limits applied to the API. In production,
consider implementing rate limiting based on your requirements.

Pagination
==========

List endpoints support pagination:

.. code-block:: json

    {
        "count": 100,
        "next": "http://localhost:8000/api/articles/?page=2",
        "previous": null,
        "results": [...]
    }

Testing the API
===============

The project includes comprehensive API tests. Run them with:

.. code-block:: bash

    python run_tests.py --specific APISerializerTests

Or test manually using curl, Postman, or any HTTP client.
