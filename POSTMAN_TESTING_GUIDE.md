# Postman Testing Guide for News Application API

## Overview
This guide provides comprehensive instructions for testing the News Application RESTful API using Postman. The API supports subscription-based content filtering, allowing third-party clients to retrieve articles and newsletters based on their subscriptions.

## Base URL
```
http://127.0.0.1:8002/api/
```

## Authentication
The API supports two authentication methods:
1. **Token Authentication** (Recommended for API clients)
2. **Session Authentication** (For web applications)

### Getting an Authentication Token
1. **Method**: POST
2. **URL**: `http://127.0.0.1:8002/api/auth/token/`
3. **Headers**: 
   - `Content-Type: application/json`
4. **Body** (JSON):
   ```json
   {
       "username": "your_username",
       "password": "your_password"
   }
   ```
5. **Response**: 
   ```json
   {
       "token": "your_auth_token_here"
   }
   ```

### Using the Token
Add the token to all subsequent requests:
- **Header**: `Authorization: Token your_auth_token_here`

## API Endpoints

### 1. API Information (No Authentication Required)
- **Method**: GET
- **URL**: `http://127.0.0.1:8002/api/info/`
- **Description**: Get API information and available endpoints
- **Response**: API metadata and endpoint list

### 2. Articles

#### List Articles
- **Method**: GET
- **URL**: `http://127.0.0.1:8002/api/articles/`
- **Authentication**: Required
- **Query Parameters**:
  - `page`: Page number (default: 1)
  - `page_size`: Items per page (default: 20, max: 100)
- **Response**: Paginated list of articles with subscription-based filtering

#### Get Article Detail
- **Method**: GET
- **URL**: `http://127.0.0.1:8002/api/articles/{id}/`
- **Authentication**: Required
- **Response**: Detailed article information

### 3. Newsletters

#### List Newsletters
- **Method**: GET
- **URL**: `http://127.0.0.1:8002/api/newsletters/`
- **Authentication**: Required
- **Query Parameters**: Same as articles
- **Response**: Paginated list of newsletters with subscription-based filtering

#### Get Newsletter Detail
- **Method**: GET
- **URL**: `http://127.0.0.1:8002/api/newsletters/{id}/`
- **Authentication**: Required
- **Response**: Detailed newsletter information

### 4. Publishers

#### List Publishers
- **Method**: GET
- **URL**: `http://127.0.0.1:8002/api/publishers/`
- **Authentication**: Required
- **Response**: List of all publishers

#### Get Publisher Detail
- **Method**: GET
- **URL**: `http://127.0.0.1:8002/api/publishers/{id}/`
- **Authentication**: Required
- **Response**: Detailed publisher information

### 5. Journalists

#### List Journalists
- **Method**: GET
- **URL**: `http://127.0.0.1:8002/api/journalists/`
- **Authentication**: Required
- **Response**: List of all journalists

### 6. Subscriptions Management

#### Get User Subscriptions
- **Method**: GET
- **URL**: `http://127.0.0.1:8002/api/subscriptions/`
- **Authentication**: Required
- **Response**: User's current subscriptions

#### Add Publisher Subscription
- **Method**: POST
- **URL**: `http://127.0.0.1:8002/api/subscriptions/`
- **Authentication**: Required
- **Headers**: `Content-Type: application/json`
- **Body** (JSON):
  ```json
  {
      "publisher_id": 1
  }
  ```

#### Add Journalist Subscription
- **Method**: POST
- **URL**: `http://127.0.0.1:8002/api/subscriptions/`
- **Authentication**: Required
- **Headers**: `Content-Type: application/json`
- **Body** (JSON):
  ```json
  {
      "journalist_id": 1
  }
  ```

#### Remove Publisher Subscription
- **Method**: DELETE
- **URL**: `http://127.0.0.1:8002/api/subscriptions/`
- **Authentication**: Required
- **Headers**: `Content-Type: application/json`
- **Body** (JSON):
  ```json
  {
      "publisher_id": 1
  }
  ```

#### Remove Journalist Subscription
- **Method**: DELETE
- **URL**: `http://127.0.0.1:8002/api/subscriptions/`
- **Authentication**: Required
- **Headers**: `Content-Type: application/json`
- **Body** (JSON):
  ```json
  {
      "journalist_id": 1
  }
  ```

### 7. Combined Feed

#### Get Personalized Feed
- **Method**: GET
- **URL**: `http://127.0.0.1:8002/api/feed/`
- **Authentication**: Required
- **Description**: Returns combined articles and newsletters based on user subscriptions
- **Response**: Combined feed with subscription-based filtering

## Testing Scenarios

