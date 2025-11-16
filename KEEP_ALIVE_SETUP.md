# Keep-Alive Setup Guide

## 🎯 Purpose

Keep your Render free tier service from sleeping by pinging it every 5 minutes (12 times per hour).

## 📋 Setup Steps

### 1. Add GitHub Secret

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add:
   - **Name**: `RENDER_SERVICE_URL`
   - **Value**: Your Render service URL (e.g., `https://your-app.onrender.com`)
5. Click **Add secret**

### 2. (Optional) Add Worker URL

If you have a separate background worker service:
- **Name**: `RENDER_WORKER_URL`
- **Value**: Your worker service URL

### 3. Enable the Workflow

The workflow file is already created at:
```
.github/workflows/keep-alive.yml
```

It will automatically:
- ✅ Run every 5 minutes (12 times/hour)
- ✅ Ping your `/api/health` endpoint
- ✅ Keep your service active 24/7

### 4. Verify It's Working

1. Go to **Actions** tab in GitHub
2. You should see "Keep Render Service Alive" workflow
3. It will run automatically every 5 minutes
4. Check the logs to see successful pings

## ⏰ Schedule

The workflow runs at these times every hour:
- :00, :05, :10, :15, :20, :25, :30, :35, :40, :45, :50, :55

## 📊 GitHub Actions Usage

- **Runs per day**: 288 (12 × 24)
- **Minutes per run**: ~1-2 minutes
- **Total minutes/day**: ~288-576 minutes
- **GitHub Free Tier**: 2000 minutes/month
- **Usage**: ~8,640-17,280 minutes/month

⚠️ **Note**: This exceeds GitHub free tier (2000 min/month). Consider:
- Using a paid GitHub plan
- Reducing frequency to every 10 minutes (6 times/hour)
- Using an external service like UptimeRobot (free tier: 50 monitors)

## 🔄 Alternative: Every 10 Minutes

If you want to reduce GitHub Actions usage, change the cron schedule:

```yaml
# Every 10 minutes (6 times per hour)
- cron: '*/10 * * * *'
```

## 🆓 Free Alternative: UptimeRobot

For a completely free solution:

1. Sign up at https://uptimerobot.com (free tier: 50 monitors)
2. Add a new monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://your-app.onrender.com/api/health`
   - **Interval**: 5 minutes
3. This will ping your service every 5 minutes for free!

## ✅ Verification

After setup, your service should:
- ✅ Never sleep
- ✅ Always respond quickly
- ✅ Stay active 24/7

## 🐛 Troubleshooting

**Workflow not running?**
- Check if Actions are enabled in repository settings
- Verify the workflow file is in `.github/workflows/`

**Service still sleeping?**
- Verify the URL in secrets is correct
- Check if `/api/health` endpoint exists
- Try manually triggering the workflow

**GitHub Actions quota exceeded?**
- Switch to UptimeRobot (free)
- Or reduce frequency to every 10 minutes

