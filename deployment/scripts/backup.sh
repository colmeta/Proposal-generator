#!/bin/bash
# Backup script for proposal generator
# Handles database backups, file backups, and backup rotation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
BACKUP_DIR=${BACKUP_DIR:-./deployment/backup}
RETENTION_DAYS=${RETENTION_DAYS:-30}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PREFIX="backup_${TIMESTAMP}"

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

# Create backup directory
mkdir -p "$BACKUP_DIR"

print_status "Starting backup process..."
print_status "Backup directory: $BACKUP_DIR"
print_status "Retention days: $RETENTION_DAYS"

# Database backup
if [ -n "$DATABASE_URL" ]; then
    print_status "Backing up database..."
    
    DB_BACKUP_FILE="${BACKUP_DIR}/${BACKUP_PREFIX}_database.sql"
    
    # Extract database connection details
    python3 << EOF
import os
import re
from urllib.parse import urlparse

db_url = os.getenv('DATABASE_URL', '')
if not db_url:
    print('DATABASE_URL not set')
    exit(1)

# Parse database URL
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
    
    # Perform database backup using pg_dump
    if command -v pg_dump &> /dev/null; then
        PGPASSWORD="$DB_PASSWORD" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
            --no-owner --no-acl -F c -f "${DB_BACKUP_FILE}.dump" || {
            print_error "Database backup failed"
            exit 1
        }
        print_status "Database backup completed: ${DB_BACKUP_FILE}.dump"
    else
        # Fallback to Python-based backup
        print_status "Using Python-based database backup..."
        python3 << EOF
import os
import sys
from sqlalchemy import create_engine, text
import json
from datetime import datetime

try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    
    # Get all table names
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in result]
    
    backup_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'tables': {}
    }
    
    # Backup each table
    for table in tables:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table}"))
            columns = result.keys()
            rows = [dict(row) for row in result]
            backup_data['tables'][table] = {
                'columns': list(columns),
                'rows': rows
            }
    
    # Save backup
    backup_file = "${DB_BACKUP_FILE}.json"
    with open(backup_file, 'w') as f:
        json.dump(backup_data, f, indent=2, default=str)
    
    print(f"Database backup completed: {backup_file}")
except Exception as e:
    print(f"Database backup failed: {e}")
    sys.exit(1)
EOF
    fi
else
    print_warning "DATABASE_URL not set, skipping database backup"
fi

# File backup (important files and configurations)
print_status "Backing up important files..."

FILES_BACKUP_DIR="${BACKUP_DIR}/${BACKUP_PREFIX}_files"
mkdir -p "$FILES_BACKUP_DIR"

# Backup important directories
BACKUP_PATHS=(
    "config.py"
    ".env"
    "logs"
    "data"
)

for path in "${BACKUP_PATHS[@]}"; do
    if [ -e "$path" ]; then
        print_status "Backing up: $path"
        cp -r "$path" "$FILES_BACKUP_DIR/" 2>/dev/null || {
            print_warning "Failed to backup $path"
        }
    fi
done

# Create backup archive
print_status "Creating backup archive..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_PREFIX}.tar.gz" \
    "${BACKUP_PREFIX}_database"* \
    "${BACKUP_PREFIX}_files" 2>/dev/null || {
    print_warning "Failed to create backup archive"
}

# Clean up individual files if archive was created
if [ -f "${BACKUP_PREFIX}.tar.gz" ]; then
    rm -rf "${BACKUP_PREFIX}_database"* "${BACKUP_PREFIX}_files"
    print_status "Backup archive created: ${BACKUP_PREFIX}.tar.gz"
fi

# Backup verification
print_status "Verifying backup..."
if [ -f "${BACKUP_DIR}/${BACKUP_PREFIX}.tar.gz" ] || [ -f "${DB_BACKUP_FILE}.dump" ] || [ -f "${DB_BACKUP_FILE}.json" ]; then
    BACKUP_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_PREFIX}"* 2>/dev/null | tail -1 | cut -f1)
    print_status "Backup verified. Size: $BACKUP_SIZE"
else
    print_error "Backup verification failed - backup file not found"
    exit 1
fi

# Backup rotation (remove old backups)
print_status "Rotating old backups..."
find "$BACKUP_DIR" -name "backup_*.tar.gz" -o -name "backup_*.dump" -o -name "backup_*.json" | \
    while read backup; do
        backup_age=$(find "$backup" -mtime +$RETENTION_DAYS)
        if [ -n "$backup_age" ]; then
            print_status "Removing old backup: $(basename $backup)"
            rm -f "$backup"
        fi
    done

# List current backups
print_status "Current backups:"
ls -lh "$BACKUP_DIR"/backup_* 2>/dev/null | tail -5 || print_warning "No backups found"

print_status "Backup process completed successfully!"
print_status "Backup location: $BACKUP_DIR"
print_status "Backup timestamp: $TIMESTAMP"


