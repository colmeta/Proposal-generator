# Render Free Tier - Port Binding Fix & Background Worker Alternative

## 🔧 Port Binding Issue Fix

The service isn't binding to the port correctly. Here's the fix:

### Problem:
- Gunicorn command runs but no port detected
- Service times out waiting for port

### Solution:

**Option 1: Use Python directly (Recommended for Free Tier)**

In Render dashboard, change **Start Command** to:

```bash
python -m api.endpoints
```

This uses Flask's built-in server which works perfectly on free tier.

**Option 2: Fix Gunicorn (If you want to use it)**

Make sure gunicorn is installed (it is in requirements.txt). The start command should be:

```bash
gunicorn api.endpoints:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --access-logfile - --error-logfile -
```

**Note**: Use `--workers 1` on free tier (not 2) to save resources.

## 🆓 Background Worker Alternative (Free Tier)

Since background workers are paid on Render, here's a free alternative:

### Solution: Inline Background Processing

The background processor now runs **inside the web service** instead of a separate worker. This works on free tier!

**How it works:**
- Background tasks run in the same process as the web service
- Uses APScheduler (already installed)
- No separate worker needed
- Works perfectly on free tier

**Configuration:**

In Render environment variables, set:
```bash
BACKGROUND_PROCESSING_ENABLED=true
```

The code automatically handles this - if background processing is enabled, it starts in the same process.

## ✅ Updated Render Settings

### Web Service Configuration:

**Name**: `proposal-generator-api`

**Build Command**:
```bash
pip install -r requirements.txt
```

**Start Command** (Choose one):

**Option A - Python (Recommended)**:
```bash
python -m api.endpoints
```

**Option B - Gunicorn**:
```bash
gunicorn api.endpoints:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

**Environment Variables**:
```bash
# Database
DATABASE_URL=<your-internal-database-url>

# LLM API Keys (at least one)
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-ant-...
# OR
GEMINI_API_KEY=...
# OR
GROQ_API_KEY=gsk_...

# Security
ENCRYPTION_KEY=<generate-with-python-command>
JWT_SECRET_KEY=<random-32-char-string>

# Application
LOG_LEVEL=INFO
RENDER=true
PORT=10000

# Background Processing (runs in same process - FREE!)
BACKGROUND_PROCESSING_ENABLED=true
TASK_TIMEOUT=3600

# Quality
MIN_QUALITY_SCORE=9.5
CEO_APPROVAL_REQUIRED=true
```

## 🎯 Why This Works

1. **Port Binding**: Flask app now properly binds to `0.0.0.0:$PORT`
2. **Background Processing**: Runs in same process (free tier compatible)
3. **No Separate Worker**: Everything in one service (free tier)
4. **Resource Efficient**: Uses minimal resources

## 📝 Quick Fix Steps

1. Go to Render Dashboard → Your Web Service
2. Click **Settings**
3. Change **Start Command** to: `python -m api.endpoints`
4. Make sure **PORT** environment variable is set (Render sets this automatically)
5. Click **Save Changes**
6. Service will redeploy

## ✅ Verification

After deployment:
- Health check: `https://your-service.onrender.com/api/health`
- Should return: `{"status": "healthy", "service": "proposal-generator-api"}`

## 🎉 Result

- ✅ Port binding fixed
- ✅ Background processing works (in same process)
- ✅ No paid worker needed
- ✅ Everything works on free tier!

