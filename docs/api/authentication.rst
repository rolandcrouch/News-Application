API Authentication
==================

The Django News Application API uses token-based authentication for secure access to all endpoints.

Authentication Methods
======================

Token Authentication
--------------------

The primary authentication method is token-based authentication using Django REST Framework's built-in token system.

Getting a Token
===============

To obtain an authentication token, send a POST request to the token endpoint:

**Endpoint**: ``POST /api/auth/token/``

**Request**:

.. code-block:: bash

    curl -X POST http://localhost:8000/api/auth/token/ \
         -H "Content-Type: application/json" \
         -d '{
             "username": "your_username",
             "password": "your_password"
         }'

**Response**:

.. code-block:: json

    {
        "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
    }

Using the Token
===============

Include the token in the Authorization header of all API requests:

**Header Format**:
``Authorization: Token your_token_here``

**Example Request**:

.. code-block:: bash

    curl -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
         http://localhost:8000/api/articles/

Authentication Examples
=======================

Python with requests
--------------------

.. code-block:: python

    import requests
    
    # Get token
    response = requests.post('http://localhost:8000/api/auth/token/', {
        'username': 'your_username',
        'password': 'your_password'
    })
    token = response.json()['token']
    
    # Use token in subsequent requests
    headers = {'Authorization': f'Token {token}'}
    articles = requests.get('http://localhost:8000/api/articles/', headers=headers)
    print(articles.json())

JavaScript with fetch
---------------------

.. code-block:: javascript

    // Get token
    const tokenResponse = await fetch('http://localhost:8000/api/auth/token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: 'your_username',
            password: 'your_password'
        })
    });
    const { token } = await tokenResponse.json();
    
    // Use token in subsequent requests
    const articlesResponse = await fetch('http://localhost:8000/api/articles/', {
        headers: {
            'Authorization': `Token ${token}`
        }
    });
    const articles = await articlesResponse.json();
    console.log(articles);

Role-based Access Control
=========================

Different user roles have access to different API endpoints and data:

Reader Access
-------------

Readers can:
* View articles from subscribed publishers and followed journalists
* View newsletters from subscribed publishers and followed journalists
* Manage their own subscriptions
* Browse all approved content

**Filtered Content**: Readers only see content relevant to their subscriptions in list endpoints.

Journalist Access
-----------------

Journalists can:
* View all articles and newsletters in the system
* Create new articles and newsletters (via web interface)
* View all publishers and other journalists

**Full Content Access**: Journalists see all content regardless of approval status.

Editor Access
-------------

Editors can:
* View all articles and newsletters in the system
* Approve/reject content (via web interface)
* View all publishers and journalists

**Administrative Access**: Editors have the same viewing permissions as journalists plus approval capabilities.

Authentication Errors
=====================

Common authentication errors and their meanings:

401 Unauthorized
----------------

.. code-block:: json

    {
        "detail": "Authentication credentials were not provided."
    }

**Cause**: No Authorization header provided
**Solution**: Include the Authorization header with a valid token

.. code-block:: json

    {
        "detail": "Invalid token."
    }

**Cause**: Token is invalid or expired
**Solution**: Obtain a new token using the ``/api/auth/token/`` endpoint

403 Forbidden
--------------

.. code-block:: json

    {
        "detail": "You do not have permission to perform this action."
    }

**Cause**: Valid authentication but insufficient permissions
**Solution**: Ensure your user role has access to the requested resource

Token Management
================

Token Security
--------------

* **Keep tokens secure**: Never expose tokens in client-side code or logs
* **Use HTTPS**: Always use HTTPS in production to protect tokens in transit
* **Token rotation**: Consider implementing token rotation for enhanced security

Token Lifetime
--------------

By default, Django REST Framework tokens do not expire. In production, consider:

* Implementing token expiration
* Regular token rotation
* Monitoring token usage

Session Authentication
=====================

For web interface access, the application also supports session-based authentication.
This is primarily used by the Django admin and web views, not the API.

Testing Authentication
======================

You can test authentication using the included test users:

.. code-block:: bash

    # Test with reader account
    curl -X POST http://localhost:8000/api/auth/token/ \
         -H "Content-Type: application/json" \
         -d '{"username": "reader1", "password": "testpass123"}'
    
    # Test with journalist account
    curl -X POST http://localhost:8000/api/auth/token/ \
         -H "Content-Type: application/json" \
         -d '{"username": "journalist1", "password": "testpass123"}'
    
    # Test with editor account
    curl -X POST http://localhost:8000/api/auth/token/ \
         -H "Content-Type: application/json" \
         -d '{"username": "editor1", "password": "testpass123"}'

**Note**: Test users are created by running ``python create_test_users.py``
