#!/usr/bin/env python
"""
Test runner script for Django News Application

This script runs the comprehensive test suite and provides detailed output
about test coverage and results.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --verbose          # Run with verbose output
    python run_tests.py --coverage         # Run with coverage report
    python run_tests.py --fast             # Run fast tests only
    python run_tests.py --specific MODEL   # Run specific test class
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_app.settings')

import django
from django.conf import settings
from django.test.utils import get_runner
from django.core.management import execute_from_command_line


def run_tests(test_labels=None, verbosity=1, interactive=False, failfast=False, keepdb=False):
    """Run Django tests with specified parameters"""
    
    # Set up Django
    django.setup()
    
    # Get the Django test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(
        verbosity=verbosity,
        interactive=interactive,
        failfast=failfast,
        keepdb=keepdb
    )
    
    # Run the tests
    if test_labels:
        failures = test_runner.run_tests(test_labels)
    else:
        failures = test_runner.run_tests(['articles'])
    
    return failures


def run_coverage_tests():
    """Run tests with coverage reporting"""
    try:
        import coverage
        print("Running tests with coverage...")
        
        # Start coverage
        cov = coverage.Coverage()
        cov.start()
        
        # Run tests
        failures = run_tests(verbosity=2)
        
        # Stop coverage and generate report
        cov.stop()
        cov.save()
        
        print("\n" + "="*50)
        print("COVERAGE REPORT")
        print("="*50)
        
        # Generate coverage report
        cov.report(show_missing=True)
        
        # Generate HTML coverage report
        cov.html_report(directory='htmlcov')
        print(f"\nHTML coverage report generated in: {project_dir}/htmlcov/index.html")
        
        return failures
        
    except ImportError:
        print("Coverage package not installed. Install with: pip install coverage")
        print("Running tests without coverage...")
        return run_tests(verbosity=2)


def run_specific_tests(test_class):
    """Run specific test class"""
    test_labels = [f'articles.tests.{test_class}']
    print(f"Running specific tests: {test_class}")
    return run_tests(test_labels, verbosity=2)


def run_fast_tests():
    """Run only fast tests (excluding integration tests)"""
    fast_test_classes = [
        'articles.tests.UserModelTest',
        'articles.tests.ArticleModelTest', 
        'articles.tests.NewsletterModelTest',
        'articles.tests.PublisherModelTest',
        'articles.tests.UserRegistrationFormTest',
        'articles.tests.ArticleFormTest',
        'articles.tests.NewsletterFormTest',
        'articles.tests.APISerializerTest',
    ]
    print("Running fast tests (models, forms, serializers)...")
    return run_tests(fast_test_classes, verbosity=2)


def print_test_summary():
    """Print a summary of available tests"""
    print("="*60)
    print("DJANGO NEWS APPLICATION - TEST SUITE")
    print("="*60)
    print("\nAvailable Test Classes:")
    print("  📊 Model Tests:")
    print("    • UserModelTest - Custom user model functionality")
    print("    • ArticleModelTest - Article model and relationships")
    print("    • NewsletterModelTest - Newsletter model functionality")
    print("    • PublisherModelTest - Publisher model and constraints")
    
    print("\n  📝 Form Tests:")
    print("    • UserRegistrationFormTest - User registration validation")
    print("    • ArticleFormTest - Article creation form validation")
    print("    • NewsletterFormTest - Newsletter creation form validation")
    
    print("\n  🌐 View Tests:")
    print("    • AuthenticationViewTest - Login/logout/register views")
    print("    • ArticleViewTest - Article CRUD operations")
    print("    • NewsletterViewTest - Newsletter CRUD operations")
    print("    • BrowseViewTest - Content browsing functionality")
    print("    • SubscriptionTest - User subscription management")
    
    print("\n  🔗 Integration Tests:")
    print("    • TwitterIntegrationTest - Twitter OAuth and posting")
    print("    • EmailNotificationTest - Email notification system")
    
    print("\n  🔐 Security Tests:")
    print("    • PermissionTest - Role-based access control")
    
    print("\n  📡 API Tests:")
    print("    • APISerializerTest - REST API serialization")
    
    print("\n" + "="*60)
    print("Total Test Methods: ~60+ comprehensive test cases")
    print("Coverage: Models, Views, Forms, APIs, Integrations, Permissions")
    print("="*60)


def main():
    parser = argparse.ArgumentParser(description='Run Django News Application tests')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Run tests with verbose output')
    parser.add_argument('--coverage', '-c', action='store_true',
                       help='Run tests with coverage report')
    parser.add_argument('--fast', '-f', action='store_true',
                       help='Run only fast tests (no integration tests)')
    parser.add_argument('--specific', '-s', type=str,
                       help='Run specific test class (e.g., UserModelTest)')
    parser.add_argument('--summary', action='store_true',
                       help='Show test suite summary')
    parser.add_argument('--failfast', action='store_true',
                       help='Stop on first test failure')
    parser.add_argument('--keepdb', action='store_true',
                       help='Keep test database after tests')
    
    args = parser.parse_args()
    
    if args.summary:
        print_test_summary()
        return 0
    
    print_test_summary()
    print(f"\nStarting tests from: {project_dir}")
    print("-" * 60)
    
    try:
        if args.coverage:
            failures = run_coverage_tests()
        elif args.fast:
            failures = run_fast_tests()
        elif args.specific:
            failures = run_specific_tests(args.specific)
        else:
            verbosity = 2 if args.verbose else 1
            failures = run_tests(
                verbosity=verbosity,
                failfast=args.failfast,
                keepdb=args.keepdb
            )
        
        print("-" * 60)
        if failures:
            print(f"❌ Tests completed with {failures} failures")
            return 1
        else:
            print("✅ All tests passed successfully!")
            return 0
            
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

