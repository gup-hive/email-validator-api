# Email Validator API - Render Deployment Guide

## Quick Deploy to Render

### Prerequisites
- GitHub account
- Email Validator API pushed to GitHub: `https://github.com/gup-hive/email-validator-api`

### Deployment Steps

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com/
   - Login with GitHub

2. **Create New Web Service**
   - Click "New" → "Web Service"
   - Connect GitHub repository
   - Select `gup-hive/email-validator-api`
   - Select "Python" as runtime

3. **Configure Build & Deploy**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free (to start) → Starter ($7/mo) later
   - **Region**: Oregon (us-west) or nearest to your users

4. **Set Environment Variables**
   - `FLASK_ENV` = `production`
   - `SECRET_KEY` = Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
   - `PYTHON_VERSION` = `3.9.0`

5. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy automatically
   - Wait ~2-5 minutes for deployment

6. **Get Your URL**
   - Render will provide a URL like: `https://email-validator-api.onrender.com`
   - Test with: `curl https://email-validator-api.onrender.com/health`

---

## Testing the Deployment

### Health Check
```bash
curl https://email-validator-api.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-04T...",
  "version": "1.0.0"
}
```

### Validate Email
```bash
curl -X POST https://email-validator-api.onrender.com/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "check_smtp": false}'
```

---

## Configuration

### Free Plan Limits
- 512 MB RAM
- 0.1 CPU
- 750 hours/month
- Sleeps after 15 min of inactivity

### Paid Plans (for production)
- Starter ($7/mo): 512 MB RAM, 0.5 CPU, always on
- Standard ($25/mo): 2 GB RAM, 1 CPU, always on

### Recommended for Email Validator:
- Start with Free plan for testing
- Upgrade to Starter ($7/mo) for production
- Scale to Standard ($25/mo) at 1K+ users

---

## Custom Domain (Optional)

1. **In Render Dashboard**
   - Go to your web service
   - Click "Custom Domains"
   - Click "Add Custom Domain"

2. **Configure DNS**
   - Add CNAME record: `email-api.yourdomain.com` → `your-app-name.onrender.com`
   - Wait for DNS propagation (5-30 min)

3. **SSL**
   - Render automatically provisions SSL for custom domains
   - No additional configuration needed

---

## Monitoring

### Render Dashboard
- Logs: View real-time logs in dashboard
- Metrics: CPU, memory, response times
- Deployments: View deployment history

### Health Monitoring
- Set up uptime monitoring (UptimeRobot, Pingdom)
- Monitor `/health` endpoint
- Alert on downtime

---

## Pricing

- Render Free: $0
- Render Starter: $7/month
- Render Standard: $25/month

**Recommendation:** Start with Free plan, upgrade to Starter when ready for production.

---

## Troubleshooting

### Deployment Fails
- Check Render logs for errors
- Verify requirements.txt is correct
- Ensure Procfile exists with `gunicorn app:app`

### Application Crashes
- Check environment variables are set
- Verify SECRET_KEY is set
- Review error logs in dashboard

### Slow Response Times
- Upgrade to paid plan for more CPU
- Check for resource leaks
- Optimize code performance

### Database Errors
- Email Validator uses in-memory storage
- No database required
- Errors likely due to code issues, not data

---

## Alternative Deployment Platforms

### Railway
- Already configured with `railway.toml`
- Deploy via Railway CLI: `railway up`
- Free tier available

### Vercel
- Configured with `vercel.json` and `index.py`
- Deploy via Vercel CLI: `vercel --prod`
- Serverless only (limitations)

### Heroku
- Deploy via Heroku CLI: `heroku create email-validator-api && git push heroku main`
- Add-ons: None needed
- Free tier discontinued

---

## Next Steps

1. ✅ Deploy to Render
2. ⏳ Configure custom domain (optional)
3. ⏳ Set up Stripe payments
4. ⏳ Create landing page
5. ⏳ Launch on Product Hunt
6. ⏳ Start generating revenue

---

**Status:** Ready for deployment
**Platform:** Render (recommended for Python/Flask)
**Estimated time:** 5-10 minutes
**Cost:** $0 (free tier) → $7/month (production)
