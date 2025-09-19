#!/bin/bash

# Django News Application - Development Docker Script
# Usage: ./scripts/docker-dev.sh [command]

set -e

PROJECT_NAME="django-news-app"
COMPOSE_FILE="docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to build the development environment
build() {
    print_status "Building development environment..."
    check_docker
    
    docker-compose -f $COMPOSE_FILE build --no-cache
    print_success "Development environment built successfully!"
}

# Function to start the development environment
start() {
    print_status "Starting development environment..."
    check_docker
    
    docker-compose -f $COMPOSE_FILE up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 10
    
    # Check if web service is running
    if docker-compose -f $COMPOSE_FILE ps web | grep -q "Up"; then
        print_success "Development environment is running!"
        print_status "Web application: http://localhost:8000"
        print_status "API documentation: http://localhost:8000/api/info/"
        print_status "Admin panel: http://localhost:8000/admin/"
        print_warning "Default admin credentials: admin/admin123"
    else
        print_error "Failed to start development environment"
        docker-compose -f $COMPOSE_FILE logs web
        exit 1
    fi
}

# Function to stop the development environment
stop() {
    print_status "Stopping development environment..."
    docker-compose -f $COMPOSE_FILE down
    print_success "Development environment stopped!"
}

# Function to restart the development environment
restart() {
    print_status "Restarting development environment..."
    stop
    start
}

# Function to view logs
logs() {
    service=${2:-web}
    print_status "Showing logs for $service..."
    docker-compose -f $COMPOSE_FILE logs -f $service
}

# Function to run Django management commands
manage() {
    if [ $# -lt 2 ]; then
        print_error "Usage: $0 manage <command>"
        print_status "Example: $0 manage makemigrations"
        exit 1
    fi
    
    shift # Remove 'manage' from arguments
    print_status "Running Django command: $*"
    docker-compose -f $COMPOSE_FILE exec web python manage.py "$@"
}

# Function to run shell
shell() {
    print_status "Opening Django shell..."
    docker-compose -f $COMPOSE_FILE exec web python manage.py shell
}

# Function to run database shell
dbshell() {
    print_status "Opening database shell..."
    docker-compose -f $COMPOSE_FILE exec db mysql -u newsapp_user -p newapp_db
}

# Function to run tests
test() {
    print_status "Running tests..."
    docker-compose -f $COMPOSE_FILE exec web python run_tests.py
}

# Function to create backup
backup() {
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_file="backup_${timestamp}.sql"
    
    print_status "Creating database backup: $backup_file"
    docker-compose -f $COMPOSE_FILE exec db mysqldump -u newsapp_user -pnewsapp_password newapp_db > $backup_file
    print_success "Database backup created: $backup_file"
}

# Function to reset the development environment
reset() {
    print_warning "This will destroy all containers and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Resetting development environment..."
        docker-compose -f $COMPOSE_FILE down -v --remove-orphans
        docker-compose -f $COMPOSE_FILE build --no-cache
        print_success "Development environment reset complete!"
    else
        print_status "Reset cancelled."
    fi
}

# Function to show status
status() {
    print_status "Development environment status:"
    docker-compose -f $COMPOSE_FILE ps
}

# Function to show help
help() {
    echo "Django News Application - Development Docker Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  build     Build the development environment"
    echo "  start     Start the development environment"
    echo "  stop      Stop the development environment"
    echo "  restart   Restart the development environment"
    echo "  logs      Show logs (optionally specify service: logs web)"
    echo "  manage    Run Django management commands (e.g., manage makemigrations)"
    echo "  shell     Open Django shell"
    echo "  dbshell   Open database shell"
    echo "  test      Run tests"
    echo "  backup    Create database backup"
    echo "  reset     Reset environment (destroys all data)"
    echo "  status    Show container status"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 manage createsuperuser"
    echo "  $0 logs web"
    echo "  $0 test"
}

# Main script logic
case "${1:-help}" in
    build)
        build
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs "$@"
        ;;
    manage)
        manage "$@"
        ;;
    shell)
        shell
        ;;
    dbshell)
        dbshell
        ;;
    test)
        test
        ;;
    backup)
        backup
        ;;
    reset)
        reset
        ;;
    status)
        status
        ;;
    help|--help|-h)
        help
        ;;
    *)
        print_error "Unknown command: $1"
        help
        exit 1
        ;;
esac
