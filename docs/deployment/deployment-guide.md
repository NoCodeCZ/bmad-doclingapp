# DigitalOcean Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Workshop Document Processor to DigitalOcean App Platform for both staging and production environments.

## Prerequisites

- DigitalOcean account
- GitHub repository with the codebase
- Supabase project configured (staging and production instances)
- Git repository pushed to GitHub

## Deployment Architecture

The application consists of two services:
- **Frontend**: Next.js 14 application (Port 3000)
- **Backend**: FastAPI application (Port 8080)

Both services are deployed as separate containers on DigitalOcean App Platform with automatic deployments from the `main` branch.

---

## Part 1: Prepare Supabase Database

> **Note**: This guide supports both managed Supabase Cloud and self-hosted Supabase instances (e.g., via Coolify, Docker).

### Option A: Self-Hosted Supabase (Coolify/Docker)

If you're already running a self-hosted Supabase instance:

1. **Access Your Supabase Instance**
   - Example URL: `https://your-project.supabase.co`
   - Login to your Coolify dashboard or Supabase admin panel

2. **Run Database Migration**
   - Navigate to SQL Editor in Supabase Studio
   - Copy contents from `backend/supabase/migrations/001_create_documents_table.sql`
   - Execute the SQL to create the `documents` table

3. **Create Storage Buckets**
   - Navigate to Storage section
   - Create bucket: `uploads` (Private)
   - Create bucket: `processed` (Private)

4. **Get Credentials**
   - Settings → API → Project URL: Your self-hosted URL
   - Settings → API → anon/public key: `eyJxxx...`
   - Settings → API → service_role key: `eyJxxx...` (keep secret!)

5. **Environment Separation**
   - **Option 1**: Use the same Supabase instance with different storage bucket prefixes
     - Staging buckets: `staging-uploads`, `staging-processed`
     - Production buckets: `production-uploads`, `production-processed`
   - **Option 2**: Deploy separate Supabase instances for staging/production

### Option B: Managed Supabase Cloud

