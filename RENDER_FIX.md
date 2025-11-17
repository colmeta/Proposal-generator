# Render Deployment Fix - Gunicorn Issue

## 🔧 Quick Fix

The error `gunicorn: command not found` means gunicorn isn't installed. Here's how to fix it:

### Option 1: Use Alternative Start Command (Quickest)

In Render dashboard, change the **Start Command** to:

```bash
python -m api.endpoints
```

This uses Flask's built-in server (works for free tier).

### Option 2: Ensure Gunicorn is Installed (Recommended for Production)

1. **Verify requirements.txt includes gunicorn**:
   - It should have: `gunicorn>=21.2.0`
   - If not, add it and push to GitHub

2. **Rebuild the service**:
   - Render will reinstall dependencies
   - Gunicorn should now be available

3. **Use this Start Command**:
```bash
gunicorn api.endpoints:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

## 📝 Updated Start Commands

### For Free Tier (Recommended):
```bash
python -m api.endpoints
```

### For Production (with gunicorn):
```bash
gunicorn api.endpoints:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

## ✅ Steps to Fix Now

1. Go to Render Dashboard → Your Web Service
2. Click **Settings**
3. Scroll to **Start Command**
4. Change to: `python -m api.endpoints`
5. Click **Save Changes**
6. Service will automatically redeploy

## 🎯 Why This Happened

- Gunicorn wasn't in requirements.txt initially
- Now it's added, but you need to either:
  - Use the alternative command (immediate fix)
  - OR rebuild after requirements.txt update (takes a few minutes)

## ✅ Verification

After deployment, check:
- Health endpoint: `https://your-service.onrender.com/api/health`
- Should return: `{"status": "healthy", "service": "proposal-generator-api"}`

