from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import json

from .models import Article, Newsletter, Publisher
from .forms import UserRegistrationForm, ArticleForm, NewsletterForm


User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for the custom User model"""
    
    def setUp(self):
        self.publisher = Publisher.objects.create(
            name="Test Publisher"
        )
    
    def test_create_reader_user(self):
        """Test creating a reader user"""
        user = User.objects.create_user(
            username="reader1",
            email="reader@test.com",
            password="testpass123",
            role=User.Roles.READER
        )
        self.assertEqual(user.username, "reader1")
        self.assertEqual(user.role, User.Roles.READER)
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_journalist_user(self):
        """Test creating a journalist user"""
        user = User.objects.create_user(
            username="journalist1",
            email="journalist@test.com",
            password="testpass123",
            role=User.Roles.JOURNALIST
        )
        self.assertEqual(user.role, User.Roles.JOURNALIST)
        self.assertFalse(user.is_staff)
    
    def test_create_editor_user(self):
        """Test creating an editor user with publisher affiliation"""
        user = User.objects.create_user(
            username="editor1",
            email="editor@test.com",
            password="testpass123",
            role=User.Roles.EDITOR,
            affiliated_publisher=self.publisher
        )
        self.assertEqual(user.role, User.Roles.EDITOR)
        self.assertEqual(user.affiliated_publisher, self.publisher)
        self.assertFalse(user.is_staff)  # is_staff is not automatically set
    
    def test_user_str_method(self):
        """Test the string representation of User"""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            role=User.Roles.READER
        )
        self.assertEqual(str(user), "testuser")  # Uses AbstractUser's default __str__
    
    def test_role_validation(self):
        """Test that role validation works correctly"""
        user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            role=User.Roles.READER
        )
        self.assertEqual(user.role, User.Roles.READER)
        
        # Test that editor can have affiliated publisher
        user.role = User.Roles.EDITOR
        user.affiliated_publisher = self.publisher
        user.save()  # Should not raise an error
        
        self.assertEqual(user.role, User.Roles.EDITOR)
        self.assertEqual(user.affiliated_publisher, self.publisher)


class ArticleModelTest(TestCase):
    """Test cases for the Article model"""
    
    def setUp(self):
        self.publisher = Publisher.objects.create(
            name="Test Publisher"
        )
        self.journalist = User.objects.create_user(
            username="journalist1",
            email="journalist@test.com",
            role=User.Roles.JOURNALIST
        )
        self.editor = User.objects.create_user(
            username="editor1",
            email="editor@test.com",
            role=User.Roles.EDITOR,
            affiliated_publisher=self.publisher,
        )
    
    def test_create_article(self):
        """Test creating an article"""
        article = Article.objects.create(
            title="Test Article",
            body="This is a test article body.",
            author=self.journalist,
            publisher=self.publisher
        )
        self.assertEqual(article.title, "Test Article")
        self.assertEqual(article.author, self.journalist)
        self.assertEqual(article.publisher, self.publisher)
        self.assertFalse(article.is_approved)
        self.assertIsNotNone(article.created_at)
    
    def test_article_str_method(self):
        """Test the string representation of Article"""
        article = Article.objects.create(
            title="Test Article",
            body="Test body",
            author=self.journalist,
            publisher=self.publisher
        )
        self.assertEqual(str(article), "Test Article")
    
    def test_article_approval(self):
        """Test article approval functionality"""
        article = Article.objects.create(
            title="Test Article",
            body="Test body",
            author=self.journalist,
            publisher=self.publisher
        )
        self.assertFalse(article.is_approved)
        
        article.is_approved = True
        article.approved_by = self.editor
        article.save()
        
        self.assertTrue(article.is_approved)
        self.assertEqual(article.approved_by, self.editor)
    
    def test_article_ordering(self):
        """Test that articles are ordered by creation date (newest first)"""
        article1 = Article.objects.create(
            title="First Article",
            body="First body",
            author=self.journalist,
            publisher=self.publisher
        )
        article2 = Article.objects.create(
            title="Second Article",
            body="Second body",
            author=self.journalist,
            publisher=self.publisher
        )
        
        articles = Article.objects.all()
        self.assertEqual(articles[0], article2)  # Newest first
        self.assertEqual(articles[1], article1)


class NewsletterModelTest(TestCase):
    """Test cases for the Newsletter model"""
    
    def setUp(self):
        self.publisher = Publisher.objects.create(
            name="Test Publisher"
        )
        self.journalist = User.objects.create_user(
            username="journalist1",
            email="journalist@test.com",
            role=User.Roles.JOURNALIST
        )
    
    def test_create_newsletter(self):
        """Test creating a newsletter"""
        newsletter = Newsletter.objects.create(
            subject="Test Newsletter",
            content="This is newsletter content.",
            author=self.journalist,
            publisher=self.publisher
        )
        self.assertEqual(newsletter.subject, "Test Newsletter")
        self.assertEqual(newsletter.author, self.journalist)
        self.assertEqual(newsletter.publisher, self.publisher)
        self.assertIsNotNone(newsletter.created_at)
    
    def test_newsletter_str_method(self):
        """Test the string representation of Newsletter"""
        newsletter = Newsletter.objects.create(
            subject="Test Newsletter",
            content="Test content",
            author=self.journalist,
            publisher=self.publisher
        )
        self.assertEqual(str(newsletter), "Test Newsletter")


class PublisherModelTest(TestCase):
    """Test cases for the Publisher model"""
    
    def test_create_publisher(self):
        """Test creating a publisher"""
        publisher = Publisher.objects.create(
            name="Test Publisher"
        )
        self.assertEqual(publisher.name, "Test Publisher")
        self.assertIsNotNone(publisher.pk)  # Check that it was saved successfully
    
    def test_publisher_str_method(self):
        """Test the string representation of Publisher"""
        publisher = Publisher.objects.create(
            name="Test Publisher"
        )
        self.assertEqual(str(publisher), "Test Publisher")
    
    def test_publisher_unique_name(self):
        """Test that publisher names must be unique"""
        Publisher.objects.create(name="Unique Publisher")
        with self.assertRaises(IntegrityError):
            Publisher.objects.create(name="Unique Publisher")


class UserRegistrationFormTest(TestCase):
    """Test cases for the UserRegistrationForm"""
    
    def setUp(self):
        self.publisher = Publisher.objects.create(
            name="Test Publisher"
        )
    
    def test_valid_reader_registration(self):
        """Test valid reader registration form"""
        form_data = {
            'username': 'newreader',
            'email': 'reader@test.com',
            'role': User.Roles.READER,
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_valid_editor_registration_with_publisher(self):
        """Test valid editor registration with publisher affiliation"""
        form_data = {
            'username': 'neweditor',
            'email': 'editor@test.com',
            'role': User.Roles.EDITOR,
            'affiliated_publisher': self.publisher.id,
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_password_mismatch(self):
        """Test form validation with password mismatch"""
        form_data = {
            'username': 'testuser',
            'email': 'test@test.com',
            'role': User.Roles.READER,
            'password1': 'complexpass123',
            'password2': 'differentpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_duplicate_username(self):
        """Test form validation with duplicate username"""
        User.objects.create_user(
            username='existinguser',
            email='existing@test.com',
            role=User.Roles.READER
        )
        
        form_data = {
            'username': 'existinguser',
            'email': 'new@test.com',
            'role': User.Roles.READER,
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


class ArticleFormTest(TestCase):
    """Test cases for the ArticleForm"""
    
    def test_valid_article_form(self):
        """Test valid article form"""
        form_data = {
            'title': 'Test Article Title',
            'body': 'This is the article body content.'
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_empty_title(self):
        """Test form validation with empty title"""
        form_data = {
            'title': '',
            'body': 'This is the article body content.'
        }
        form = ArticleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_invalid_empty_body(self):
        """Test form validation with empty body"""
        form_data = {
            'title': 'Test Article Title',
            'body': ''
        }
        form = ArticleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('body', form.errors)


class NewsletterFormTest(TestCase):
    """Test cases for the NewsletterForm"""
    
    def test_valid_newsletter_form(self):
        """Test valid newsletter form"""
        form_data = {
            'subject': 'Test Newsletter Subject',
            'content': 'This is the newsletter content.'
        }
        form = NewsletterForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_empty_subject(self):
        """Test form validation with empty subject"""
        form_data = {
            'subject': '',
            'content': 'This is the newsletter content.'
        }
        form = NewsletterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('subject', form.errors)


class AuthenticationViewTest(TestCase):
    """Test cases for authentication views"""
    
    def setUp(self):
        self.client = Client()
        self.publisher = Publisher.objects.create(
            name="Test Publisher"
        )
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
            affiliated_publisher=self.publisher,
        )
    
    def test_login_view_get(self):
        """Test GET request to login view"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_login_view_post_valid(self):
        """Test POST request to login view with valid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'reader1',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
    
    def test_login_view_post_invalid(self):
        """Test POST request to login view with invalid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'reader1',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')
    
    def test_register_view_get(self):
        """Test GET request to register view"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')
    
    def test_register_view_post_valid(self):
        """Test POST request to register view with valid data"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'role': User.Roles.READER,
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_logout_view(self):
        """Test logout functionality"""
        self.client.login(username='reader1', password='testpass123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout


class ArticleViewTest(TestCase):
    """Test cases for article-related views"""
    
    def setUp(self):
        self.client = Client()
        self.publisher = Publisher.objects.create(
            name="Test Publisher"
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
            affiliated_publisher=self.publisher,
        )
        self.reader = User.objects.create_user(
            username='reader1',
            email='reader@test.com',
            password='testpass123',
            role=User.Roles.READER
        )
        self.article = Article.objects.create(
            title="Test Article",
            body="Test content",
            author=self.journalist,
            publisher=self.publisher
        )
    
    def test_article_create_view_requires_login(self):
        """Test that article creation requires login"""
        response = self.client.get(reverse('article_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_article_create_view_journalist_access(self):
        """Test that journalists can access article creation"""
        self.client.login(username='journalist1', password='testpass123')
        response = self.client.get(reverse('article_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_article_create_view_reader_forbidden(self):
        """Test that readers cannot access article creation"""
        self.client.login(username='reader1', password='testpass123')
        response = self.client.get(reverse('article_create'))
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_article_create_post(self):
        """Test creating an article via POST"""
        self.client.login(username='journalist1', password='testpass123')
        response = self.client.post(reverse('article_create'), {
            'title': 'New Test Article',
            'body': 'This is a new test article.'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Article.objects.filter(title='New Test Article').exists())
    
    def test_article_approval_editor_only(self):
        """Test that only editors can approve articles"""
        # Reader cannot approve
        self.client.login(username='reader1', password='testpass123')
        response = self.client.get(reverse('article_approve', kwargs={'pk': self.article.pk}))
        self.assertEqual(response.status_code, 403)
        
        # Editor can approve
        self.client.login(username='editor1', password='testpass123')
        response = self.client.get(reverse('article_approve', kwargs={'pk': self.article.pk}))
        self.assertEqual(response.status_code, 302)
        
        self.article.refresh_from_db()
        self.assertTrue(self.article.is_approved)
        self.assertEqual(self.article.approved_by, self.editor)


class NewsletterViewTest(TestCase):
    """Test cases for newsletter-related views"""
    
    def setUp(self):
        self.client = Client()
        self.publisher = Publisher.objects.create(
            name="Test Publisher"
        )
        self.journalist = User.objects.create_user(
            username='journalist1',
            email='journalist@test.com',
            password='testpass123',
            role=User.Roles.JOURNALIST
        )
        self.reader = User.objects.create_user(
            username='reader1',
            email='reader@test.com',
            password='testpass123',
            role=User.Roles.READER
        )
    
    def test_newsletter_create_view_requires_login(self):
        """Test that newsletter creation requires login"""
        response = self.client.get(reverse('newsletter_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_newsletter_create_view_journalist_access(self):
        """Test that journalists can access newsletter creation"""
        self.client.login(username='journalist1', password='testpass123')
        response = self.client.get(reverse('newsletter_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_newsletter_create_post(self):
        """Test creating a newsletter via POST"""
        self.client.login(username='journalist1', password='testpass123')
        response = self.client.post(reverse('newsletter_create'), {
            'subject': 'Test Newsletter',
            'content': 'This is a test newsletter content.'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertTrue(Newsletter.objects.filter(subject='Test Newsletter').exists())


class TwitterIntegrationTest(TestCase):
    """Test cases for Twitter integration"""
    
    def setUp(self):
        self.client = Client()
        self.publisher = Publisher.objects.create(
            name="Test Publisher"
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
            affiliated_publisher=self.publisher,
        )
    
    def test_twitter_connect_requires_login(self):
        """Test that Twitter connection requires login"""
        response = self.client.get(reverse('twitter_connect'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    @patch('articles.integrations.twitter_views.OAuth2Session')
    def test_twitter_connect_journalist_access(self, mock_oauth):
        """Test that journalists can access Twitter connection"""
        mock_oauth.return_value.authorization_url.return_value = ('http://test.com', 'state')
        self.client.login(username='journalist1', password='testpass123')
        response = self.client.get(reverse('twitter_connect'))
        self.assertEqual(response.status_code, 302)  # Redirect to Twitter
    
    @patch('articles.integrations.twitter_views.requests.post')
    def test_twitter_post_on_approval(self, mock_post):
        """Test that articles are posted to Twitter when approved"""
        # Mock successful Twitter API response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'data': {'id': '12345', 'text': 'Test tweet'}
        }
        mock_post.return_value = mock_response
        
        # Create and approve an article
        article = Article.objects.create(
            title="Test Article for Twitter",
            body="Test content",
            author=self.journalist,
            publisher=self.publisher
        )
        
        # Mock Twitter token file existence
        with patch('articles.functions.tweet.os.path.exists', return_value=True):
            with patch('articles.integrations.twitter_views.is_twitter_connected', return_value=True):
                self.client.login(username='editor1', password='testpass123')
                response = self.client.get(reverse('article_approve', kwargs={'pk': article.pk}))
        
        # Check that Twitter API was called
        self.assertTrue(mock_post.called)


class EmailNotificationTest(TestCase):
    """Test cases for email notifications"""
    
    def setUp(self):
        self.publisher = Publisher.objects.create(
            name="Test Publisher"
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
            affiliated_publisher=self.publisher,
        )
        self.client = Client()
    
    @patch('articles.views.send_mail')
    def test_email_sent_on_article_approval(self, mock_send_mail):
        """Test that email is sent when article is approved"""
        mock_send_mail.return_value = True
        
        article = Article.objects.create(
            title="Test Article",
            body="Test content",
            author=self.journalist,
            publisher=self.publisher
        )
        
        self.client.login(username='editor1', password='testpass123')
        response = self.client.get(reverse('article_approve', kwargs={'pk': article.pk}))
        
        # Check that email was sent
        self.assertTrue(mock_send_mail.called)
        
        # Check email content
        call_args = mock_send_mail.call_args
        self.assertIn('approved', call_args[0][0])  # Subject contains 'approved'
        self.assertEqual(call_args[1]['recipient_list'], [self.journalist.email])
    
    @patch('articles.views.send_mail')
    def test_email_sent_on_article_rejection(self, mock_send_mail):
        """Test that email is sent when article is rejected"""
        mock_send_mail.return_value = True
        
        article = Article.objects.create(
            title="Test Article",
            body="Test content",
            author=self.journalist,
            publisher=self.publisher,
            is_approved=True  # Start as approved
        )
        
        self.client.login(username='editor1', password='testpass123')
        response = self.client.get(reverse('article_unapprove', kwargs={'pk': article.pk}))
        
        # Check that email was sent
        self.assertTrue(mock_send_mail.called)
        
        # Check email content
        call_args = mock_send_mail.call_args
        self.assertIn('rejected', call_args[0][0])  # Subject contains 'rejected'


class SubscriptionTest(TestCase):
    """Test cases for subscription functionality"""
    
    def setUp(self):
        self.client = Client()
        self.publisher = Publisher.objects.create(
            name="Test Publisher"
        )
        self.journalist = User.objects.create_user(
            username='journalist1',
            email='journalist@test.com',
            password='testpass123',
            role=User.Roles.JOURNALIST
        )
        self.reader = User.objects.create_user(
            username='reader1',
            email='reader@test.com',
            password='testpass123',
            role=User.Roles.READER
        )
    
    def test_subscription_view_requires_login(self):
        """Test that subscription view requires login"""
        response = self.client.get(reverse('subscriptions'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_subscription_view_reader_access(self):
        """Test that readers can access subscription view"""
        self.client.login(username='reader1', password='testpass123')
        response = self.client.get(reverse('subscriptions'))
        self.assertEqual(response.status_code, 200)
    
    def test_subscribe_to_publisher(self):
        """Test subscribing to a publisher"""
        self.client.login(username='reader1', password='testpass123')
        response = self.client.post(reverse('subscriptions'), {
            'action': 'subscribe_publisher',
            'publisher_id': self.publisher.id
        })
        self.assertEqual(response.status_code, 302)  # Redirect after subscription
        self.assertTrue(self.reader.subscribed_publishers.filter(id=self.publisher.id).exists())
    
    def test_subscribe_to_journalist(self):
        """Test subscribing to a journalist"""
        self.client.login(username='reader1', password='testpass123')
        response = self.client.post(reverse('subscriptions'), {
            'action': 'subscribe_journalist',
            'journalist_id': self.journalist.id
        })
        self.assertEqual(response.status_code, 302)  # Redirect after subscription
        self.assertTrue(self.reader.subscribed_journalists.filter(id=self.journalist.id).exists())


class BrowseViewTest(TestCase):
    """Test cases for browse functionality"""
    
    def setUp(self):
        self.client = Client()
        self.publisher = Publisher.objects.create(
            name="Test Publisher"
        )
        self.journalist = User.objects.create_user(
            username='journalist1',
            email='journalist@test.com',
            password='testpass123',
            role=User.Roles.JOURNALIST
        )
        self.reader = User.objects.create_user(
            username='reader1',
            email='reader@test.com',
            password='testpass123',
            role=User.Roles.READER
        )
        
        # Create test content
        self.article = Article.objects.create(
            title="Test Article",
            body="Test content",
            author=self.journalist,
            publisher=self.publisher,
            is_approved=True
        )
        self.newsletter = Newsletter.objects.create(
            subject="Test Newsletter",
            content="Test content",
            author=self.journalist,
            publisher=self.publisher
        )
    
    def test_browse_all_news_view(self):
        """Test browse all news view"""
        self.client.login(username='reader1', password='testpass123')
        response = self.client.get(reverse('browse_all_news'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)
        self.assertContains(response, self.newsletter.subject)
    
    def test_browse_articles_filter(self):
        """Test browse with articles filter"""
        self.client.login(username='reader1', password='testpass123')
        response = self.client.get(reverse('browse_all_news'), {'content_filter': 'articles'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article.title)
        # Newsletter should not appear in articles-only view
        self.assertNotContains(response, self.newsletter.subject)
    
    def test_browse_newsletters_filter(self):
        """Test browse with newsletters filter"""
        self.client.login(username='reader1', password='testpass123')
        response = self.client.get(reverse('browse_all_news'), {'content_filter': 'newsletters'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.newsletter.subject)
        # Article should not appear in newsletters-only view
        self.assertNotContains(response, self.article.title)


class APISerializerTest(TestCase):
    """Test cases for API serializers"""
    
    def setUp(self):
        self.publisher = Publisher.objects.create(
            name="Test Publisher"
        )
        self.journalist = User.objects.create_user(
            username='journalist1',
            email='journalist@test.com',
            password='testpass123',
            role=User.Roles.JOURNALIST
        )
        self.article = Article.objects.create(
            title="Test Article",
            body="Test content",
            author=self.journalist,
            publisher=self.publisher
        )
        self.newsletter = Newsletter.objects.create(
            subject="Test Newsletter",
            content="Test content",
            author=self.journalist,
            publisher=self.publisher
        )
    
    def test_user_serializer(self):
        """Test User serializer"""
        from .serializers import UserSerializer
        serializer = UserSerializer(self.journalist)
        data = serializer.data
        self.assertEqual(data['username'], 'journalist1')
        self.assertEqual(data['role'], User.Roles.JOURNALIST)
        self.assertIn('email', data)
    
    def test_article_serializer(self):
        """Test Article serializer"""
        from .serializers import ArticleSerializer
        serializer = ArticleSerializer(self.article)
        data = serializer.data
        self.assertEqual(data['title'], 'Test Article')
        self.assertEqual(data['body'], 'Test content')
        self.assertIn('author', data)
        self.assertIn('publisher', data)
    
    def test_newsletter_serializer(self):
        """Test Newsletter serializer"""
        from .serializers import NewsletterSerializer
        serializer = NewsletterSerializer(self.newsletter)
        data = serializer.data
        self.assertEqual(data['subject'], 'Test Newsletter')
        self.assertEqual(data['content'], 'Test content')
        self.assertIn('author', data)
        self.assertIn('publisher', data)
    
    def test_publisher_serializer(self):
        """Test Publisher serializer"""
        from .serializers import PublisherSerializer
        serializer = PublisherSerializer(self.publisher)
        data = serializer.data
        self.assertEqual(data['name'], 'Test Publisher')


class PermissionTest(TestCase):
    """Test cases for role-based permissions"""
    
    def setUp(self):
        self.client = Client()
        self.publisher = Publisher.objects.create(
            name="Test Publisher"
        )
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
            affiliated_publisher=self.publisher,
        )
    
    def test_reader_permissions(self):
        """Test that readers have limited permissions"""
        self.client.login(username='reader1', password='testpass123')
        
        # Can access newsfeed
        response = self.client.get(reverse('newsfeed'))
        self.assertEqual(response.status_code, 200)
        
        # Can access subscriptions
        response = self.client.get(reverse('subscriptions'))
        self.assertEqual(response.status_code, 200)
        
        # Cannot create articles
        response = self.client.get(reverse('article_create'))
        self.assertEqual(response.status_code, 403)
        
        # Cannot create newsletters
        response = self.client.get(reverse('newsletter_create'))
        self.assertEqual(response.status_code, 403)
    
    def test_journalist_permissions(self):
        """Test that journalists can create content"""
        self.client.login(username='journalist1', password='testpass123')
        
        # Can create articles
        response = self.client.get(reverse('article_create'))
        self.assertEqual(response.status_code, 200)
        
        # Can create newsletters
        response = self.client.get(reverse('newsletter_create'))
        self.assertEqual(response.status_code, 200)
        
        # Can connect Twitter
        with patch('articles.integrations.twitter_views.OAuth2Session') as mock_oauth:
            mock_oauth.return_value.authorization_url.return_value = ('http://test.com', 'state')
            response = self.client.get(reverse('twitter_connect'))
            self.assertEqual(response.status_code, 302)
    
    def test_editor_permissions(self):
        """Test that editors can approve content"""
        article = Article.objects.create(
            title="Test Article",
            body="Test content",
            author=self.journalist,
            publisher=self.publisher
        )
        
        self.client.login(username='editor1', password='testpass123')
        
        # Can approve articles
        response = self.client.get(reverse('article_approve', kwargs={'pk': article.pk}))
        self.assertEqual(response.status_code, 302)
        
        # Can unapprove articles
        response = self.client.get(reverse('article_unapprove', kwargs={'pk': article.pk}))
        self.assertEqual(response.status_code, 302)