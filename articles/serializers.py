from rest_framework import serializers
from .models import Article, Newsletter, Publisher, User


class PublisherSerializer(serializers.ModelSerializer):
    """Serializer for Publisher model"""
    class Meta:
        model = Publisher
        fields = ['id', 'name']
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (simplified for API)"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'role_display', 'affiliated_publisher']
        read_only_fields = ['id', 'role', 'affiliated_publisher']


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model"""
    author = UserSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    publisher_name = serializers.CharField(source='publisher.name', read_only=True)
    is_approved_display = serializers.CharField(source='get_is_approved_display', read_only=True)
    created_at_formatted = serializers.DateTimeField(source='created_at', read_only=True, format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'body', 'author', 'author_username', 'publisher', 'publisher_name',
            'is_approved', 'is_approved_display', 'approved_by', 'created_at', 'created_at_formatted'
        ]
        read_only_fields = ['id', 'author', 'is_approved', 'approved_by', 'created_at']


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for Newsletter model"""
    author = UserSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    publisher_name = serializers.CharField(source='publisher.name', read_only=True)
    created_at_formatted = serializers.DateTimeField(source='created_at', read_only=True, format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = Newsletter
        fields = [
            'id', 'subject', 'content', 'author', 'author_username', 'publisher', 'publisher_name',
            'created_at', 'created_at_formatted'
        ]
        read_only_fields = ['id', 'author', 'created_at']


class SubscriptionSerializer(serializers.Serializer):
    """Serializer for user subscriptions"""
    subscribed_publishers = PublisherSerializer(many=True, read_only=True)
    followed_journalists = UserSerializer(many=True, read_only=True)
    
    def to_representation(self, instance):
        return {
            'subscribed_publishers': PublisherSerializer(instance.subscriptions_publishers.all(), many=True).data,
            'followed_journalists': UserSerializer(instance.subscriptions_journalists.all(), many=True).data,
        }


class ArticleListSerializer(serializers.ModelSerializer):
    """Simplified serializer for article lists"""
    author_username = serializers.CharField(source='author.username', read_only=True)
    publisher_name = serializers.CharField(source='publisher.name', read_only=True)
    is_approved_display = serializers.CharField(source='get_is_approved_display', read_only=True)
    created_at_formatted = serializers.DateTimeField(source='created_at', read_only=True, format='%Y-%m-%d %H:%M:%S')
    body_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'body_preview', 'author_username', 'publisher_name',
            'is_approved', 'is_approved_display', 'created_at_formatted'
        ]
    
    def get_body_preview(self, obj):
        """Return first 200 characters of body"""
        return obj.body[:200] + '...' if len(obj.body) > 200 else obj.body


class NewsletterListSerializer(serializers.ModelSerializer):
    """Simplified serializer for newsletter lists"""
    author_username = serializers.CharField(source='author.username', read_only=True)
    publisher_name = serializers.CharField(source='publisher.name', read_only=True)
    created_at_formatted = serializers.DateTimeField(source='created_at', read_only=True, format='%Y-%m-%d %H:%M:%S')
    content_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Newsletter
        fields = [
            'id', 'subject', 'content_preview', 'author_username', 'publisher_name',
            'created_at_formatted'
        ]
    
    def get_content_preview(self, obj):
        """Return first 200 characters of content"""
        return obj.content[:200] + '...' if len(obj.content) > 200 else obj.content