### Scenario 1: Reader with Subscriptions
1. **Create a Reader Account** (via Django admin or registration)
2. **Get Authentication Token**
3. **Subscribe to Publishers and Journalists**
4. **Test Content Filtering**:
   - Get articles - should only see subscribed content
   - Get newsletters - should only see subscribed content
   - Get feed - should see combined subscribed content

### Scenario 2: Editor Access
1. **Create an Editor Account** with publisher affiliation
2. **Get Authentication Token**
3. **Test Full Access**:
   - Get articles - should see all content
   - Get newsletters - should see all content
   - Get feed - should see all content

### Scenario 3: Journalist Access
1. **Create a Journalist Account**
2. **Get Authentication Token**
3. **Test Full Access**:
   - Get articles - should see all content
   - Get newsletters - should see all content
   - Get feed - should see all content

## Sample Postman Collection

### Environment Variables
Create a Postman environment with these variables:
- `base_url`: `http://127.0.0.1:8002/api`
- `auth_token`: (will be set after authentication)

### Collection Structure
1. **Authentication**
   - POST `/auth/token/` - Get token
   
2. **Articles**
   - GET `/articles/` - List articles
   - GET `/articles/{id}/` - Get article detail
   
3. **Newsletters**
   - GET `/newsletters/` - List newsletters
   - GET `/newsletters/{id}/` - Get newsletter detail
   
4. **Publishers**
   - GET `/publishers/` - List publishers
   - GET `/publishers/{id}/` - Get publisher detail
   
5. **Journalists**
   - GET `/journalists/` - List journalists
   
6. **Subscriptions**
   - GET `/subscriptions/` - Get subscriptions
   - POST `/subscriptions/` - Add subscription
   - DELETE `/subscriptions/` - Remove subscription
   
7. **Feed**
   - GET `/feed/` - Get personalized feed

## Expected Responses

### Successful Article List Response
```json
{
    "count": 10,
    "next": "http://127.0.0.1:8002/api/articles/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Sample Article",
            "body": "Article content...",
            "author_username": "journalist1",
            "publisher_name": "Tech News",
            "is_approved": true,
            "is_approved_display": "Approved",
            "created_at": "2025-09-11T15:30:00Z",
            "created_at_formatted": "2025-09-11 15:30:00"
        }
    ]
}
```

### Successful Subscription Response
```json
{
    "message": "Now subscribed to Tech News",
    "subscribed_publishers": [
        {
            "id": 1,
            "name": "Tech News"
        }
    ],
    "followed_journalists": []
}
```

### Error Responses
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Valid authentication but insufficient permissions
- **404 Not Found**: Resource not found
- **400 Bad Request**: Invalid request data

## Testing Subscription-Based Filtering

### Test Case 1: Reader Sees Only Subscribed Content
1. Create a reader account
2. Subscribe to Publisher A and Journalist B
3. Create articles:
   - Article 1: Published by Publisher A
   - Article 2: Published by Publisher B (not subscribed)
   - Article 3: Independent article by Journalist B
   - Article 4: Independent article by Journalist C (not followed)
4. Get articles - should only see Article 1 and Article 3

### Test Case 2: Editor Sees All Content
1. Create an editor account
2. Get articles - should see all articles regardless of subscriptions

### Test Case 3: Journalist Sees All Content
1. Create a journalist account
2. Get articles - should see all articles regardless of subscriptions

## Performance Testing

### Load Testing with Postman
1. **Create a Collection Runner** with multiple iterations
2. **Test Concurrent Requests** to different endpoints
3. **Monitor Response Times** for pagination
4. **Test Large Datasets** with high page numbers

### Memory Testing
1. **Test Large Page Sizes** (up to max 100)
2. **Test Deep Pagination** (high page numbers)
3. **Monitor Server Performance** during tests

## Troubleshooting

### Common Issues
1. **401 Unauthorized**: Check token validity and format
2. **403 Forbidden**: Verify user has appropriate role
3. **404 Not Found**: Check URL and resource existence
4. **500 Internal Server Error**: Check server logs for details

### Debug Tips
1. **Enable Postman Console** to see request/response details
2. **Check Response Headers** for additional information
3. **Verify JSON Format** in request bodies
4. **Test with Different User Roles** to verify permissions

## Security Considerations

1. **Token Security**: Store tokens securely, don't log them
2. **HTTPS**: Use HTTPS in production environments
3. **Rate Limiting**: Be aware of potential rate limits
4. **Input Validation**: Test with invalid data to verify validation

## Conclusion

This API provides comprehensive functionality for third-party clients to access news content with proper subscription-based filtering. The unit tests ensure reliability, and Postman testing verifies real-world functionality.

For additional support or questions, refer to the API documentation or contact the development team.

