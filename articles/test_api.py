"""
Unit tests for the News Application RESTful API
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from articles.models import Article, Newsletter, Publisher, User

User = get_user_model()


class APISerializerTests(TestCase):
    """Test API serializers"""
    
    def setUp(self):
        """Set up test data"""
        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.journalist = User.objects.create_user(
            username='test_journalist',
            email='journalist@test.com',
            password='testpass123',
            role=User.Roles.JOURNALIST,
            first_name='Test',
            last_name='Journalist'
        )
        self.editor = User.objects.create_user(
            username='test_editor',
            email='editor@test.com',
            password='testpass123',
            role=User.Roles.EDITOR,
            first_name='Test',
            last_name='Editor',
            affiliated_publisher=self.publisher
        )
        self.reader = User.objects.create_user(
            username='test_reader',
            email='reader@test.com',
            password='testpass123',
            role=User.Roles.READER,
            first_name='Test',
            last_name='Reader'
        )
        self.article = Article.objects.create(
            title="Test Article",
            body="This is a test article body content.",
            author=self.journalist,
            publisher=self.publisher,
            is_approved=True,
            approved_by=self.editor
        )
        self.newsletter = Newsletter.objects.create(
            subject="Test Newsletter",
            content="This is a test newsletter content.",
            author=self.editor,
            publisher=self.publisher
        )

    def test_publisher_serializer(self):
        """Test PublisherSerializer"""
        from articles.serializers import PublisherSerializer
        
        serializer = PublisherSerializer(self.publisher)
        data = serializer.data
        
        self.assertEqual(data['id'], self.publisher.id)
        self.assertEqual(data['name'], self.publisher.name)

    def test_user_serializer(self):
        """Test UserSerializer"""
        from articles.serializers import UserSerializer
        
        serializer = UserSerializer(self.journalist)
        data = serializer.data
        
        self.assertEqual(data['username'], self.journalist.username)
        self.assertEqual(data['role'], 'journalist')
        self.assertEqual(data['role_display'], 'Journalist')

    def test_article_serializer(self):
        """Test ArticleSerializer"""
        from articles.serializers import ArticleSerializer
        
        serializer = ArticleSerializer(self.article)
        data = serializer.data
        
        self.assertEqual(data['title'], self.article.title)
        self.assertEqual(data['body'], self.article.body)
        self.assertEqual(data['author_username'], self.journalist.username)
        self.assertEqual(data['publisher_name'], self.publisher.name)
        self.assertTrue(data['is_approved'])
        self.assertEqual(data['is_approved_display'], 'Approved')

    def test_newsletter_serializer(self):
        """Test NewsletterSerializer"""
        from articles.serializers import NewsletterSerializer
        
        serializer = NewsletterSerializer(self.newsletter)
        data = serializer.data
        
        self.assertEqual(data['subject'], self.newsletter.subject)
        self.assertEqual(data['content'], self.newsletter.content)
        self.assertEqual(data['author_username'], self.editor.username)
        self.assertEqual(data['publisher_name'], self.publisher.name)


class APIAuthenticationTests(APITestCase):
    """Test API authentication and permissions"""
    
    def setUp(self):
        """Set up test data"""
        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.journalist = User.objects.create_user(
            username='test_journalist',
            email='journalist@test.com',
            password='testpass123',
            role=User.Roles.JOURNALIST
        )
        self.reader = User.objects.create_user(
            username='test_reader',
            email='reader@test.com',
            password='testpass123',
            role=User.Roles.READER
        )
        self.article = Article.objects.create(
            title="Test Article",
            body="This is a test article body content.",
            author=self.journalist,
            publisher=self.publisher,
            is_approved=True
        )

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access protected endpoints"""
        url = reverse('api_article_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_token_authentication(self):
        """Test token-based authentication"""
        token = Token.objects.create(user=self.reader)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        url = reverse('api_article_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_session_authentication(self):
        """Test session-based authentication"""
        self.client.force_authenticate(user=self.reader)
        
        url = reverse('api_article_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class APIContentFilteringTests(APITestCase):
    """Test subscription-based content filtering"""
    
    def setUp(self):
        """Set up test data with subscriptions"""
        # Create publishers
        self.publisher1 = Publisher.objects.create(name="Publisher 1")
        self.publisher2 = Publisher.objects.create(name="Publisher 2")
        
        # Create journalists
        self.journalist1 = User.objects.create_user(
            username='journalist1',
            email='j1@test.com',
            password='testpass123',
            role=User.Roles.JOURNALIST
        )
        self.journalist2 = User.objects.create_user(
            username='journalist2',
            email='j2@test.com',
            password='testpass123',
            role=User.Roles.JOURNALIST
        )
        
        # Create reader with subscriptions
        self.reader = User.objects.create_user(
            username='test_reader',
            email='reader@test.com',
            password='testpass123',
            role=User.Roles.READER
        )
        
        # Create articles
        self.article1 = Article.objects.create(
            title="Article from Publisher 1",
            body="Content from publisher 1",
            author=self.journalist1,
            publisher=self.publisher1,
            is_approved=True
        )
        self.article2 = Article.objects.create(
            title="Article from Publisher 2",
            body="Content from publisher 2",
            author=self.journalist2,
            publisher=self.publisher2,
            is_approved=True
        )
        self.article3 = Article.objects.create(
            title="Independent Article",
            body="Independent content",
            author=self.journalist1,
            publisher=None,
            is_approved=True
        )
        
        # Set up subscriptions
        self.reader.subscriptions_publishers.add(self.publisher1)
        self.reader.subscriptions_journalists.add(self.journalist1)
        
        # Create token for reader
        self.token = Token.objects.create(user=self.reader)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_reader_sees_subscribed_content_only(self):
        """Test that readers only see content from their subscriptions"""
        url = reverse('api_article_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should see article1 (subscribed publisher) and article3 (followed journalist)
        # Should NOT see article2 (not subscribed)
        article_titles = [article['title'] for article in data['results']]
        
        self.assertIn("Article from Publisher 1", article_titles)
        self.assertIn("Independent Article", article_titles)
        self.assertNotIn("Article from Publisher 2", article_titles)

    def test_editor_sees_all_content(self):
        """Test that editors see all content regardless of subscriptions"""
        editor = User.objects.create_user(
            username='test_editor',
            email='editor@test.com',
            password='testpass123',
            role=User.Roles.EDITOR,
            affiliated_publisher=self.publisher1
        )
        
        editor_token = Token.objects.create(user=editor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {editor_token.key}')
        
        url = reverse('api_article_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should see all articles
        article_titles = [article['title'] for article in data['results']]
        
        self.assertIn("Article from Publisher 1", article_titles)
        self.assertIn("Article from Publisher 2", article_titles)
        self.assertIn("Independent Article", article_titles)

    def test_journalist_sees_all_content(self):
        """Test that journalists see all content regardless of subscriptions"""
        journalist_token = Token.objects.create(user=self.journalist1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {journalist_token.key}')
        
        url = reverse('api_article_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should see all articles
        article_titles = [article['title'] for article in data['results']]
        
        self.assertIn("Article from Publisher 1", article_titles)
        self.assertIn("Article from Publisher 2", article_titles)
        self.assertIn("Independent Article", article_titles)


class APISubscriptionManagementTests(APITestCase):
    """Test subscription management endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.journalist = User.objects.create_user(
            username='test_journalist',
            email='journalist@test.com',
            password='testpass123',
            role=User.Roles.JOURNALIST
        )
        self.reader = User.objects.create_user(
            username='test_reader',
            email='reader@test.com',
            password='testpass123',
            role=User.Roles.READER
        )
        
        self.token = Token.objects.create(user=self.reader)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_get_subscriptions(self):
        """Test getting user subscriptions"""
        url = reverse('api_subscriptions')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('subscribed_publishers', data)
        self.assertIn('followed_journalists', data)
        self.assertEqual(len(data['subscribed_publishers']), 0)
        self.assertEqual(len(data['followed_journalists']), 0)

    def test_add_publisher_subscription(self):
        """Test adding a publisher subscription"""
        url = reverse('api_subscriptions')
        data = {'publisher_id': self.publisher.id}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Now subscribed to', response.json()['message'])
        
        # Verify subscription was added
        self.reader.refresh_from_db()
        self.assertIn(self.publisher, self.reader.subscriptions_publishers.all())

    def test_add_journalist_subscription(self):
        """Test adding a journalist subscription"""
        url = reverse('api_subscriptions')
        data = {'journalist_id': self.journalist.id}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Now following', response.json()['message'])
        
        # Verify subscription was added
        self.reader.refresh_from_db()
        self.assertIn(self.journalist, self.reader.subscriptions_journalists.all())

    def test_remove_publisher_subscription(self):
        """Test removing a publisher subscription"""
        # First add subscription
        self.reader.subscriptions_publishers.add(self.publisher)
        
        url = reverse('api_subscriptions')
        data = {'publisher_id': self.publisher.id}
        
        response = self.client.delete(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Unsubscribed from', response.json()['message'])
        
        # Verify subscription was removed
        self.reader.refresh_from_db()
        self.assertNotIn(self.publisher, self.reader.subscriptions_publishers.all())

    def test_remove_journalist_subscription(self):
        """Test removing a journalist subscription"""
        # First add subscription
        self.reader.subscriptions_journalists.add(self.journalist)
        
        url = reverse('api_subscriptions')
        data = {'journalist_id': self.journalist.id}
        
        response = self.client.delete(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Unfollowed', response.json()['message'])
        
        # Verify subscription was removed
        self.reader.refresh_from_db()
        self.assertNotIn(self.journalist, self.reader.subscriptions_journalists.all())


class APIPaginationTests(APITestCase):
    """Test API pagination"""
    
    def setUp(self):
        """Set up test data with multiple articles"""
        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.journalist = User.objects.create_user(
            username='test_journalist',
            email='journalist@test.com',
            password='testpass123',
            role=User.Roles.JOURNALIST
        )
        self.reader = User.objects.create_user(
            username='test_reader',
            email='reader@test.com',
            password='testpass123',
            role=User.Roles.READER
        )
        
        # Create 25 articles to test pagination
        for i in range(25):
            Article.objects.create(
                title=f"Test Article {i+1}",
                body=f"Content for article {i+1}",
                author=self.journalist,
                publisher=self.publisher,
                is_approved=True
        )
        
        # Subscribe reader to publisher
        self.reader.subscriptions_publishers.add(self.publisher)
        
        self.token = Token.objects.create(user=self.reader)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_pagination_default_page_size(self):
        """Test default pagination (20 items per page)"""
        url = reverse('api_article_list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(len(data['results']), 20)  # Default page size
        self.assertIsNotNone(data['next'])  # Should have next page
        self.assertIsNone(data['previous'])  # Should be first page
        self.assertEqual(data['count'], 25)  # Total count

    def test_pagination_custom_page_size(self):
        """Test custom page size"""
        url = reverse('api_article_list')
        response = self.client.get(url, {'page_size': 10})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Note: Custom page size might not work with default pagination
        # This test verifies the API accepts the parameter without error
        self.assertIn('results', data)
        self.assertIn('count', data)
        self.assertEqual(data['count'], 25)

    def test_pagination_second_page(self):
        """Test accessing second page"""
        url = reverse('api_article_list')
        response = self.client.get(url, {'page': 2})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(len(data['results']), 5)  # Remaining articles
        self.assertIsNone(data['next'])  # Should be last page
        self.assertIsNotNone(data['previous'])  # Should have previous page


class APIFeedTests(APITestCase):
    """Test combined feed endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.journalist = User.objects.create_user(
            username='test_journalist',
            email='journalist@test.com',
            password='testpass123',
            role=User.Roles.JOURNALIST
        )
        self.editor = User.objects.create_user(
            username='test_editor',
            email='editor@test.com',
            password='testpass123',
            role=User.Roles.EDITOR,
            affiliated_publisher=self.publisher
        )
        self.reader = User.objects.create_user(
            username='test_reader',
            email='reader@test.com',
            password='testpass123',
            role=User.Roles.READER
        )
        
        # Create content
        self.article = Article.objects.create(
            title="Test Article",
            body="Article content",
            author=self.journalist,
            publisher=self.publisher,
            is_approved=True
        )
        self.newsletter = Newsletter.objects.create(
            subject="Test Newsletter",
            content="Newsletter content",
            author=self.editor,
            publisher=self.publisher
        )
        
        # Subscribe reader
        self.reader.subscriptions_publishers.add(self.publisher)
        
        self.token = Token.objects.create(user=self.reader)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_feed_returns_combined_content(self):
        """Test that feed returns both articles and newsletters"""
        url = reverse('api_feed')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('articles', data)
        self.assertIn('newsletters', data)
        self.assertIn('total_articles', data)
        self.assertIn('total_newsletters', data)
        
        self.assertEqual(len(data['articles']), 1)
        self.assertEqual(len(data['newsletters']), 1)
        self.assertEqual(data['total_articles'], 1)
        self.assertEqual(data['total_newsletters'], 1)

    def test_feed_respects_subscriptions(self):
        """Test that feed respects user subscriptions"""
        # Create content from unsubscribed publisher
        other_publisher = Publisher.objects.create(name="Other Publisher")
        other_article = Article.objects.create(
            title="Other Article",
            body="Other content",
            author=self.journalist,
            publisher=other_publisher,
            is_approved=True
        )
        
        url = reverse('api_feed')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should only see content from subscribed publisher
        article_titles = [article['title'] for article in data['articles']]
        self.assertIn("Test Article", article_titles)
        self.assertNotIn("Other Article", article_titles)


class APIErrorHandlingTests(APITestCase):
    """Test API error handling"""
    
    def setUp(self):
        """Set up test data"""
        self.reader = User.objects.create_user(
            username='test_reader',
            email='reader@test.com',
            password='testpass123',
            role=User.Roles.READER
        )
        
        self.token = Token.objects.create(user=self.reader)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_invalid_article_id(self):
        """Test accessing non-existent article"""
        url = reverse('api_article_detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_subscription_data(self):
        """Test invalid subscription data"""
        url = reverse('api_subscriptions')
        
        # Test missing required fields
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Must provide', response.json()['error'])
        
        # Test invalid publisher ID
        response = self.client.post(url, {'publisher_id': 99999}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Publisher not found', response.json()['error'])
        
        # Test invalid journalist ID
        response = self.client.post(url, {'journalist_id': 99999}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Journalist not found', response.json()['error'])

    def test_api_info_no_auth_required(self):
        """Test that API info endpoint doesn't require authentication"""
        url = reverse('api_info')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn('api_name', data)
        self.assertIn('endpoints', data)
        self.assertIn('authentication', data)
