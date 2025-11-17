# Render Deployment Settings - Complete Configuration

## 🚀 Quick Setup Guide

### Step 1: Create PostgreSQL Database

**Service Type**: PostgreSQL  
**Name**: `proposal-generator-db`  
**Database**: `proposals`  
**Plan**: Free  
**Region**: Choose closest to you

**After Creation**: Copy the **Internal Database URL** (starts with `postgresql://`)

---

### Step 2: Create Web Service

**Service Type**: Web Service  
**Name**: `proposal-generator-api`  
**Repository**: `colmeta/proposal_generator`  
**Branch**: `main`  
**Root Directory**: (leave empty)  
**Runtime**: `Python 3`  
**Plan**: Free

#### Build Command:
```bash
pip install -r requirements.txt
```

#### Start Command:

**RECOMMENDED for Free Tier** (Use this):
```bash
python run.py
```

**Alternative** (also works):
```bash
python -m api.endpoints
```

**Alternative** (If you want to use gunicorn - requires more resources):
```bash
gunicorn api.endpoints:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

**Note**: 
- For **free tier**, use `python -m api.endpoints` (simpler, works perfectly)
- Gunicorn is optional and uses more resources
- Both work, but Python is recommended for free tier

#### Environment Variables:

Copy and paste these into Render's Environment section:

```bash
# ============================================
# DATABASE (REQUIRED)
# ============================================
DATABASE_URL=<PASTE_INTERNAL_DATABASE_URL_FROM_STEP_1>

# ============================================
# LLM API KEYS (At least ONE required)
# ============================================
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-openai-key-here

# OR Get from: https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# OR Get from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-gemini-key-here

# OR Get from: https://console.groq.com/keys
GROQ_API_KEY=gsk_your-groq-key-here

# ============================================
# SECURITY (REQUIRED - Generate these!)
# ============================================
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY=<GENERATE_AND_PASTE_HERE>

# Generate random string (32+ characters)
JWT_SECRET_KEY=<GENERATE_RANDOM_STRING_HERE>

# ============================================
# APPLICATION SETTINGS
# ============================================
LOG_LEVEL=INFO
RENDER=true
PORT=10000

# ============================================
# EMAIL (Optional)
# ============================================
EMAIL_ENABLED=false
# If enabling:
# SENDGRID_API_KEY=your-sendgrid-key
# FROM_EMAIL=noreply@yourdomain.com

# ============================================
# STORAGE (Optional - for file uploads)
# ============================================
USE_S3=false
# If using S3:
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret
# S3_BUCKET=your-bucket-name

# ============================================
# QUALITY SETTINGS
# ============================================
MIN_QUALITY_SCORE=9.5
CEO_APPROVAL_REQUIRED=true

# ============================================
# BACKGROUND PROCESSING
# ============================================
BACKGROUND_PROCESSING_ENABLED=true
TASK_TIMEOUT=3600
```

#### Advanced Settings:
- **Auto-Deploy**: Yes
- **Health Check Path**: `/api/health`
- **Plan**: Free

---

### Step 3: Create Background Worker (Optional but Recommended)

**Service Type**: Background Worker  
**Name**: `proposal-generator-worker`  
**Repository**: `colmeta/proposal_generator`  
**Branch**: `main`  
**Root Directory**: (leave empty)  
**Runtime**: `Python 3`  
**Plan**: Free

#### Build Command:
```bash
pip install -r requirements.txt
```

#### Start Command:
```bash
python -m workers.task_worker
```

#### Environment Variables:
Copy **ALL the same environment variables** from Step 2.

---

### Step 4: Initialize Database

After services are deployed:

1. Go to Web Service → **Shell** tab
2. Run:
```bash
python -c "from database.db import init_db; init_db()"
```

---

### Step 5: Set Up Keep-Alive

#### Option A: GitHub Actions (Already Configured)
1. Go to GitHub repo: `colmeta/proposal_generator`
2. Settings → Secrets and variables → Actions
3. Add secret: `RENDER_SERVICE_URL` = `https://proposal-generator-api.onrender.com`
4. Workflow runs automatically every 5 minutes

#### Option B: UptimeRobot (Free, Recommended)
1. Sign up: https://uptimerobot.com
2. Add monitor:
   - Type: HTTP(s)
   - URL: `https://proposal-generator-api.onrender.com/api/health`
   - Interval: 5 minutes
3. Free forever!

---

## 🔑 Generating Security Keys

### Encryption Key:
Run this locally:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Copy the output to `ENCRYPTION_KEY`

### JWT Secret Key:
Generate a random 32+ character string:
```bash
# Linux/Mac:
openssl rand -hex 32

# Windows PowerShell:
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```
Copy to `JWT_SECRET_KEY`

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Web service health check: `https://proposal-generator-api.onrender.com/api/health` returns 200
- [ ] Database initialized (check logs)
- [ ] Background worker running (check logs)
- [ ] Keep-alive service configured
- [ ] Can create a test job via API

---

## 📝 API Endpoints Available

Once deployed, these endpoints are available:

- `GET /api/health` - Health check
- `POST /api/jobs` - Create job
- `GET /api/jobs/<id>` - Get job status
- `GET /api/jobs/<id>/result` - Get job result
- `POST /api/jobs/<id>/cancel` - Cancel job
- `GET /api/jobs` - List all jobs
- `POST /api/documents/upload` - Upload document (PDF, DOCX, images)
- `POST /api/documents/upload-urls` - Scrape URLs (websites, social media)
- `POST /api/proposals/generate-auto` - Auto-generate proposal from knowledge base
- `POST /api/knowledge-base/search` - Search knowledge base

---

## 🎉 You're Ready!

Your platform is now live and ready to:
- ✅ Upload documents (PDFs, images, DOCX)
- ✅ Scrape websites and social media
- ✅ Auto-generate proposals from knowledge base
- ✅ Research any funder
- ✅ Generate professional proposals

**Service URL**: `https://proposal-generator-api.onrender.com`