If using Supabase Cloud (https://app.supabase.com):

1. **Create Staging Project**
   - Click "New Project"
   - Name: `workshop-doc-processor-staging`
   - Region: US (same as DigitalOcean region)
   - Database Password: Generate and save securely

2. **Run Database Migration**
   - SQL Editor → Copy from `backend/supabase/migrations/001_create_documents_table.sql`
   - Execute the SQL

3. **Create Storage Buckets**
   - Storage → Create bucket: `uploads` (Private)
   - Storage → Create bucket: `processed` (Private)

4. **Get Credentials**
   - Settings → API → URL: `https://xxx.supabase.co`
   - Settings → API → anon/public key: `eyJxxx...`
   - Settings → API → service_role key: `eyJxxx...` (keep secret!)

5. **Repeat for Production**
   - Project name: `workshop-doc-processor-production`
   - Same database schema and storage buckets
   - Different credentials

---

## Part 2: Deploy to DigitalOcean App Platform

### Step 1: Create App from GitHub

1. **Login to DigitalOcean**
   - Go to https://cloud.digitalocean.com

2. **Create New App**
   - Click "Apps" in left sidebar
   - Click "Create App"
   - Choose "GitHub" as source
   - Authorize DigitalOcean to access your repository
   - Select your repository: `workshop-document-processor`
   - Branch: `main`
   - Autodeploy: ✅ Enabled

### Step 2: Configure Frontend Service

1. **Add Frontend Service**
   - Click "Edit" on the auto-detected service or add manually
   - Name: `frontend`
   - Type: Web Service
   - Source Directory: `/frontend`

2. **Build Settings**
   - Build Command: `npm ci && npm run build`
   - Run Command: `npm start`
   - HTTP Port: `3000`
   - Instance Size: Basic (512 MB RAM, 1 vCPU) - $5/month

3. **Environment Variables**
   Click "Edit" → "Environment Variables" → Add:
   ```
   NEXT_PUBLIC_API_URL = ${backend.PUBLIC_URL}
   NEXT_PUBLIC_SUPABASE_URL = https://your-supabase-url.com
   NEXT_PUBLIC_SUPABASE_ANON_KEY = eyJxxx...
   NODE_ENV = production
   ```
   
   **For self-hosted Supabase**: Use your Coolify/self-hosted URL
   **For managed Supabase**: Use `https://xxx.supabase.co`

4. **Health Check**
   - HTTP Path: `/`
   - Initial Delay: 30 seconds
   - Period: 10 seconds
   - Timeout: 5 seconds

### Step 3: Configure Backend Service

1. **Add Backend Service**
   - Click "+ Add Component" → Web Service
   - Name: `backend`
   - Source Directory: `/backend`

2. **Build Settings**
   - Build Command: `pip install --upgrade pip && pip install -r requirements.txt`
   - Run Command: `uvicorn app.main:app --host 0.0.0.0 --port 8080`
   - HTTP Port: `8080`
   - Instance Size: Basic (1 GB RAM, 1 vCPU) - $12/month

3. **Environment Variables**
   Click "Edit" → "Environment Variables" → Add:
   ```
   SUPABASE_URL = https://your-supabase-url.com
   SUPABASE_KEY = eyJxxx... (service_role key)
   MAX_FILE_SIZE = 10485760
   PROCESSING_TIMEOUT = 300
   ALLOWED_ORIGINS = ${frontend.PUBLIC_URL}
   ENVIRONMENT = staging
   ```
   
   **For self-hosted Supabase**: Use your Coolify/self-hosted URL
   **For managed Supabase**: Use `https://xxx.supabase.co`

4. **Health Check**
   - HTTP Path: `/api/health`
   - Initial Delay: 30 seconds
   - Period: 10 seconds
   - Timeout: 5 seconds

### Step 4: Configure Routes

1. **Frontend Route**
   - Path: `/`
   - Preserve Path Prefix: Yes

2. **Backend Route**
   - Path: `/api`
   - Preserve Path Prefix: Yes

### Step 5: Review and Deploy

1. **Review Configuration**
   - Check all environment variables are set
   - Verify build and run commands
   - Confirm health checks configured

2. **Name Your App**
   - App Name: `workshop-doc-processor-staging`

3. **Select Region**
   - Region: New York 3 (NYC3) or San Francisco 3 (SFO3)

4. **Deploy**
   - Click "Create Resources"
   - Wait for deployment (5-10 minutes)

---

## Part 3: Verify Deployment

### Check Deployment Status

1. **Monitor Build Logs**
   - Click on each service
   - View "Runtime Logs"
   - Ensure no errors during build

2. **Test Health Checks**
   - Frontend: `https://your-app.ondigitalocean.app/`
   - Backend: `https://your-app.ondigitalocean.app/api/health`

### Run Smoke Test

1. **Access Frontend**
   ```
   https://your-app.ondigitalocean.app
   ```

2. **Upload Test Document**
   - Prepare a small PDF file (< 1MB)
   - Upload via drag-and-drop
   - Select processing options
   - Wait for processing to complete
   - Download the markdown file

3. **Verify Backend API**
   ```bash
   curl https://your-app.ondigitalocean.app/api/health
   ```
   
   Expected response:
   ```json
   {
     "status": "healthy",
     "timestamp": "2025-10-04T14:30:00Z",
     "version": "1.0.0",
     "database_connected": true,
     "storage_connected": true
   }
   ```

4. **Check Supabase Integration**
   - Go to Supabase dashboard
   - Table Editor → `documents` table
   - Verify new record was created
   - Storage → `uploads` bucket → Check file exists
   - Storage → `processed` bucket → Check markdown exists

---

## Part 4: Production Deployment

### Create Production Environment

1. **Clone Staging App**
   - Go to App Platform dashboard
   - Click on staging app
   - Click "..." → "Clone App"
   - Name: `workshop-doc-processor-production`

2. **Update Environment Variables**
   - Use production Supabase credentials
   - Change `ENVIRONMENT = production`

3. **Configure Auto-Scaling (Optional)**
   ```yaml
   # In App Spec
   autoscaling:
     min_instance_count: 1
     max_instance_count: 3
     metrics:
       cpu:
         percent: 80
   ```

4. **Deploy Production**
   - Review all settings
   - Click "Create Resources"

---

## Part 5: CI/CD Setup

### Automatic Deployments

DigitalOcean App Platform automatically deploys on push to `main` branch:

1. **Push to Main**
   ```bash
   git add .
   git commit -m "feat: update deployment configuration"
   git push origin main
   ```

2. **Monitor Deployment**
   - Go to DigitalOcean dashboard
   - Click on app
   - View "Deployments" tab
   - Monitor build and deploy progress

### Manual Deployments

To manually trigger deployment:

1. Go to App Platform dashboard
2. Click on your app
3. Click "Actions" → "Force Rebuild and Deploy"

---

## Part 6: Monitoring and Logging

### DigitalOcean Monitoring

1. **Access Metrics**
   - App Platform → Your App → "Insights"
   - View metrics:
     - CPU Usage
     - Memory Usage
     - Request Rate
     - Response Time
     - Error Rate (4xx, 5xx)

2. **Set Up Alerts**
   - Click "Alerts" tab
   - Create alert: "High Error Rate"
     - Metric: HTTP 5xx Errors
     - Threshold: > 10% over 5 minutes
   - Create alert: "Service Down"
     - Metric: Health Check Failures
     - Threshold: 3 consecutive failures

### Application Logs

1. **View Runtime Logs**
   - App Platform → Your App → Service → "Runtime Logs"
   - Filter by:
     - Time range
     - Log level (INFO, WARNING, ERROR)
     - Search terms

2. **Download Logs**
   ```bash
   doctl apps logs <app-id> --type run
   ```

---

## Part 7: Rollback Procedures

### Rollback to Previous Deployment

1. **Via Dashboard**
   - App Platform → Your App → "Deployments"
   - Find previous successful deployment
   - Click "..." → "Rollback to this Deployment"

2. **Via Git**
   ```bash
   # Revert to previous commit
   git log --oneline
   git revert <commit-hash>
   git push origin main
   ```

### Emergency Rollback

If production is completely broken:

1. **Disable Auto-Deploy**
   - Settings → Disable "Autodeploy"

2. **Rollback to Last Known Good State**
   - Deployments → Select last working deployment
   - Rollback

3. **Fix Issues Locally**
   - Test fixes in staging first
   - Once verified, deploy to production

---

## Cost Optimization

### Estimated Monthly Costs

**Staging Environment:**
- Frontend: Basic ($5/month)
- Backend: Basic ($12/month)
- **Total: ~$17/month**

**Production Environment (Workshop Day):**
- Frontend: Basic with auto-scaling ($5-15/month)
- Backend: Professional with auto-scaling ($12-36/month)
- **Total: ~$17-51/month**

### Cost-Saving Tips

1. **Destroy Staging After Workshop**
   - Keep only production running
   - Rebuild staging when needed

2. **Scale Down After Workshop**
   - Reduce instance sizes
   - Disable auto-scaling
   - Reduce to minimum resources

3. **Use Supabase Free Tier**
   - Staging: Free tier (500 MB storage, 500 MB bandwidth)
   - Production: Free tier or upgrade if needed

---

## Troubleshooting

### Build Failures

**Frontend Build Fails:**
```bash
# Check Node.js version
# Update package.json engines:
"engines": {
  "node": "20.x",
  "npm": "9.x"
}
```

**Backend Build Fails:**
```bash
# Check Python version
# Update runtime.txt:
python-3.11
```

### Deployment Issues

**Health Check Failures:**
- Verify health check paths are correct
- Check if services are listening on correct ports
- Review runtime logs for errors

**Environment Variable Issues:**
- Verify all required variables are set
- Check for typos in variable names
- Ensure sensitive values are marked as "Secret"

**CORS Errors:**
- Update `ALLOWED_ORIGINS` in backend
- Include frontend public URL
- Check backend CORS middleware configuration

### Runtime Issues

**504 Gateway Timeout:**
- Increase processing timeout
- Check Docling processing time
- Verify file size limits

**Out of Memory:**
- Upgrade instance size
- Optimize Docling memory usage
- Implement file size restrictions

**Database Connection Errors:**
- Verify Supabase credentials
- Check database availability
- Review connection pooling settings

---

## Security Checklist

- [ ] All environment variables set as "Secret" in DigitalOcean
- [ ] Supabase service_role key never exposed to frontend
- [ ] HTTPS enforced (automatic with DigitalOcean)
- [ ] CORS configured with specific origins
- [ ] File size limits enforced (10MB)
- [ ] Processing timeouts configured (5 minutes)
- [ ] Private storage buckets configured
- [ ] Health check endpoints do not expose sensitive data

---

## Post-Deployment Checklist

- [ ] Frontend deployed and accessible
- [ ] Backend API responding to health checks
- [ ] Supabase database connection verified
- [ ] Supabase storage buckets accessible
- [ ] Test document upload successful
- [ ] Test document processing successful
- [ ] Test markdown download successful
- [ ] Monitoring and alerts configured
- [ ] Logs accessible and searchable
- [ ] Rollback procedure tested
- [ ] Documentation updated with production URLs
- [ ] Workshop facilitators notified

---

## Next Steps After Deployment

1. **Load Testing** (Story 3.3)
   - Test with 30 concurrent users
   - Verify auto-scaling triggers
   - Benchmark processing times

2. **Workshop Rehearsal** (Story 3.5)
   - Test with real workshop documents
   - Gather feedback from testers
   - Identify and fix issues

3. **Production Cutover**
   - Schedule deployment during low-traffic period
   - Run final smoke tests
   - Communicate production URL to workshop attendees

---

## Support Contacts

- **DigitalOcean Support**: https://cloud.digitalocean.com/support
- **Supabase Support**: https://supabase.com/support
- **Workshop Facilitator**: [Add contact information]

---

## Appendix: App Spec YAML Reference

See `.digitalocean/app.yaml` for the complete App Spec configuration.

To deploy using App Spec:
```bash
doctl apps create --spec .digitalocean/app.yaml
```

To update existing app:
```bash
doctl apps update <app-id> --spec .digitalocean/app.yaml
```

---

**Deployment Guide Complete** ✓

This guide covers all aspects of deploying the Workshop Document Processor to DigitalOcean App Platform. Follow the steps sequentially for successful deployment.