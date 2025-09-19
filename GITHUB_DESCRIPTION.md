# 📰 Django News Application

A comprehensive, role-based news management platform built with Django, featuring social media integration, content approval workflows, and modern responsive design.

## 🌟 Key Features

### 📋 **Multi-Role System**
- **Readers**: Subscribe to publishers, browse content, personalized news feed
- **Journalists**: Create articles, connect Twitter accounts, publish content
- **Editors**: Approve/reject content, manage publications, oversee platform

### 🔗 **Social Media Integration**
- **Twitter/X OAuth 2.0** integration with automatic posting
- **Real-time status updates** and connection management
- **Secure PKCE flow** for enhanced authentication

### 📧 **Smart Notifications**
- **Email alerts** for content approval/rejection
- **Gmail integration** with App Password support
- **Role-based notification system**

### 🎨 **Modern UI/UX**
- **Responsive Bootstrap design** optimized for all devices
- **Role-based color coding** and intuitive navigation
- **Clean, professional interface** with custom CSS styling

### 🔒 **Security & Authentication**
- **Django's built-in authentication** with custom user roles
- **Session management** and secure logout functionality
- **Environment-based configuration** for sensitive data

## 🚀 Quick Start

### Docker Deployment (Recommended)
```bash
git clone https://github.com/your-username/django-news-application.git
cd django-news-application
docker-compose up -d
```
**Access at**: http://localhost:8000

### Test Accounts
- **Reader**: `reader1` / `password123`
- **Journalist**: `journalist1` / `password123` 
- **Editor**: `editor1` / `password123`

## 🛠️ Technology Stack

- **Backend**: Django 5.2.6, Python 3.13
- **Database**: MySQL 8.0 with utf8mb4 support
- **Frontend**: Bootstrap 5, Custom CSS, Responsive design
- **APIs**: Twitter API v2, Gmail SMTP
- **Deployment**: Docker & Docker Compose
- **Authentication**: Django Auth + OAuth 2.0 PKCE

## 📁 Core Functionality

### Content Management
- ✅ **Article Creation** with rich text editing
- ✅ **Newsletter Publishing** with email distribution
- ✅ **Content Approval Workflow** for quality control
- ✅ **Publisher Management** and affiliation system

### User Experience
- ✅ **Personalized News Feed** based on subscriptions
- ✅ **Browse All Content** for content discovery
- ✅ **Subscription Management** for publishers and journalists
- ✅ **Real-time Status Updates** for social media connections

### Integration Features
- ✅ **Automatic Twitter Posting** when content is approved
- ✅ **Email Notifications** for all stakeholders
- ✅ **Environment Configuration** for easy deployment
- ✅ **Health Checks** and monitoring support

## 🔧 Configuration

### Environment Variables
```env
# Twitter Integration
TWITTER_CLIENT_ID=your_client_id
TWITTER_CLIENT_SECRET=your_client_secret
TWITTER_REDIRECT_URI=http://localhost:8000/accounts/twitter/callback/

# Email Configuration
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password

# Database (for manual setup)
DB_NAME=newapp_db
DB_USER=newsapp_user
DB_PASSWORD=newsapp_password
```

## 📊 Project Structure

```
django-news-application/
├── articles/                 # Main Django app
├── news_app/                # Project settings
├── templates/               # HTML templates
├── static/                  # CSS, JS, images
├── docker-compose.yml       # Multi-service setup
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies
└── create_test_users.py    # Test data script
```

## 🎯 Use Cases

### News Organizations
- **Multi-editor workflow** for content approval
- **Social media automation** for increased reach
- **Reader engagement** through subscriptions

### Content Creators
- **Professional publishing platform** with approval process
- **Social media integration** for automatic promotion
- **Audience management** and subscription tracking

### Educational Projects
- **Role-based system demonstration** 
- **Django best practices** implementation
- **API integration** examples

## 🔍 Advanced Features

### Database Design
- **Optimized MySQL schema** with proper indexing
- **Foreign key relationships** for data integrity
- **Migration support** for schema evolution

### Security Measures
- **CSRF protection** on all forms
- **SQL injection prevention** through ORM
- **Secure password hashing** with Django's built-in system
- **Environment variable protection** for sensitive data

### Performance Optimization
- **Static file handling** with proper caching
- **Database query optimization** 
- **Responsive design** for fast loading
- **Docker containerization** for consistent deployment

## 📈 Scalability

- **Docker-ready** for easy horizontal scaling
- **Database separation** for performance optimization
- **Environment-based configuration** for multiple deployments
- **Modular architecture** for feature extension

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 **Documentation**: Comprehensive README and deployment guides
- 🐛 **Issues**: GitHub Issues for bug reports and feature requests
- 💬 **Discussions**: GitHub Discussions for questions and community support

---

**Built with ❤️ using Django and modern web technologies**

