# News Application RESTful API Documentation

## Overview

The News Application API provides RESTful endpoints for retrieving articles and newsletters from publishers and journalists that third-party clients have subscribed to. The API supports both JSON format and includes authentication via tokens.

## Base URL

```
http://127.0.0.1:8000/api/
```

## Authentication

The API uses token-based authentication. To access protected endpoints:

1. **Get a token**: POST to `/api/auth/token/` with username and password
2. **Use the token**: Include `Authorization: Token <your_token>` in request headers

### Example Authentication

```bash
# Get token
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Use token in requests
curl -H "Authorization: Token <your_token>" \
  http://127.0.0.1:8000/api/articles/
```

## Endpoints

### 1. API Information

**GET** `/api/info/`

Returns API information and available endpoints.

**Response:**
```json
{
  "api_name": "News Application API",
  "version": "1.0",
  "description": "RESTful API for retrieving articles and newsletters",
  "endpoints": { ... },
  "authentication": { ... },
  "formats": ["JSON"],
  "pagination": "Page-based (20 items per page)"
}
```

### 2. Articles

#### List Articles
**GET** `/api/articles/`

Returns a paginated list of articles based on user subscriptions:
- **Readers**: Articles from followed journalists and subscribed publishers
- **Editors/Journalists**: All articles

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)

**Response:**
```json
{
  "count": 25,
  "next": "http://127.0.0.1:8000/api/articles/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Sample Article",
      "body_preview": "This is a preview of the article content...",
      "author_username": "journalist1",
      "publisher_name": "Tech News",
      "is_approved": true,
      "is_approved_display": "Approved",
      "created_at_formatted": "2025-01-11 15:30:00"
    }
  ]
}
```

#### Get Article Detail
**GET** `/api/articles/{id}/`

Returns detailed information about a specific article.

**Response:**
```json
{
  "id": 1,
  "title": "Sample Article",
  "body": "Full article content here...",
  "author": {
    "id": 1,
    "username": "journalist1",
    "email": "journalist1@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "journalist",
    "role_display": "Journalist",
    "affiliated_publisher": null
  },
  "author_username": "journalist1",
  "publisher": {
    "id": 1,
    "name": "Tech News",
    "description": "Technology news publisher",
    "created_at": "2025-01-01T00:00:00Z"
  },
  "publisher_name": "Tech News",
  "is_approved": true,
  "is_approved_display": "Approved",
  "approved_by": 2,
  "created_at": "2025-01-11T15:30:00Z",
  "created_at_formatted": "2025-01-11 15:30:00"
}
```

### 3. Newsletters

#### List Newsletters
**GET** `/api/newsletters/`

Returns a paginated list of newsletters based on user subscriptions.

**Response:** Similar to articles but for newsletters.

#### Get Newsletter Detail
**GET** `/api/newsletters/{id}/`

Returns detailed information about a specific newsletter.

### 4. Publishers

#### List Publishers
**GET** `/api/publishers/`

Returns a list of all publishers.

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Tech News",
      "description": "Technology news publisher",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

#### Get Publisher Detail
**GET** `/api/publishers/{id}/`

Returns detailed information about a specific publisher.

### 5. Journalists

#### List Journalists
**GET** `/api/journalists/`

Returns a list of all journalists.

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "journalist1",
      "email": "journalist1@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "journalist",
      "role_display": "Journalist",
      "affiliated_publisher": null
    }
  ]
}
```

### 6. Subscriptions

#### Get Subscriptions
**GET** `/api/subscriptions/`

Returns user's current subscriptions.

**Response:**
```json
{
  "subscribed_publishers": [
    {
      "id": 1,
      "name": "Tech News",
      "description": "Technology news publisher",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "followed_journalists": [
    {
      "id": 1,
      "username": "journalist1",
      "email": "journalist1@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "journalist",
      "role_display": "Journalist",
      "affiliated_publisher": null
    }
  ]
}
```

#### Add Subscription
**POST** `/api/subscriptions/`

Add a new subscription.

**Request Body:**
```json
{
  "journalist_id": 1
}
```
or
```json
{
  "publisher_id": 1
}
```

**Response:**
```json
{
  "message": "Now following journalist1"
}
```

#### Remove Subscription
**DELETE** `/api/subscriptions/`

Remove a subscription.

**Request Body:** Same as POST

**Response:**
```json
{
  "message": "Unfollowed journalist1"
}
```

### 7. Combined Feed

#### Get User Feed
**GET** `/api/feed/`

Returns a combined feed of articles and newsletters based on user subscriptions.

**Response:**
```json
{
  "articles": [
    {
      "id": 1,
      "title": "Sample Article",
      "body_preview": "Article preview...",
      "author_username": "journalist1",
      "publisher_name": "Tech News",
      "is_approved": true,
      "is_approved_display": "Approved",
      "created_at_formatted": "2025-01-11 15:30:00"
    }
  ],
  "newsletters": [
    {
      "id": 1,
      "title": "Weekly Newsletter",
      "body_preview": "Newsletter preview...",
      "author_username": "editor1",
      "publisher_name": "Tech News",
      "created_at_formatted": "2025-01-11 15:30:00"
    }
  ],
  "total_articles": 1,
  "total_newsletters": 1
}
```

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 400 Bad Request
```json
{
  "error": "Must provide journalist_id or publisher_id"
}
```

## Usage Examples

### Using curl

```bash
# Get API info
curl http://127.0.0.1:8000/api/info/

# Get token
TOKEN=$(curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}' \
  | jq -r '.token')

# Get articles
curl -H "Authorization: Token $TOKEN" \
  http://127.0.0.1:8000/api/articles/

# Get user feed
curl -H "Authorization: Token $TOKEN" \
  http://127.0.0.1:8000/api/feed/

# Follow a journalist
curl -X POST -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"journalist_id": 1}' \
  http://127.0.0.1:8000/api/subscriptions/
```

### Using Python requests

```python
import requests

# Get token
response = requests.post('http://127.0.0.1:8000/api/auth/token/', 
                        json={'username': 'your_username', 'password': 'your_password'})
token = response.json()['token']

# Set up headers
headers = {'Authorization': f'Token {token}'}

# Get articles
articles = requests.get('http://127.0.0.1:8000/api/articles/', headers=headers)
print(articles.json())

# Get user feed
feed = requests.get('http://127.0.0.1:8000/api/feed/', headers=headers)
print(feed.json())
```

## Pagination

All list endpoints support pagination with the following parameters:
- `page`: Page number (1-based)
- `page_size`: Number of items per page (max 100)

Response includes:
- `count`: Total number of items
- `next`: URL for next page (null if last page)
- `previous`: URL for previous page (null if first page)
- `results`: Array of items for current page

## Rate Limiting

Currently no rate limiting is implemented, but it's recommended to implement appropriate rate limiting for production use.

## Security Considerations

1. **Token Security**: Keep your API tokens secure and don't expose them in client-side code
2. **HTTPS**: Use HTTPS in production to protect token transmission
3. **Token Rotation**: Consider implementing token rotation for enhanced security
4. **Input Validation**: All input is validated on the server side

## Support

For API support or questions, please refer to the application documentation or contact the development team.

