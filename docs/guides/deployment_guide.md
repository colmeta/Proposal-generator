# Deployment Guide

Complete guide for deploying the Proposal Generator to production.

## Overview

This guide covers deploying the Proposal Generator to various platforms and environments.

## Prerequisites

- Production server or cloud platform
- Domain name (optional but recommended)
- SSL certificate (required for HTTPS)
- Database (PostgreSQL recommended)
- API keys for LLM providers

## Deployment Options

### Option 1: Docker Deployment

#### Build Docker Image

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000 8501

CMD ["python", "-m", "api.main"]
```

#### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/proposals
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
  
  web:
    build: .
    command: streamlit run web/app.py --server.port 8501
    ports:
      - "8501:8501"
    environment:
      - API_BASE_URL=http://api:5000/api
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=proposals
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### Deploy

```bash
docker-compose up -d
```

### Option 2: Cloud Platform Deployment

#### Heroku

1. **Create Procfile**:
```
web: python -m api.main
streamlit: streamlit run web/app.py --server.port=$PORT
```

2. **Deploy**:
```bash
heroku create proposal-generator
heroku addons:create heroku-postgresql
git push heroku main
```

#### AWS EC2

1. **Launch EC2 Instance**
2. **Install Dependencies**:
```bash
sudo apt update
sudo apt install python3-pip postgresql
pip3 install -r requirements.txt
```

3. **Configure Services**:
```bash
# Create systemd service for API
sudo nano /etc/systemd/system/proposal-api.service
```

4. **Start Services**:
```bash
sudo systemctl start proposal-api
sudo systemctl enable proposal-api
```

#### Google Cloud Platform

1. **Create App Engine Config**:
```yaml
runtime: python310

handlers:
- url: /.*
  script: auto
```

2. **Deploy**:
```bash
gcloud app deploy
```

### Option 3: Kubernetes Deployment

#### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: proposal-generator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: proposal-generator
  template:
    metadata:
      labels:
        app: proposal-generator
    spec:
      containers:
      - name: api
        image: proposal-generator:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

## Environment Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
SECRET_KEY=your-secret-key-here

# LLM Providers
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key

# Email
SENDGRID_API_KEY=your-key
FROM_EMAIL=noreply@example.com

# Storage
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-key
S3_BUCKET=your-bucket

# Security
ALLOWED_ORIGINS=https://yourdomain.com
JWT_SECRET_KEY=your-jwt-secret
```

### Security Settings

1. **Use HTTPS**: Always use HTTPS in production
2. **Secure Secrets**: Use secret management (AWS Secrets Manager, etc.)
3. **Environment Variables**: Never commit secrets to version control
4. **Firewall**: Configure firewall rules
5. **Rate Limiting**: Enable rate limiting

## Database Setup

### PostgreSQL

```bash
# Create database
createdb proposal_generator

# Run migrations
alembic upgrade head
```

### Backup Strategy

```bash
# Daily backup
pg_dump proposal_generator > backup_$(date +%Y%m%d).sql

# Restore
psql proposal_generator < backup_20240115.sql
```

## Monitoring

### Health Checks

```python
# Health check endpoint
@app.route('/health')
def health():
    return {
        'status': 'healthy',
        'database': check_database(),
        'storage': check_storage()
    }
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics

```python
from prometheus_client import Counter, Histogram

requests_total = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')
```

## Scaling

### Horizontal Scaling

- Use load balancer
- Deploy multiple API instances
- Use shared database
- Use shared storage (S3, etc.)

### Vertical Scaling

- Increase server resources
- Optimize database queries
- Use caching (Redis)
- Optimize code

## Backup and Recovery

### Backup Strategy

1. **Database**: Daily automated backups
2. **Documents**: Replicated storage (S3 with versioning)
3. **Configuration**: Version controlled
4. **Secrets**: Secure backup

### Recovery Plan

1. **Database**: Restore from backup
2. **Documents**: Restore from storage
3. **Configuration**: Deploy from version control
4. **Testing**: Regular recovery drills

## Maintenance

### Updates

1. **Plan Updates**: Schedule maintenance windows
2. **Test First**: Test in staging environment
3. **Backup**: Backup before updates
4. **Rollback Plan**: Have rollback procedure ready

### Monitoring

1. **Uptime**: Monitor service availability
2. **Performance**: Track response times
3. **Errors**: Monitor error rates
4. **Resources**: Monitor CPU, memory, disk

## Troubleshooting

### Common Issues

1. **Database Connection**: Check connection string
2. **API Keys**: Verify API keys are valid
3. **Storage**: Check storage permissions
4. **Network**: Verify firewall rules

### Logs

```bash
# View API logs
tail -f /var/log/proposal-api.log

# View database logs
tail -f /var/log/postgresql/postgresql.log
```

## Next Steps

- Review [Best Practices](best_practices.md)
- Check [Integration Guide](integration_guide.md)
- See [Troubleshooting Guide](../user_guide/troubleshooting.md)



