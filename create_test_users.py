#!/usr/bin/env python3
"""
Create test users for API testing
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_app.settings')
django.setup()

from articles.models import User, Publisher

def create_test_users():
    print("=== Creating Test Users ===")
    
    # Create a publisher first
    publisher, created = Publisher.objects.get_or_create(
        name="Tech News",
        defaults={'name': 'Tech News'}
    )
    if created:
        print(f"✅ Created publisher: {publisher.name}")
    else:
        print(f"✅ Found existing publisher: {publisher.name}")
    
    # Create test users
    test_users = [
        {
            'username': 'reader1',
            'email': 'reader1@test.com',
            'password': 'testpass123',
            'role': User.Roles.READER,
            'first_name': 'Test',
            'last_name': 'Reader'
        },
        {
            'username': 'journalist1',
            'email': 'journalist1@test.com',
            'password': 'testpass123',
            'role': User.Roles.JOURNALIST,
            'first_name': 'Test',
            'last_name': 'Journalist'
        },
        {
            'username': 'editor1',
            'email': 'editor1@test.com',
            'password': 'testpass123',
            'role': User.Roles.EDITOR,
            'first_name': 'Test',
            'last_name': 'Editor',
            'affiliated_publisher': publisher
        }
    ]
    
    for user_data in test_users:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"✅ Created {user_data['role']}: {user_data['username']}")
        else:
            print(f"✅ Found existing {user_data['role']}: {user_data['username']}")
    
    print("\n=== Test Users Created ===")
    print("You can now use these credentials to test the API:")
    print("• Reader: username='reader1', password='testpass123'")
    print("• Journalist: username='journalist1', password='testpass123'")
    print("• Editor: username='editor1', password='testpass123'")
    print("\nTest the API with these credentials in Postman or curl!")

if __name__ == "__main__":
    create_test_users()

