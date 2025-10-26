# Bookshop Deployment Script for Windows
# This script automates the deployment of the Bookshop application using Docker

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Bookshop Deployment Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker ps | Out-Null
    Write-Host "[OK] Docker is running" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Stop and remove existing containers
Write-Host "[INFO] Stopping existing containers..." -ForegroundColor Yellow
docker-compose down
Write-Host ""

# Build Docker images
Write-Host "[INFO] Building Docker images..." -ForegroundColor Yellow
docker-compose build
Write-Host ""

# Start containers
Write-Host "[INFO] Starting containers..." -ForegroundColor Yellow
docker-compose up -d
Write-Host ""

# Wait for database to be ready
Write-Host "[INFO] Waiting for database to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host ""

# Run migrations
Write-Host "[INFO] Running database migrations..." -ForegroundColor Yellow
docker-compose exec -T web python manage.py makemigrations
docker-compose exec -T web python manage.py migrate
Write-Host ""

# Load initial data
Write-Host "[INFO] Loading initial data..." -ForegroundColor Yellow
docker-compose exec -T web python manage.py load_initial_data
Write-Host ""

# Collect static files
Write-Host "[INFO] Collecting static files..." -ForegroundColor Yellow
docker-compose exec -T web python manage.py collectstatic --noinput
Write-Host ""

# Create superuser
Write-Host "[INFO] Creating superuser..." -ForegroundColor Yellow
Write-Host "Please enter superuser credentials:" -ForegroundColor Cyan
docker-compose exec web python manage.py createsuperuser
Write-Host ""

# Show running containers
Write-Host "[INFO] Running containers:" -ForegroundColor Yellow
docker-compose ps
Write-Host ""

# Show application URLs
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Application URLs:" -ForegroundColor Cyan
Write-Host "   - API: http://localhost:8000/api/"
Write-Host "   - Admin Panel: http://localhost:8000/admin/"
Write-Host ""
Write-Host "API Endpoints:" -ForegroundColor Cyan
Write-Host "   - Authors: http://localhost:8000/api/authors/"
Write-Host "   - Books: http://localhost:8000/api/books/"
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "   - View logs: docker-compose logs -f"
Write-Host "   - Stop application: docker-compose down"
Write-Host "   - Restart application: docker-compose restart"
Write-Host "   - Run tests: docker-compose exec web python manage.py test"
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green