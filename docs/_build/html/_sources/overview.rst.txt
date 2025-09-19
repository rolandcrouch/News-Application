Application Overview
===================

Architecture
============

The Django News Application follows a role-based architecture with three distinct user types,
each with specific permissions and capabilities.

User Roles and Permissions
===========================

Readers
-------

Readers are the primary consumers of content in the application. They have the following capabilities:

* Subscribe to publishers to receive notifications about new content
* Follow individual journalists to see their independent work
* Browse all approved articles and newsletters
* Manage their subscription preferences
* Access personalized news feeds based on their subscriptions

**Database Fields:**
* ``subscriptions_publishers``: Many-to-many relationship with publishers
* ``subscriptions_journalists``: Many-to-many relationship with journalists

Journalists
-----------

Journalists are content creators who can publish both independently and through publishers:

* Create and edit articles and newsletters
* Publish content independently (without publisher affiliation)
* Work with publishers as affiliated journalists
* View all content in the system
* Cannot approve their own content

**Key Features:**
* Independent publishing capability
* Publisher affiliation support
* Content creation permissions

Editors
-------

Editors have administrative control over content and publishers:

* Approve or reject articles and newsletters
* Publish approved content to Twitter (if configured)
* Manage publisher relationships
* Create new publishers
* Cannot create content themselves

**Database Fields:**
* ``affiliated_publisher``: Foreign key to associated publisher

Publishers
==========

Publishers act as content organizations that can have:

* Multiple affiliated editors
* Multiple affiliated journalists
* Subscribers (readers who follow the publisher)
* Branded content approval workflows

Content Management
==================

Articles
--------

Articles are the primary content type with the following attributes:

* **Title**: Article headline
* **Body**: Full article content
* **Author**: Must be a journalist
* **Publisher**: Optional, can be independent
* **Approval Status**: Requires editor approval for publication
* **Timestamps**: Creation and modification tracking

Newsletters
-----------

Newsletters are email-style content with:

* **Subject**: Newsletter headline
* **Content**: Newsletter body
* **Author**: Must be a journalist
* **Publisher**: Optional, can be independent
* **Timestamps**: Creation and modification tracking

Subscription System
===================

The application implements a flexible subscription system:

Publisher Subscriptions
-----------------------

Readers can subscribe to publishers to:
* Receive notifications when new content is published
* See publisher content in their personalized feed
* Get email notifications for approved articles

Journalist Following
--------------------

Readers can follow individual journalists to:
* See independent content from followed journalists
* Track journalist activity across publishers
* Receive updates on new publications

Content Feeds
=============

Personalized Feeds
------------------

Each user type sees different content in their feeds:

* **Readers**: Content from subscribed publishers and followed journalists
* **Journalists**: All content in the system
* **Editors**: All content in the system with approval capabilities

Browse All
----------

A separate "Browse All" view allows readers to:
* Discover new publishers and journalists
* Search and filter content
* Find content outside their current subscriptions

Approval Workflow
=================

Content Approval Process
------------------------

1. **Creation**: Journalist creates article or newsletter
2. **Submission**: Content is saved with ``is_approved=False``
3. **Review**: Editor reviews content for approval
4. **Approval**: Editor approves content (``is_approved=True``)
5. **Publication**: Approved content becomes visible to readers
6. **Notification**: Email notifications sent to subscribers
7. **Social Media**: Optional Twitter posting for approved content

Integration Features
====================

Twitter Integration
-------------------

The application includes OAuth2-based Twitter integration:

* Secure PKCE-based authentication
* Automatic tweet composition for approved content
* Media upload support
* Rate limiting and error handling

Email Notifications
-------------------

Automated email system for:

* New content notifications to subscribers
* Account management (password reset, username recovery)
* System notifications

API Architecture
================

RESTful Design
--------------

The API follows REST principles with:

* Resource-based URLs
* HTTP methods for different operations
* JSON request/response format
* Token-based authentication
* Proper HTTP status codes

Authentication
--------------

* Token-based authentication for API access
* Session-based authentication for web interface
* Role-based access control
* Secure password handling

Security Features
=================

* CSRF protection for web forms
* SQL injection prevention through Django ORM
* XSS protection with template auto-escaping
* Secure password hashing
* Role-based access control
* Input validation and sanitization
