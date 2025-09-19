from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Article, Newsletter, Publisher, User
from .serializers import (
    ArticleSerializer, NewsletterSerializer, PublisherSerializer, UserSerializer,
    SubscriptionSerializer, ArticleListSerializer, NewsletterListSerializer
)

User = get_user_model()


class ArticleListView(generics.ListAPIView):
    """
    API endpoint for listing articles based on user subscriptions.
    For readers: shows articles from followed journalists and subscribed publishers.
    For editors/journalists: shows all articles.
    """
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == User.Roles.READER:
            # For readers: show articles from followed journalists and subscribed publishers
            followed_journalist_ids = user.subscriptions_journalists.values_list('id', flat=True)
            subscribed_publisher_ids = user.subscriptions_publishers.values_list('id', flat=True)
            
            return Article.objects.filter(
                Q(publisher__isnull=True, author_id__in=followed_journalist_ids) |
                Q(publisher_id__in=subscribed_publisher_ids)
            ).select_related('author', 'publisher').order_by('-created_at')
        else:
            # For editors and journalists: show all articles
            return Article.objects.select_related('author', 'publisher').order_by('-created_at')


class ArticleDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a specific article.
    """
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Article.objects.select_related('author', 'publisher')


class NewsletterListView(generics.ListAPIView):
    """
    API endpoint for listing newsletters based on user subscriptions.
    For readers: shows newsletters from followed journalists and subscribed publishers.
    For editors/journalists: shows all newsletters.
    """
    serializer_class = NewsletterListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == User.Roles.READER:
            # For readers: show newsletters from followed journalists and subscribed publishers
            followed_journalist_ids = user.subscriptions_journalists.values_list('id', flat=True)
            subscribed_publisher_ids = user.subscriptions_publishers.values_list('id', flat=True)
            
            return Newsletter.objects.filter(
                Q(publisher__isnull=True, author_id__in=followed_journalist_ids) |
                Q(publisher_id__in=subscribed_publisher_ids)
            ).select_related('author', 'publisher').order_by('-created_at')
        else:
            # For editors and journalists: show all newsletters
            return Newsletter.objects.select_related('author', 'publisher').order_by('-created_at')


class NewsletterDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a specific newsletter.
    """
    serializer_class = NewsletterSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Newsletter.objects.select_related('author', 'publisher')


class PublisherListView(generics.ListAPIView):
    """
    API endpoint for listing all publishers.
    """
    serializer_class = PublisherSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Publisher.objects.all().order_by('name')


class PublisherDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a specific publisher.
    """
    serializer_class = PublisherSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Publisher.objects.all()


class JournalistListView(generics.ListAPIView):
    """
    API endpoint for listing all journalists.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.filter(role=User.Roles.JOURNALIST).order_by('username')


class UserSubscriptionsView(APIView):
    """
    API endpoint for managing user subscriptions.
    GET: Retrieve user's current subscriptions
    POST: Add subscriptions (follow journalist or subscribe to publisher)
    DELETE: Remove subscriptions
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user's current subscriptions"""
        serializer = SubscriptionSerializer(request.user)
        return Response(serializer.data)
    
    def post(self, request):
        """Add subscriptions"""
        user = request.user
        data = request.data
        
        if 'journalist_id' in data:
            try:
                journalist = User.objects.get(id=data['journalist_id'], role=User.Roles.JOURNALIST)
                user.subscriptions_journalists.add(journalist)
                return Response({'message': f'Now following {journalist.username}'}, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response({'error': 'Journalist not found'}, status=status.HTTP_404_NOT_FOUND)
        
        elif 'publisher_id' in data:
            try:
                publisher = Publisher.objects.get(id=data['publisher_id'])
                user.subscriptions_publishers.add(publisher)
                return Response({'message': f'Now subscribed to {publisher.name}'}, status=status.HTTP_201_CREATED)
            except Publisher.DoesNotExist:
                return Response({'error': 'Publisher not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'error': 'Must provide journalist_id or publisher_id'}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        """Remove subscriptions"""
        user = request.user
        data = request.data
        
        if 'journalist_id' in data:
            try:
                journalist = User.objects.get(id=data['journalist_id'], role=User.Roles.JOURNALIST)
                user.subscriptions_journalists.remove(journalist)
                return Response({'message': f'Unfollowed {journalist.username}'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'Journalist not found'}, status=status.HTTP_404_NOT_FOUND)
        
        elif 'publisher_id' in data:
            try:
                publisher = Publisher.objects.get(id=data['publisher_id'])
                user.subscriptions_publishers.remove(publisher)
                return Response({'message': f'Unsubscribed from {publisher.name}'}, status=status.HTTP_200_OK)
            except Publisher.DoesNotExist:
                return Response({'error': 'Publisher not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'error': 'Must provide journalist_id or publisher_id'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_feed(request):
    """
    API endpoint for getting a combined feed of articles and newsletters
    based on user subscriptions.
    """
    user = request.user
    
    if user.role == User.Roles.READER:
        # For readers: show content from followed journalists and subscribed publishers
        followed_journalist_ids = user.subscriptions_journalists.values_list('id', flat=True)
        subscribed_publisher_ids = user.subscriptions_publishers.values_list('id', flat=True)
        
        articles = Article.objects.filter(
            Q(publisher__isnull=True, author_id__in=followed_journalist_ids) |
            Q(publisher_id__in=subscribed_publisher_ids)
        ).select_related('author', 'publisher').order_by('-created_at')[:10]
        
        newsletters = Newsletter.objects.filter(
            Q(publisher__isnull=True, author_id__in=followed_journalist_ids) |
            Q(publisher_id__in=subscribed_publisher_ids)
        ).select_related('author', 'publisher').order_by('-created_at')[:10]
    else:
        # For editors and journalists: show all content
        articles = Article.objects.select_related('author', 'publisher').order_by('-created_at')[:10]
        newsletters = Newsletter.objects.select_related('author', 'publisher').order_by('-created_at')[:10]
    
    # Combine and serialize
    feed_data = {
        'articles': ArticleListSerializer(articles, many=True).data,
        'newsletters': NewsletterListSerializer(newsletters, many=True).data,
        'total_articles': articles.count(),
        'total_newsletters': newsletters.count(),
    }
    
    return Response(feed_data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_info(request):
    """
    API endpoint for getting API information and available endpoints.
    """
    info = {
        'api_name': 'News Application API',
        'version': '1.0',
        'description': 'RESTful API for retrieving articles and newsletters from publishers and journalists',
        'endpoints': {
            'articles': {
                'list': '/api/articles/',
                'detail': '/api/articles/{id}/',
            },
            'newsletters': {
                'list': '/api/newsletters/',
                'detail': '/api/newsletters/{id}/',
            },
            'publishers': {
                'list': '/api/publishers/',
                'detail': '/api/publishers/{id}/',
            },
            'journalists': {
                'list': '/api/journalists/',
            },
            'subscriptions': {
                'manage': '/api/subscriptions/',
            },
            'feed': {
                'combined': '/api/feed/',
            }
        },
        'authentication': {
            'methods': ['Session', 'Token'],
            'token_endpoint': '/api/auth/token/',
        },
        'formats': ['JSON', 'XML'],
        'pagination': 'Page-based (20 items per page)',
    }
    
    return Response(info)
