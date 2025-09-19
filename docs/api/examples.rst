API Usage Examples
==================

This section provides practical examples of using the Django News Application API.

Basic Authentication Flow
=========================

Python Example
--------------

.. code-block:: python

    import requests
    import json

    # Base URL
    BASE_URL = 'http://localhost:8000/api'

    class NewsAPIClient:
        def __init__(self, base_url=BASE_URL):
            self.base_url = base_url
            self.token = None
            self.session = requests.Session()

        def authenticate(self, username, password):
            """Get authentication token"""
            response = self.session.post(f'{self.base_url}/auth/token/', {
                'username': username,
                'password': password
            })
            
            if response.status_code == 200:
                self.token = response.json()['token']
                self.session.headers.update({
                    'Authorization': f'Token {self.token}'
                })
                return True
            return False

        def get_articles(self):
            """Get articles for the authenticated user"""
            response = self.session.get(f'{self.base_url}/articles/')
            return response.json() if response.status_code == 200 else None

        def get_article_details(self, article_id):
            """Get detailed information about a specific article"""
            response = self.session.get(f'{self.base_url}/articles/{article_id}/')
            return response.json() if response.status_code == 200 else None

        def get_user_feed(self):
            """Get combined feed of articles and newsletters"""
            response = self.session.get(f'{self.base_url}/feed/')
            return response.json() if response.status_code == 200 else None

    # Usage example
    client = NewsAPIClient()
    
    # Authenticate
    if client.authenticate('reader1', 'testpass123'):
        print("Authentication successful!")
        
        # Get articles
        articles = client.get_articles()
        print(f"Found {len(articles)} articles")
        
        # Get detailed article info
        if articles:
            article_details = client.get_article_details(articles[0]['id'])
            print(f"Article: {article_details['title']}")
        
        # Get combined feed
        feed = client.get_user_feed()
        print(f"Feed contains {feed['total_articles']} articles and {feed['total_newsletters']} newsletters")
    else:
        print("Authentication failed!")

JavaScript Example
------------------

