"""
Application settings and configuration
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = BASE_DIR / "storage"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, STORAGE_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/proposals.db")

# Email configuration
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@proposal-generator.com")

# Storage
USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
S3_BUCKET = os.getenv("S3_BUCKET", "")

# Background processing
BACKGROUND_PROCESSING_ENABLED = os.getenv("BACKGROUND_PROCESSING_ENABLED", "true").lower() == "true"
TASK_TIMEOUT = int(os.getenv("TASK_TIMEOUT", "3600"))  # 1 hour

# Quality thresholds
MIN_QUALITY_SCORE = float(os.getenv("MIN_QUALITY_SCORE", "9.5"))
CEO_APPROVAL_REQUIRED = os.getenv("CEO_APPROVAL_REQUIRED", "true").lower() == "true"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "app.log"

# Render deployment
RENDER = os.getenv("RENDER", "false").lower() == "true"
PORT = int(os.getenv("PORT", "8000"))

