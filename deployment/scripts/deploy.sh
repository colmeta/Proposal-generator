#!/bin/bash
# Deployment script for proposal generator
# Performs pre-deployment checks, migrations, and service restart

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${ENVIRONMENT:-production}
BACKUP_BEFORE_DEPLOY=${BACKUP_BEFORE_DEPLOY:-true}
RUN_MIGRATIONS=${RUN_MIGRATIONS:-true}
HEALTH_CHECK_TIMEOUT=${HEALTH_CHECK_TIMEOUT:-300}

echo -e "${GREEN}Starting deployment for environment: ${ENVIRONMENT}${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Pre-deployment checks
print_status "Running pre-deployment checks..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

# Check if required environment variables are set
if [ -z "$DATABASE_URL" ]; then
    print_error "DATABASE_URL environment variable is not set"
    exit 1
fi

# Check database connectivity
print_status "Checking database connectivity..."
python3 -c "
import os
import sys
from sqlalchemy import create_engine, text

try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
" || {
    print_error "Database connection check failed"
    exit 1
}

# Backup before deployment (if enabled)
if [ "$BACKUP_BEFORE_DEPLOY" = "true" ]; then
    print_status "Creating backup before deployment..."
    if [ -f "deployment/scripts/backup.sh" ]; then
        bash deployment/scripts/backup.sh || {
            print_warning "Backup failed, but continuing deployment..."
        }
    else
        print_warning "Backup script not found, skipping backup"
    fi
fi

# Install/update dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt --upgrade || {
    print_error "Failed to install dependencies"
    exit 1
}

# Run database migrations (if enabled)
if [ "$RUN_MIGRATIONS" = "true" ]; then
    print_status "Running database migrations..."
    
    # Check if alembic is available
    if command -v alembic &> /dev/null; then
        alembic upgrade head || {
            print_error "Database migration failed"
            exit 1
        }
    else
        print_warning "Alembic not found, skipping migrations"
    fi
fi

# Run tests (optional, can be skipped in production)
if [ "$RUN_TESTS" = "true" ] && [ "$ENVIRONMENT" != "production" ]; then
    print_status "Running tests..."
    pytest tests/ -v --tb=short || {
        print_warning "Some tests failed, but continuing deployment..."
    }
fi

# Restart services (implementation depends on deployment platform)
print_status "Restarting services..."

# For systemd
if systemctl is-active --quiet proposal-generator-web 2>/dev/null; then
    print_status "Restarting systemd service..."
    sudo systemctl restart proposal-generator-web || {
        print_error "Failed to restart web service"
        exit 1
    }
    sudo systemctl restart proposal-generator-worker || {
        print_error "Failed to restart worker service"
        exit 1
    }
# For Docker Compose
elif docker-compose ps | grep -q proposal-generator-web; then
    print_status "Restarting Docker Compose services..."
    docker-compose restart web worker || {
        print_error "Failed to restart Docker services"
        exit 1
    }
# For Render/other platforms, services auto-restart on deploy
else
    print_status "Services will restart automatically on deployment platform"
fi

# Health check
print_status "Performing health check..."
HEALTH_CHECK_URL=${HEALTH_CHECK_URL:-http://localhost:8000/api/monitoring/health}

for i in $(seq 1 30); do
    if curl -f -s "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
        print_status "Health check passed!"
        break
    fi
    
    if [ $i -eq 30 ]; then
        print_error "Health check failed after 30 attempts"
        print_warning "Consider rolling back the deployment"
        exit 1
    fi
    
    print_status "Health check attempt $i/30 failed, retrying in 10 seconds..."
    sleep 10
done

# Post-deployment verification
print_status "Running post-deployment verification..."

# Check if services are running
python3 -c "
import requests
import sys

try:
    response = requests.get('$HEALTH_CHECK_URL', timeout=10)
    if response.status_code == 200:
        print('Service is healthy')
        sys.exit(0)
    else:
        print(f'Service returned status code: {response.status_code}')
        sys.exit(1)
except Exception as e:
    print(f'Health check failed: {e}')
    sys.exit(1)
" || {
    print_error "Post-deployment verification failed"
    exit 1
}

print_status "Deployment completed successfully!"
print_status "Environment: ${ENVIRONMENT}"
print_status "Deployment time: $(date)"

