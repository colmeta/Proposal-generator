# GitHub Actions Workflows

## Keep-Alive Workflow

### Purpose
Keeps Render free tier services from sleeping by pinging them every 5 minutes (12 times per hour).

### Setup Instructions

1. **Add GitHub Secrets:**
   - Go to your GitHub repository
   - Navigate to: Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `RENDER_SERVICE_URL`: Your Render service URL (e.g., `https://your-app.onrender.com`)
     - `RENDER_WORKER_URL`: (Optional) Your background worker URL if separate

2. **Enable the Workflow:**
   - The workflow is already set up in `.github/workflows/keep-alive.yml`
   - It will automatically run every 5 minutes
   - You can also manually trigger it from the Actions tab

3. **Verify it's Working:**
   - Go to Actions tab in GitHub
   - You should see "Keep Render Service Alive" running every 5 minutes
   - Check the logs to confirm successful pings

### How It Works

- Runs on a cron schedule: `*/5 * * * *` (every 5 minutes)
- Pings your Render service health endpoint: `/api/health`
- If health check fails, tries the root endpoint to wake up the service
- Keeps the service active 24/7

### Notes

- GitHub Actions free tier allows 2000 minutes/month
- This workflow uses ~2 minutes/hour = ~48 minutes/day = ~1440 minutes/month
- Well within free tier limits ✅

### Alternative: Simple Version

If you prefer a simpler version, use `keep-alive.yml`. For more detailed logging and error handling, use `keep-alive-advanced.yml`.

