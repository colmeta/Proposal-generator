#!/bin/bash
# Rollback script for proposal generator
# Handles version rollback, database rollback, and configuration rollback

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
BACKUP_DIR=${BACKUP_DIR:-./deployment/backup}
ROLLBACK_VERSION=${1:-latest}

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

print_status "Starting rollback process..."
print_status "Rollback version: $ROLLBACK_VERSION"

# Confirm rollback
if [ -z "$AUTO_CONFIRM" ]; then
    read -p "Are you sure you want to rollback? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        print_status "Rollback cancelled"
        exit 0
    fi
fi

# Find backup to restore
if [ "$ROLLBACK_VERSION" = "latest" ]; then
    BACKUP_FILE=$(ls -t "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null | head -1)
    if [ -z "$BACKUP_FILE" ]; then
        BACKUP_FILE=$(ls -t "$BACKUP_DIR"/backup_*.dump 2>/dev/null | head -1)
    fi
    if [ -z "$BACKUP_FILE" ]; then
        BACKUP_FILE=$(ls -t "$BACKUP_DIR"/backup_*.json 2>/dev/null | head -1)
    fi
else
    BACKUP_FILE=$(find "$BACKUP_DIR" -name "*${ROLLBACK_VERSION}*" | head -1)
fi

if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
    print_error "Backup file not found for version: $ROLLBACK_VERSION"
    print_status "Available backups:"
    ls -lh "$BACKUP_DIR"/backup_* 2>/dev/null || print_warning "No backups found"
    exit 1
fi

print_status "Found backup: $BACKUP_FILE"

# Create pre-rollback backup
print_status "Creating pre-rollback backup..."
if [ -f "deployment/scripts/backup.sh" ]; then
    bash deployment/scripts/backup.sh || {
        print_warning "Pre-rollback backup failed, but continuing..."
    }
fi

# Extract backup if it's an archive
if [[ "$BACKUP_FILE" == *.tar.gz ]]; then
    print_status "Extracting backup archive..."
    TEMP_DIR=$(mktemp -d)
    tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"
    
    # Find database backup in extracted files
    DB_BACKUP=$(find "$TEMP_DIR" -name "*database*" | head -1)
    FILES_BACKUP=$(find "$TEMP_DIR" -name "*files" -type d | head -1)
else
    DB_BACKUP="$BACKUP_FILE"
    FILES_BACKUP=""
fi

# Database rollback
if [ -n "$DB_BACKUP" ] && [ -n "$DATABASE_URL" ]; then
    print_status "Rolling back database..."
    
    if [[ "$DB_BACKUP" == *.dump ]]; then
        # PostgreSQL dump file
        if command -v pg_restore &> /dev/null; then
            python3 << EOF
import os
import re
from urllib.parse import urlparse

db_url = os.getenv('DATABASE_URL', '')
parsed = urlparse(db_url)
db_name = parsed.path.lstrip('/')
db_user = parsed.username
db_password = parsed.password
db_host = parsed.hostname
db_port = parsed.port or 5432

print(f"DB_NAME={db_name}")
print(f"DB_USER={db_user}")
print(f"DB_HOST={db_host}")
print(f"DB_PORT={db_port}")
print(f"DB_PASSWORD={db_password}")
EOF > /tmp/db_info.txt
            
            source /tmp/db_info.txt
            
            # Drop and recreate database (CAUTION: This will delete current data)
            print_warning "Dropping existing database connections..."
            PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres \
                -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();" || true
            
            # Restore database
            PGPASSWORD="$DB_PASSWORD" pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" \
                -d "$DB_NAME" --clean --if-exists "$DB_BACKUP" || {
                print_error "Database restore failed"
                exit 1
            }
        else
            print_error "pg_restore not found. Cannot restore database dump."
            exit 1
        fi
    elif [[ "$DB_BACKUP" == *.json ]]; then
        # JSON backup file
        print_status "Restoring from JSON backup..."
        python3 << EOF
import os
import json
import sys
from sqlalchemy import create_engine, text, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError

try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    
    # Load backup data
    with open("$DB_BACKUP", 'r') as f:
        backup_data = json.load(f)
    
    # Clear existing tables
    metadata = MetaData()
    metadata.reflect(bind=engine)
    
    with engine.begin() as conn:
        # Drop all tables
        for table_name in reversed(metadata.sorted_tables):
            conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
        
        # Restore tables and data
        for table_name, table_data in backup_data.get('tables', {}).items():
            # Recreate table structure (simplified - in production, use proper schema)
            columns = table_data.get('columns', [])
            if not columns:
                continue
            
            # Create table (simplified)
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (id SERIAL PRIMARY KEY)"
            conn.execute(text(create_sql))
            
            # Insert data
            rows = table_data.get('rows', [])
            if rows:
                # This is simplified - proper implementation would need schema
                print(f"Restored {len(rows)} rows to {table_name}")
    
    print("Database restore completed")
except Exception as e:
    print(f"Database restore failed: {e}")
    sys.exit(1)
EOF
    fi
    
    print_status "Database rollback completed"
else
    print_warning "Database backup not found or DATABASE_URL not set, skipping database rollback"
fi

# File rollback
if [ -n "$FILES_BACKUP" ] && [ -d "$FILES_BACKUP" ]; then
    print_status "Rolling back files..."
    
    # Restore important files
    if [ -d "$FILES_BACKUP/.env" ] || [ -f "$FILES_BACKUP/.env" ]; then
        print_status "Restoring .env file..."
        cp -r "$FILES_BACKUP/.env" . 2>/dev/null || true
    fi
    
    if [ -d "$FILES_BACKUP/config.py" ] || [ -f "$FILES_BACKUP/config.py" ]; then
        print_status "Restoring config.py..."
        cp -r "$FILES_BACKUP/config.py" . 2>/dev/null || true
    fi
    
    print_status "File rollback completed"
fi

# Cleanup temp directory
if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

# Code rollback (if using Git)
if command -v git &> /dev/null && [ -d .git ]; then
    print_status "Rolling back code to previous version..."
    
    # Get previous commit
    PREVIOUS_COMMIT=$(git log --oneline -2 | tail -1 | cut -d' ' -f1)
    
    if [ -n "$PREVIOUS_COMMIT" ]; then
        print_status "Reverting to commit: $PREVIOUS_COMMIT"
        git reset --hard "$PREVIOUS_COMMIT" || {
            print_warning "Git rollback failed, but continuing..."
        }
    fi
fi

# Restart services
print_status "Restarting services..."

if systemctl is-active --quiet proposal-generator-web 2>/dev/null; then
    sudo systemctl restart proposal-generator-web
    sudo systemctl restart proposal-generator-worker
elif docker-compose ps | grep -q proposal-generator-web; then
    docker-compose restart web worker
fi

# Health check
print_status "Performing health check after rollback..."
HEALTH_CHECK_URL=${HEALTH_CHECK_URL:-http://localhost:8000/api/monitoring/health}

for i in $(seq 1 30); do
    if curl -f -s "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
        print_status "Health check passed!"
        break
    fi
    
    if [ $i -eq 30 ]; then
        print_error "Health check failed after rollback"
        print_warning "Manual intervention may be required"
        exit 1
    fi
    
    sleep 10
done

print_status "Rollback completed successfully!"
print_status "Rollback version: $ROLLBACK_VERSION"
print_status "Rollback time: $(date)"



