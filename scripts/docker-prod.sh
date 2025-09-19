#!/bin/bash

# Django News Application - Production Docker Script
# Usage: ./scripts/docker-prod.sh [command]

set -e

PROJECT_NAME="django-news-app-prod"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"

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

# Function to check if environment file exists
check_env() {
    if [ ! -f "$ENV_FILE" ]; then
        print_error "Production environment file not found: $ENV_FILE"
        print_status "Please create $ENV_FILE with production settings."
        print_status "You can copy from .env.example and modify for production."
        exit 1
    fi
}

# Function to build the production environment
build() {
    print_status "Building production environment..."
    check_docker
    check_env
    
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE build --no-cache
    print_success "Production environment built successfully!"
}

# Function to start the production environment
start() {
    print_status "Starting production environment..."
    check_docker
    check_env
    
    # Create required directories
    mkdir -p backups nginx/ssl
    
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 30
    
    # Check if web service is running
    if docker-compose -f $COMPOSE_FILE ps web | grep -q "Up"; then
        print_success "Production environment is running!"
        print_status "Web application: https://your-domain.com"
        print_status "API documentation: https://your-domain.com/api/info/"
        print_warning "Make sure to configure SSL certificates and domain name"
    else
        print_error "Failed to start production environment"
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE logs web
        exit 1
    fi
}

# Function to stop the production environment
stop() {
    print_status "Stopping production environment..."
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE down
    print_success "Production environment stopped!"
}

# Function to restart the production environment
restart() {
    print_status "Restarting production environment..."
    stop
    start
}

# Function to view logs
logs() {
    service=${2:-web}
    print_status "Showing logs for $service..."
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE logs -f $service
}

# Function to run Django management commands
manage() {
    if [ $# -lt 2 ]; then
        print_error "Usage: $0 manage <command>"
        print_status "Example: $0 manage collectstatic"
        exit 1
    fi
    
    shift # Remove 'manage' from arguments
    print_status "Running Django command: $*"
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec web python manage.py "$@"
}

# Function to create backup
backup() {
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_file="backups/backup_${timestamp}.sql"
    
    print_status "Creating database backup: $backup_file"
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec db pg_dump -U newsapp_user newsapp_prod > $backup_file
    
    # Compress the backup
    gzip $backup_file
    print_success "Database backup created: ${backup_file}.gz"
    
    # Clean up old backups (keep last 7 days)
    find backups/ -name "backup_*.sql.gz" -mtime +7 -delete
    print_status "Old backups cleaned up (keeping last 7 days)"
}

# Function to restore from backup
restore() {
    if [ $# -lt 2 ]; then
        print_error "Usage: $0 restore <backup_file>"
        print_status "Example: $0 restore backups/backup_20231219_120000.sql.gz"
        exit 1
    fi
    
    backup_file="$2"
    
    if [ ! -f "$backup_file" ]; then
        print_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    print_warning "This will replace the current database. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Restoring database from: $backup_file"
        
        # Stop web service to prevent connections
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE stop web
        
        # Restore database
        if [[ "$backup_file" == *.gz ]]; then
            zcat "$backup_file" | docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec -T db psql -U newsapp_user newsapp_prod
        else
            docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec -T db psql -U newsapp_user newsapp_prod < "$backup_file"
        fi
        
        # Restart web service
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE start web
        
        print_success "Database restored successfully!"
    else
        print_status "Restore cancelled."
    fi
}

# Function to update the application
update() {
    print_status "Updating production application..."
    
    # Pull latest code (assuming git repository)
    if [ -d ".git" ]; then
        print_status "Pulling latest code..."
        git pull
    fi
    
    # Rebuild and restart
    build
    
    # Stop services
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE down
    
    # Start services
    start
    
    # Run migrations
    print_status "Running database migrations..."
    manage migrate
    
    # Collect static files
    print_status "Collecting static files..."
    manage collectstatic --noinput
    
    print_success "Application updated successfully!"
}

# Function to show SSL certificate status
ssl_status() {
    print_status "Checking SSL certificate status..."
    
    if [ -f "nginx/ssl/cert.pem" ] && [ -f "nginx/ssl/key.pem" ]; then
        # Check certificate expiration
        expiry_date=$(openssl x509 -in nginx/ssl/cert.pem -noout -enddate | cut -d= -f2)
        print_status "SSL certificate expires: $expiry_date"
        
        # Check if certificate is valid for more than 30 days
        if openssl x509 -checkend 2592000 -noout -in nginx/ssl/cert.pem; then
            print_success "SSL certificate is valid for more than 30 days"
        else
            print_warning "SSL certificate expires within 30 days!"
        fi
    else
        print_warning "SSL certificates not found in nginx/ssl/"
        print_status "Please add your SSL certificates to nginx/ssl/cert.pem and nginx/ssl/key.pem"
    fi
}

# Function to show monitoring information
monitor() {
    print_status "Production environment monitoring:"
    echo ""
    
    # Container status
    print_status "Container Status:"
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE ps
    echo ""
    
    # Resource usage
    print_status "Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" $(docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE ps -q)
    echo ""
    
    # Disk usage
    print_status "Volume Usage:"
    docker system df -v | grep -E "(VOLUME NAME|django-news-app)"
    echo ""
    
    # Recent logs
    print_status "Recent Error Logs:"
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE logs --tail=10 web | grep -i error || echo "No recent errors found"
}

# Function to show health status
health() {
    print_status "Checking application health..."
    
    # Check if services are running
    services=(web db redis nginx)
    all_healthy=true
    
    for service in "${services[@]}"; do
        if docker-compose -f $COMPOSE_FILE ps $service | grep -q "Up"; then
            print_success "$service: Running"
        else
            print_error "$service: Not running"
            all_healthy=false
        fi
    done
    
    # Check application endpoint
    if curl -f -s http://localhost/health/ > /dev/null; then
        print_success "Application: Responding"
    else
        print_error "Application: Not responding"
        all_healthy=false
    fi
    
    if [ "$all_healthy" = true ]; then
        print_success "All services are healthy!"
    else
        print_error "Some services are unhealthy!"
        exit 1
    fi
}

# Function to show help
help() {
    echo "Django News Application - Production Docker Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  build       Build the production environment"
    echo "  start       Start the production environment"
    echo "  stop        Stop the production environment"
    echo "  restart     Restart the production environment"
    echo "  logs        Show logs (optionally specify service: logs web)"
    echo "  manage      Run Django management commands"
    echo "  backup      Create database backup"
    echo "  restore     Restore from backup"
    echo "  update      Update application (pull code, rebuild, restart)"
    echo "  ssl-status  Check SSL certificate status"
    echo "  monitor     Show monitoring information"
    echo "  health      Check application health"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 manage createsuperuser"
    echo "  $0 backup"
    echo "  $0 restore backups/backup_20231219_120000.sql.gz"
    echo "  $0 monitor"
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
    backup)
        backup
        ;;
    restore)
        restore "$@"
        ;;
    update)
        update
        ;;
    ssl-status)
        ssl_status
        ;;
    monitor)
        monitor
        ;;
    health)
        health
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
