API Endpoints Reference
=======================

This section provides detailed information about all available API endpoints.

Authentication Endpoints
========================

Get Authentication Token
-------------------------

**Endpoint**: ``POST /api/auth/token/``

**Description**: Obtain an authentication token for API access.

**Authentication**: None required

**Request Body**:

.. code-block:: json

    {
        "username": "string",
        "password": "string"
    }

**Response**:

.. code-block:: json

    {
        "token": "string"
    }

**Status Codes**:
* ``200 OK`` - Token generated successfully
* ``400 Bad Request`` - Invalid credentials

Articles Endpoints
==================

List Articles
-------------

**Endpoint**: ``GET /api/articles/``

**Description**: Get a list of articles filtered by user role and subscriptions.

**Authentication**: Required

**Query Parameters**: None

**Response**:

.. code-block:: json

    [
        {
            "id": 1,
            "title": "Article Title",
            "body_preview": "First 200 characters of article...",
            "author_username": "journalist1",
            "publisher_name": "Tech News",
            "is_approved": true,
            "is_approved_display": "Approved",
            "created_at_formatted": "2025-01-19 10:30:00"
        }
    ]

**Filtering Logic**:
* **Readers**: Articles from subscribed publishers and followed journalists
* **Journalists/Editors**: All articles

Get Article Details
-------------------

**Endpoint**: ``GET /api/articles/{id}/``

**Description**: Get detailed information about a specific article.

**Authentication**: Required

**Path Parameters**:
* ``id`` (integer): Article ID

**Response**:

.. code-block:: json

    {
        "id": 1,
        "title": "Article Title",
        "body": "Full article content...",
        "author": {
            "id": 2,
            "username": "journalist1",
            "email": "journalist@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": "journalist",
            "role_display": "Journalist"
        },
        "publisher": {
            "id": 1,
            "name": "Tech News"
        },
        "author_username": "journalist1",
        "publisher_name": "Tech News",
        "is_approved": true,
        "is_approved_display": "Approved",
        "approved_by": 3,
        "created_at": "2025-01-19T10:30:00Z",
        "created_at_formatted": "2025-01-19 10:30:00"
    }

**Status Codes**:
* ``200 OK`` - Article found
* ``404 Not Found`` - Article not found

Newsletters Endpoints
=====================

List Newsletters
----------------

**Endpoint**: ``GET /api/newsletters/``

**Description**: Get a list of newsletters filtered by user role and subscriptions.

**Authentication**: Required

**Response**:

.. code-block:: json

    [
        {
            "id": 1,
            "subject": "Newsletter Subject",
            "content_preview": "First 200 characters of content...",
            "author_username": "journalist1",
            "publisher_name": "Tech News",
            "created_at_formatted": "2025-01-19 10:30:00"
        }
    ]

Get Newsletter Details
----------------------

**Endpoint**: ``GET /api/newsletters/{id}/``

**Description**: Get detailed information about a specific newsletter.

**Authentication**: Required

**Path Parameters**:
* ``id`` (integer): Newsletter ID

**Response**:

.. code-block:: json

    {
        "id": 1,
        "subject": "Newsletter Subject",
        "content": "Full newsletter content...",
        "author": {
            "id": 2,
            "username": "journalist1",
            "email": "journalist@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": "journalist",
            "role_display": "Journalist"
        },
        "publisher": {
            "id": 1,
            "name": "Tech News"
        },
        "author_username": "journalist1",
        "publisher_name": "Tech News",
        "created_at": "2025-01-19T10:30:00Z",
        "created_at_formatted": "2025-01-19 10:30:00"
    }

Publishers Endpoints
====================

List Publishers
---------------

**Endpoint**: ``GET /api/publishers/``

**Description**: Get a list of all publishers.

**Authentication**: Required

**Response**:

.. code-block:: json

    [
        {
            "id": 1,
            "name": "Tech News"
        },
        {
            "id": 2,
            "name": "Sports Daily"
        }
    ]

Get Publisher Details
---------------------

**Endpoint**: ``GET /api/publishers/{id}/``

**Description**: Get detailed information about a specific publisher.

**Authentication**: Required

**Path Parameters**:
* ``id`` (integer): Publisher ID

**Response**:

.. code-block:: json

    {
        "id": 1,
        "name": "Tech News"
    }

Journalists Endpoints
=====================

List Journalists
----------------

**Endpoint**: ``GET /api/journalists/``

**Description**: Get a list of all journalists.

**Authentication**: Required

**Response**:

.. code-block:: json

    [
        {
            "id": 2,
            "username": "journalist1",
            "email": "journalist@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "role": "journalist",
            "role_display": "Journalist",
            "affiliated_publisher": null
        }
    ]