.. code-block:: javascript

    class NewsAPIClient {
        constructor(baseUrl = 'http://localhost:8000/api') {
            this.baseUrl = baseUrl;
            this.token = null;
        }

        async authenticate(username, password) {
            try {
                const response = await fetch(`${this.baseUrl}/auth/token/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });

                if (response.ok) {
                    const data = await response.json();
                    this.token = data.token;
                    return true;
                }
                return false;
            } catch (error) {
                console.error('Authentication error:', error);
                return false;
            }
        }

        async apiRequest(endpoint, options = {}) {
            const url = `${this.baseUrl}${endpoint}`;
            const headers = {
                'Content-Type': 'application/json',
                ...options.headers
            };

            if (this.token) {
                headers.Authorization = `Token ${this.token}`;
            }

            try {
                const response = await fetch(url, {
                    ...options,
                    headers
                });

                if (response.ok) {
                    return await response.json();
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            } catch (error) {
                console.error('API request error:', error);
                throw error;
            }
        }

        async getArticles() {
            return await this.apiRequest('/articles/');
        }

        async getArticleDetails(articleId) {
            return await this.apiRequest(`/articles/${articleId}/`);
        }

        async getUserFeed() {
            return await this.apiRequest('/feed/');
        }

        async getSubscriptions() {
            return await this.apiRequest('/subscriptions/');
        }

        async subscribeToPublisher(publisherId) {
            return await this.apiRequest('/subscriptions/', {
                method: 'POST',
                body: JSON.stringify({ publisher_id: publisherId })
            });
        }

        async followJournalist(journalistId) {
            return await this.apiRequest('/subscriptions/', {
                method: 'POST',
                body: JSON.stringify({ journalist_id: journalistId })
            });
        }
    }

    // Usage example
    async function main() {
        const client = new NewsAPIClient();

        // Authenticate
        if (await client.authenticate('reader1', 'testpass123')) {
            console.log('Authentication successful!');

            // Get articles
            const articles = await client.getArticles();
            console.log(`Found ${articles.length} articles`);

            // Get user feed
            const feed = await client.getUserFeed();
            console.log(`Feed: ${feed.total_articles} articles, ${feed.total_newsletters} newsletters`);

            // Get current subscriptions
            const subscriptions = await client.getSubscriptions();
            console.log('Current subscriptions:', subscriptions);
        } else {
            console.log('Authentication failed!');
        }
    }

    main().catch(console.error);

Subscription Management Examples
===============================

Managing Publisher Subscriptions
--------------------------------

.. code-block:: bash

    # Get current subscriptions
    curl -H "Authorization: Token your_token_here" \
         http://localhost:8000/api/subscriptions/

    # Subscribe to a publisher
    curl -X POST \
         -H "Authorization: Token your_token_here" \
         -H "Content-Type: application/json" \
         -d '{"publisher_id": 1}' \
         http://localhost:8000/api/subscriptions/

    # Unsubscribe from a publisher
    curl -X DELETE \
         -H "Authorization: Token your_token_here" \
         -H "Content-Type: application/json" \
         -d '{"publisher_id": 1}' \
         http://localhost:8000/api/subscriptions/

Following Journalists
--------------------

.. code-block:: bash

    # Follow a journalist
    curl -X POST \
         -H "Authorization: Token your_token_here" \
         -H "Content-Type: application/json" \
         -d '{"journalist_id": 2}' \
         http://localhost:8000/api/subscriptions/

    # Unfollow a journalist
    curl -X DELETE \
         -H "Authorization: Token your_token_here" \
         -H "Content-Type: application/json" \
         -d '{"journalist_id": 2}' \
         http://localhost:8000/api/subscriptions/

Content Discovery Examples
==========================

Finding Publishers and Journalists
----------------------------------

.. code-block:: python

    # Get all publishers
    publishers = client.session.get(f'{BASE_URL}/publishers/').json()
    print("Available publishers:")
    for publisher in publishers:
        print(f"- {publisher['name']} (ID: {publisher['id']})")

    # Get all journalists
    journalists = client.session.get(f'{BASE_URL}/journalists/').json()
    print("\nAvailable journalists:")
    for journalist in journalists:
        name = f"{journalist['first_name']} {journalist['last_name']}"
        print(f"- {name} (@{journalist['username']}, ID: {journalist['id']})")

Building a News Reader Application
=================================

Here's a complete example of building a simple news reader:

.. code-block:: python

    import requests
    from datetime import datetime

    class SimpleNewsReader:
        def __init__(self):
            self.client = NewsAPIClient()
            self.authenticated = False

        def login(self, username, password):
            """Login to the news application"""
            if self.client.authenticate(username, password):
                self.authenticated = True
                print(f"✅ Logged in as {username}")
                return True
            else:
                print("❌ Login failed")
                return False

        def show_feed(self):
            """Display the user's personalized feed"""
            if not self.authenticated:
                print("Please login first")
                return

            feed = self.client.get_user_feed()
            if not feed:
                print("Failed to fetch feed")
                return

            print(f"\n📰 Your News Feed")
            print(f"{'='*50}")

            # Show articles
            if feed['articles']:
                print(f"\n📄 Articles ({feed['total_articles']} total):")
                for article in feed['articles'][:5]:  # Show first 5
                    print(f"• {article['title']}")
                    print(f"  By: {article['author_username']}")
                    if article['publisher_name']:
                        print(f"  Publisher: {article['publisher_name']}")
                    print(f"  Date: {article['created_at_formatted']}")
                    print(f"  Preview: {article['body_preview'][:100]}...")
                    print()

            # Show newsletters
            if feed['newsletters']:
                print(f"\n📧 Newsletters ({feed['total_newsletters']} total):")
                for newsletter in feed['newsletters'][:5]:  # Show first 5
                    print(f"• {newsletter['subject']}")
                    print(f"  By: {newsletter['author_username']}")
                    if newsletter['publisher_name']:
                        print(f"  Publisher: {newsletter['publisher_name']}")
                    print(f"  Date: {newsletter['created_at_formatted']}")
                    print(f"  Preview: {newsletter['content_preview'][:100]}...")
                    print()

        def show_subscriptions(self):
            """Display current subscriptions"""
            if not self.authenticated:
                print("Please login first")
                return

            subs = self.client.session.get(f'{self.client.base_url}/subscriptions/').json()
            
            print(f"\n👥 Your Subscriptions")
            print(f"{'='*30}")

            if subs['subscribed_publishers']:
                print("\n📰 Publishers:")
                for pub in subs['subscribed_publishers']:
                    print(f"• {pub['name']}")

            if subs['followed_journalists']:
                print("\n✍️ Journalists:")
                for journalist in subs['followed_journalists']:
                    name = f"{journalist['first_name']} {journalist['last_name']}"
                    print(f"• {name} (@{journalist['username']})")

        def discover_content(self):
            """Help users discover new publishers and journalists"""
            if not self.authenticated:
                print("Please login first")
                return

            print(f"\n🔍 Discover New Content")
            print(f"{'='*30}")

            # Show available publishers
            publishers = self.client.session.get(f'{self.client.base_url}/publishers/').json()
            print("\n📰 Available Publishers:")
            for pub in publishers[:10]:  # Show first 10
                print(f"• {pub['name']} (ID: {pub['id']})")

            # Show available journalists
            journalists = self.client.session.get(f'{self.client.base_url}/journalists/').json()
            print("\n✍️ Available Journalists:")
            for journalist in journalists[:10]:  # Show first 10
                name = f"{journalist['first_name']} {journalist['last_name']}"
                print(f"• {name} (@{journalist['username']}, ID: {journalist['id']})")

    # Usage example
    def main():
        reader = SimpleNewsReader()
        
        # Login
        if reader.login('reader1', 'testpass123'):
            # Show current subscriptions
            reader.show_subscriptions()
            
            # Show personalized feed
            reader.show_feed()
            
            # Discover new content
            reader.discover_content()

    if __name__ == "__main__":
        main()

Error Handling Examples
======================

Robust Error Handling
---------------------

.. code-block:: python

    import requests
    from requests.exceptions import RequestException, ConnectionError, Timeout

    def safe_api_call(url, headers=None, timeout=10):
        """Make a safe API call with proper error handling"""
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            elif response.status_code == 401:
                return {'success': False, 'error': 'Authentication required'}
            elif response.status_code == 403:
                return {'success': False, 'error': 'Permission denied'}
            elif response.status_code == 404:
                return {'success': False, 'error': 'Resource not found'}
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except ConnectionError:
            return {'success': False, 'error': 'Connection failed'}
        except Timeout:
            return {'success': False, 'error': 'Request timeout'}
        except RequestException as e:
            return {'success': False, 'error': f'Request error: {str(e)}'}

    # Usage
    result = safe_api_call('http://localhost:8000/api/articles/', 
                          headers={'Authorization': 'Token your_token'})
    
    if result['success']:
        articles = result['data']
        print(f"Found {len(articles)} articles")
    else:
        print(f"Error: {result['error']}")

Testing API Endpoints
=====================

Using pytest for API Testing
----------------------------

.. code-block:: python

    import pytest
    import requests

    class TestNewsAPI:
        BASE_URL = 'http://localhost:8000/api'
        
        @pytest.fixture
        def authenticated_client(self):
            """Create an authenticated API client"""
            client = requests.Session()
            
            # Get token
            response = client.post(f'{self.BASE_URL}/auth/token/', {
                'username': 'reader1',
                'password': 'testpass123'
            })
            
            if response.status_code == 200:
                token = response.json()['token']
                client.headers.update({'Authorization': f'Token {token}'})
            
            return client

        def test_get_articles(self, authenticated_client):
            """Test getting articles"""
            response = authenticated_client.get(f'{self.BASE_URL}/articles/')
            assert response.status_code == 200
            
            articles = response.json()
            assert isinstance(articles, list)
            
            if articles:
                article = articles[0]
                assert 'id' in article
                assert 'title' in article
                assert 'author_username' in article

        def test_get_article_details(self, authenticated_client):
            """Test getting article details"""
            # First get list of articles
            response = authenticated_client.get(f'{self.BASE_URL}/articles/')
            articles = response.json()
            
            if articles:
                article_id = articles[0]['id']
                
                # Get detailed article info
                response = authenticated_client.get(f'{self.BASE_URL}/articles/{article_id}/')
                assert response.status_code == 200
                
                article = response.json()
                assert article['id'] == article_id
                assert 'body' in article  # Full content should be present

        def test_unauthorized_access(self):
            """Test that unauthorized requests are rejected"""
            response = requests.get(f'{self.BASE_URL}/articles/')
            assert response.status_code == 401

Run tests with: ``pytest test_api_examples.py -v``

Performance Considerations
=========================

Efficient API Usage
-------------------

1. **Reuse connections**: Use session objects to reuse HTTP connections
2. **Cache tokens**: Store authentication tokens and reuse them
3. **Batch requests**: When possible, minimize the number of API calls
4. **Handle rate limits**: Implement exponential backoff for failed requests

.. code-block:: python

    import time
    import random

    def api_call_with_retry(func, max_retries=3, backoff_factor=1):
        """Make API call with exponential backoff retry"""
        for attempt in range(max_retries):
            try:
                result = func()
                if result.get('success'):
                    return result
                
                if attempt < max_retries - 1:  # Don't sleep on last attempt
                    sleep_time = backoff_factor * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(sleep_time)
                    
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise e
                    
        return {'success': False, 'error': 'Max retries exceeded'}

This completes the API usage examples. These examples demonstrate real-world usage patterns and best practices for integrating with the Django News Application API.
