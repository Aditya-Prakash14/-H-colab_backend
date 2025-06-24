#!/bin/bash

# HackMate Deployment Script
# This script helps deploy the HackMate application to various platforms

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to deploy with Docker
deploy_docker() {
    print_status "Deploying with Docker..."
    
    # Check if Docker is installed
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Copy environment file
    if [ ! -f .env ]; then
        print_warning ".env file not found. Copying from .env.production..."
        cp .env.production .env
        print_warning "Please edit .env file with your production settings before continuing."
        read -p "Press enter to continue after editing .env file..."
    fi
    
    # Build and start services
    print_status "Building Docker images..."
    docker-compose build
    
    print_status "Starting services..."
    docker-compose up -d
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Run migrations
    print_status "Running database migrations..."
    docker-compose exec backend python manage.py migrate
    
    # Create superuser if needed
    print_status "Creating superuser (if needed)..."
    docker-compose exec backend python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@hackmate.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"
    
    # Populate initial data
    print_status "Populating initial data..."
    docker-compose exec backend python manage.py populate_initial_data
    
    print_status "Deployment completed successfully!"
    print_status "Application is running at: http://localhost"
    print_status "Admin panel: http://localhost/admin/"
    print_status "API documentation: http://localhost/api/v1/"
}

# Function to deploy to Heroku
deploy_heroku() {
    print_status "Deploying to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command_exists heroku; then
        print_error "Heroku CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if user is logged in to Heroku
    if ! heroku auth:whoami >/dev/null 2>&1; then
        print_error "Please login to Heroku first: heroku login"
        exit 1
    fi
    
    # Create Heroku app if it doesn't exist
    read -p "Enter your Heroku app name: " app_name
    
    if ! heroku apps:info "$app_name" >/dev/null 2>&1; then
        print_status "Creating Heroku app: $app_name"
        heroku create "$app_name"
    fi
    
    # Add Heroku PostgreSQL addon
    print_status "Adding PostgreSQL addon..."
    heroku addons:create heroku-postgresql:mini -a "$app_name" || true
    
    # Set environment variables
    print_status "Setting environment variables..."
    heroku config:set DEBUG=False -a "$app_name"
    heroku config:set ALLOWED_HOSTS="$app_name.herokuapp.com" -a "$app_name"
    
    # Generate a secret key
    secret_key=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    heroku config:set SECRET_KEY="$secret_key" -a "$app_name"
    
    # Deploy
    print_status "Deploying to Heroku..."
    git add .
    git commit -m "Deploy to Heroku" || true
    git push heroku main
    
    # Run migrations
    print_status "Running migrations..."
    heroku run python backend/manage.py migrate -a "$app_name"
    
    # Create superuser
    print_status "Creating superuser..."
    heroku run python backend/manage.py createsuperuser -a "$app_name"
    
    print_status "Deployment completed successfully!"
    print_status "Application URL: https://$app_name.herokuapp.com"
}

# Main menu
echo "HackMate Deployment Script"
echo "=========================="
echo "1. Deploy with Docker (local/VPS)"
echo "2. Deploy to Heroku"
echo "3. Exit"
echo

read -p "Choose deployment option (1-3): " choice

case $choice in
    1)
        deploy_docker
        ;;
    2)
        deploy_heroku
        ;;
    3)
        print_status "Exiting..."
        exit 0
        ;;
    *)
        print_error "Invalid option. Please choose 1, 2, or 3."
        exit 1
        ;;
esac
