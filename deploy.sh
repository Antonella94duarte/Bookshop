#!/bin/bash

# Bookshop Deployment Script for Linux
# This script automates the deployment of the Bookshop application using Docker

set -e  # Exit on error

echo "=========================================="
echo " Bookshop Deployment Script"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo " Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo " Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Stop and remove existing containers
echo " Stopping existing containers..."
docker-compose down
echo ""

# Build Docker images
echo "Building Docker images..."
docker-compose build
echo ""

# Start containers
echo "Starting containers..."
docker-compose up -d
echo ""

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 10
echo ""

# Run migrations
echo "Running database migrations..."
docker-compose exec -T web python manage.py makemigrations
docker-compose exec -T web python manage.py migrate
echo ""

# Load initial data
echo "Loading initial data..."
docker-compose exec -T web python manage.py load_initial_data
echo ""

# Collect static files
echo "📦 Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput
echo ""

# Create superuser (if needed)
echo "👤 Creating superuser..."
echo "Please enter superuser credentials:"
docker-compose exec web python manage.py createsuperuser
echo ""

# Show running containers
echo "📋 Running containers:"
docker-compose ps
echo ""

# Show application URLs
echo "=========================================="
echo "✅ Deployment completed successfully!"
echo "=========================================="
echo ""
echo "🌐 Application URLs:"
echo "   - API: http://localhost:8000/api/"
echo "   - Admin Panel: http://localhost:8000/admin/"
echo ""
echo "📚 API Endpoints:"
echo "   - Authors: http://localhost:8000/api/authors/"
echo "   - Books: http://localhost:8000/api/books/"
echo ""
echo "🔧 Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop application: docker-compose down"
echo "   - Restart application: docker-compose restart"
echo "   - Run tests: docker-compose exec web python manage.py test"
echo ""
echo "=========================================="