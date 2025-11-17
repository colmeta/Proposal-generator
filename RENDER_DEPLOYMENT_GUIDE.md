# Render Deployment Guide - Free Tier

## 🚀 Complete Setup Instructions

### Step 1: Push to GitHub

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: AI Consultancy Multi-Agent System"

# Add remote (replace with your actual repo)
git remote add origin https://github.com/colmeta/proposal_generator.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub (recommended)
3. Connect your GitHub account
4. Authorize Render to access your repositories

### Step 3: Create PostgreSQL Database (Free Tier)

1. In Render Dashboard, click **New +** → **PostgreSQL**
2. Configure:
   - **Name**: `proposal-generator-db`
   - **Database**: `proposals`
   - **User**: `proposal_user` (auto-generated)
   - **Region**: Choose closest to you
   - **PostgreSQL Version**: 15 (or latest)
   - **Plan**: Free
3. Click **Create Database**
4. **IMPORTANT**: Copy the **Internal Database URL** (you'll need it)

### Step 4: Create Web Service

1. In Render Dashboard, click **New +** → **Web Service**
2. Connect your GitHub repository: `colmeta/proposal_generator`
3. Configure:

#### Basic Settings:
- **Name**: `proposal-generator-api`
- **Region**: Same as database
- **Branch**: `main`
- **Root Directory**: (leave empty)
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  python -m api.endpoints
  ```
  **Note**: This is the recommended command for free tier. It works perfectly and uses fewer resources.
  
  (Optional: If you want to use gunicorn instead, use: `gunicorn api.endpoints:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`)

#### Environment Variables:
Add these in the **Environment** section:

```bash
# Database
DATABASE_URL=<Internal Database URL from Step 3>

# LLM API Keys (at least one required)
OPENAI_API_KEY=sk-your-openai-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
# OR
GEMINI_API_KEY=your-gemini-key-here
# OR
GROQ_API_KEY=gsk_your-groq-key-here

# Security (IMPORTANT - Generate these!)
ENCRYPTION_KEY=<Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
JWT_SECRET_KEY=<Generate a random string, e.g., openssl rand -hex 32>

# Application Settings
LOG_LEVEL=INFO
RENDER=true
PORT=10000

# Email (Optional - for notifications)
EMAIL_ENABLED=false
# If enabling email:
# SENDGRID_API_KEY=your-sendgrid-key
# FROM_EMAIL=noreply@yourdomain.com

# Storage (Optional - for file uploads)
USE_S3=false
# If using S3:
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret
# S3_BUCKET=your-bucket-name

# Quality Settings
MIN_QUALITY_SCORE=9.5
CEO_APPROVAL_REQUIRED=true

# Background Processing
BACKGROUND_PROCESSING_ENABLED=true
TASK_TIMEOUT=3600
```

#### Advanced Settings:
- **Auto-Deploy**: Yes
- **Health Check Path**: `/api/health`
- **Plan**: Free

4. Click **Create Web Service**

### Step 5: Create Background Worker (Optional but Recommended)

1. In Render Dashboard, click **New +** → **Background Worker**
2. Connect same repository: `colmeta/proposal_generator`
3. Configure:

#### Basic Settings:
- **Name**: `proposal-generator-worker`
- **Region**: Same as web service
- **Branch**: `main`
- **Root Directory**: (leave empty)
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  python -m workers.task_worker
  ```

#### Environment Variables:
Copy ALL the same environment variables from Step 4.

4. Click **Create Background Worker**

### Step 6: Initialize Database

After services are deployed:

1. Go to your Web Service in Render
2. Click **Shell** tab
3. Run:
   ```bash
   python -c "from database.db import init_db; init_db()"
   ```
   OR if using Alembic:
   ```bash
   alembic upgrade head
   ```

### Step 7: Verify Deployment

1. **Check Web Service**:
   - Visit: `https://proposal-generator-api.onrender.com/api/health`
   - Should return: `{"status": "healthy", "service": "proposal-generator-api"}`

2. **Check Background Worker**:
   - Check logs in Render dashboard
   - Should show: "Background processor started"

3. **Test API**:
   ```bash
   curl https://proposal-generator-api.onrender.com/api/health
   ```

### Step 8: Set Up Keep-Alive (Prevent Sleeping)

#### Option A: GitHub Actions (Already Set Up)
1. Go to GitHub repo → Settings → Secrets
2. Add secret: `RENDER_SERVICE_URL` = `https://proposal-generator-api.onrender.com`
3. Workflow will run automatically every 5 minutes

#### Option B: UptimeRobot (Free, Recommended)
1. Sign up at https://uptimerobot.com
2. Add monitor:
   - Type: HTTP(s)
   - URL: `https://proposal-generator-api.onrender.com/api/health`
   - Interval: 5 minutes
3. This keeps service alive for free!

## 🔑 Generating Security Keys

### Encryption Key:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### JWT Secret Key:
```bash
# On Linux/Mac:
openssl rand -hex 32

# On Windows (PowerShell):
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

## 📋 Pre-Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] PostgreSQL database created
- [ ] Web service created with all environment variables
- [ ] Background worker created (optional)
- [ ] Database initialized
- [ ] Health check working
- [ ] Keep-alive service configured
- [ ] At least one LLM API key configured

## 🐛 Troubleshooting

### Service Not Starting:
- Check logs in Render dashboard
- Verify all environment variables are set
- Check build command completed successfully

### Database Connection Issues:
- Use **Internal Database URL** (not external)
- Verify database is in same region
- Check database is running

### API Not Responding:
- Check health endpoint: `/api/health`
- Verify PORT environment variable
- Check service logs for errors

### Background Jobs Not Working:
- Verify background worker is running
- Check APScheduler is starting
- Verify database connection in worker

## ✅ Success Indicators

When everything is working:
- ✅ Health endpoint returns 200
- ✅ Database migrations completed
- ✅ Background worker logs show "started"
- ✅ Can create a test job via API
- ✅ Service stays awake (doesn't sleep)

## 🎉 You're Done!

Your platform is now live and ready to generate proposals!

**Service URL**: `https://proposal-generator-api.onrender.com`
**API Docs**: `https://proposal-generator-api.onrender.com/api/docs` (if Swagger enabled)