Subscriptions Endpoints
=======================

Get User Subscriptions
-----------------------

**Endpoint**: ``GET /api/subscriptions/``

**Description**: Get the current user's subscriptions to publishers and journalists.

**Authentication**: Required

**Response**:

.. code-block:: json

    {
        "subscribed_publishers": [
            {
                "id": 1,
                "name": "Tech News"
            }
        ],
        "followed_journalists": [
            {
                "id": 2,
                "username": "journalist1",
                "email": "journalist@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "role": "journalist",
                "role_display": "Journalist"
            }
        ]
    }

Add Subscription
----------------

**Endpoint**: ``POST /api/subscriptions/``

**Description**: Add a subscription to a publisher or follow a journalist.

**Authentication**: Required

**Request Body** (Publisher):

.. code-block:: json

    {
        "publisher_id": 1
    }

**Request Body** (Journalist):

.. code-block:: json

    {
        "journalist_id": 2
    }

**Response**:

.. code-block:: json

    {
        "message": "Now subscribed to Tech News"
    }

**Status Codes**:
* ``201 Created`` - Subscription added successfully
* ``400 Bad Request`` - Invalid request data
* ``404 Not Found`` - Publisher or journalist not found

Remove Subscription
-------------------

**Endpoint**: ``DELETE /api/subscriptions/``

**Description**: Remove a subscription to a publisher or unfollow a journalist.

**Authentication**: Required

**Request Body**: Same format as POST

**Response**:

.. code-block:: json

    {
        "message": "Unsubscribed from Tech News"
    }

**Status Codes**:
* ``200 OK`` - Subscription removed successfully
* ``400 Bad Request`` - Invalid request data
* ``404 Not Found`` - Publisher or journalist not found

Feed Endpoints
==============

Get Combined Feed
-----------------

**Endpoint**: ``GET /api/feed/``

**Description**: Get a combined feed of articles and newsletters based on user subscriptions.

**Authentication**: Required

**Response**:

.. code-block:: json

    {
        "articles": [
            {
                "id": 1,
                "title": "Article Title",
                "body_preview": "Article preview...",
                "author_username": "journalist1",
                "publisher_name": "Tech News",
                "is_approved": true,
                "is_approved_display": "Approved",
                "created_at_formatted": "2025-01-19 10:30:00"
            }
        ],
        "newsletters": [
            {
                "id": 1,
                "subject": "Newsletter Subject",
                "content_preview": "Newsletter preview...",
                "author_username": "journalist1",
                "publisher_name": "Tech News",
                "created_at_formatted": "2025-01-19 10:30:00"
            }
        ],
        "total_articles": 10,
        "total_newsletters": 5
    }

**Note**: Returns the latest 10 items of each type.

Utility Endpoints
=================

Get API Information
-------------------

**Endpoint**: ``GET /api/info/``

**Description**: Get information about the API and available endpoints.

**Authentication**: None required

**Response**:

.. code-block:: json

    {
        "api_name": "News Application API",
        "version": "1.0",
        "description": "RESTful API for retrieving articles and newsletters from publishers and journalists",
        "endpoints": {
            "articles": {
                "list": "/api/articles/",
                "detail": "/api/articles/{id}/"
            },
            "newsletters": {
                "list": "/api/newsletters/",
                "detail": "/api/newsletters/{id}/"
            },
            "publishers": {
                "list": "/api/publishers/",
                "detail": "/api/publishers/{id}/"
            },
            "journalists": {
                "list": "/api/journalists/"
            },
            "subscriptions": {
                "manage": "/api/subscriptions/"
            },
            "feed": {
                "combined": "/api/feed/"
            }
        },
        "authentication": {
            "methods": ["Session", "Token"],
            "token_endpoint": "/api/auth/token/"
        },
        "formats": ["JSON", "XML"],
        "pagination": "Page-based (20 items per page)"
    }

Error Responses
===============

All endpoints may return the following error responses:

Authentication Errors
---------------------

**401 Unauthorized**:

.. code-block:: json

    {
        "detail": "Authentication credentials were not provided."
    }

**403 Forbidden**:

.. code-block:: json

    {
        "detail": "You do not have permission to perform this action."
    }

Validation Errors
-----------------

**400 Bad Request**:

.. code-block:: json

    {
        "field_name": [
            "This field is required."
        ]
    }

Not Found Errors
----------------

**404 Not Found**:

.. code-block:: json

    {
        "detail": "Not found."
    }

Server Errors
-------------

**500 Internal Server Error**:

.. code-block:: json

    {
        "detail": "A server error occurred."
    }
