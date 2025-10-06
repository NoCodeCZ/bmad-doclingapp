# Coolify Deployment Checklist

## Pre-Deployment Status ✅

**Git Repository**: `https://github.com/NoCodeCZ/bmad-doclingapp.git`

**Ready for Deployment:**
- ✅ docker-compose.yml validated
- ✅ Backend Dockerfile configured
- ✅ Frontend Dockerfile configured
- ✅ Environment variables template ready
- ✅ 50MB file upload support enabled
- ✅ Health checks configured
- ✅ Auto-restart enabled

**Outstanding Changes to Commit:**
- 12 commits ahead of origin/main
- Modified test/docs files (non-critical for deployment)
- New test infrastructure (can deploy as-is)

---

## Step 1: Push Code to Repository

```bash
# Optional: Commit recent changes
git add -A
git commit -m "Add deployment infrastructure and tests"
git push origin main

# Verify push succeeded
git status
```

**Status**: Repository has 12 unpushed commits. Push before deploying or deploy current origin/main.

---

## Step 2: Create Application in Coolify

### 2.1 Basic Setup
1. Login to your Coolify dashboard
2. Click **"New Application"**
3. Select **"Docker Compose"**
4. Name: `docling-processor`

### 2.2 Repository Configuration
- **Repository URL**: `https://github.com/NoCodeCZ/bmad-doclingapp.git`
- **Branch**: `main`
- **Build Context**: `/` (project root)
- **Auto-deploy**: ✅ Enable
- **Docker Compose File**: `docker-compose.yml`

---

## Step 3: Configure Environment Variables

Copy these into Coolify's Environment Variables section:

```bash
# Supabase Configuration
SUPABASE_URL=https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/
SUPABASE_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoic2VydmljZV9yb2xlIn0.EnOpR72H05QVdHsjZPsw2IC3vSnOUcwOWd8MreYffR4
SUPABASE_ANON_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoiYW5vbiJ9.9N2FNNrBisKwF-AIj-jdeB4pGRNNBol-kXTNL3RCBFY

# Application URLs (IMPORTANT: Set these based on your domain)
BACKEND_URL=http://backend:8080
FRONTEND_URL=https://YOUR-DOMAIN.com

# File Upload Configuration
MAX_FILE_SIZE=52428800
PROCESSING_TIMEOUT=600

# Environment
ENVIRONMENT=production
```

**⚠️ CRITICAL**:
1. Replace `YOUR-DOMAIN.com` with your actual domain (e.g., `https://docling.mycompany.com`)
2. `BACKEND_URL` should stay as `http://backend:8080` (internal Docker network)
3. All three `NEXT_PUBLIC_*` variables are passed as build arguments automatically

---

## Step 4: Domain Configuration

### 4.1 Set Domain in Coolify
- Frontend domain: `docling.your-domain.com` (or your chosen subdomain)
- Coolify will auto-generate SSL certificates via Let's Encrypt

### 4.2 DNS Configuration
Point your domain to Coolify server:
```
Type: A
Name: docling (or your subdomain)
Value: [Your Coolify Server IP]
TTL: 300
```

### 4.3 Update FRONTEND_URL
After setting domain, update environment variable:
```bash
FRONTEND_URL=https://docling.your-domain.com
```

---

## Step 5: Deploy Application

1. Review all settings in Coolify
2. Click **"Deploy"**
3. Monitor build logs in real-time
4. Wait for both services to start (2-5 minutes)

### Expected Build Process:
```
1. Cloning repository...
2. Building backend service...
   - Installing Python dependencies
   - Setting up Docling
3. Building frontend service...
   - Installing npm dependencies
   - Building Next.js app
4. Starting containers...
   - Backend: Port 8080
   - Frontend: Port 3000
5. Health checks passing...
```

---

## Step 6: Verify Deployment

### 6.1 Health Check
```bash
curl https://your-domain.com/api/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-06T08:56:04Z"
}
```

### 6.2 Frontend Check
1. Open `https://your-domain.com` in browser
2. Verify UI loads correctly
3. Check for console errors (F12 DevTools)

### 6.3 File Upload Test
1. Prepare a test PDF (under 50MB)
2. Drag and drop onto upload area
3. Verify processing starts
4. Check status updates appear
5. Download markdown output
6. Verify content accuracy

### 6.4 Container Status (Coolify Dashboard)
- ✅ Backend container: Running
- ✅ Frontend container: Running
- ✅ Health checks: Passing
- ✅ Memory usage: <2GB backend, <1GB frontend
- ✅ No restart loops

---

## Step 7: Post-Deployment Configuration

### 7.1 Monitoring
In Coolify dashboard, configure:
- Email alerts for container failures
- Resource usage thresholds
- Log retention settings

### 7.2 Backups
- Database: Already handled by Supabase
- Uploaded files: Volume mounted at `/app/uploads`
- Configuration: Stored in Git repository

---

## Troubleshooting Guide

### Issue: Build Fails

**Check:**
1. Build logs in Coolify dashboard
2. Verify all environment variables set
3. Check repository branch is correct
4. Ensure Dockerfile paths are valid

**Common Fixes:**
```bash
# Backend build fails
- Check requirements.txt exists
- Verify Python 3.11 compatibility

# Frontend build fails
- Check package.json exists
- Verify Node 18 compatibility
- Clear build cache in Coolify
```

### Issue: Containers Won't Start

**Check:**
1. Environment variables are set correctly
2. Port conflicts (8080, 3000)
3. Health check logs
4. Container resource limits

**Debug Commands:**
```bash
# View logs in Coolify dashboard
# Or SSH to Coolify server:
docker logs docling-backend
docker logs docling-frontend
```

### Issue: Frontend Loads But White Screen

**Cause**: Backend not accessible

**Fix:**
1. Verify `BACKEND_URL=http://backend:8080`
2. Check backend container is running
3. Test backend health endpoint
4. Check Docker network connectivity

### Issue: File Upload Fails

**Check:**
1. File size under 50MB
2. Supported file type (PDF, DOCX, PPTX, XLSX)
3. Backend logs for errors
4. Supabase connection

**Debug:**
```bash
# Check backend logs
# Look for Docling processing errors
# Verify Supabase storage bucket exists
```

### Issue: SSL Certificate Fails

**Check:**
1. DNS A record points to Coolify server
2. Domain propagated (check via dig/nslookup)
3. Port 80/443 open on firewall
4. Let's Encrypt rate limits not exceeded

**Fix:**
```bash
# Wait for DNS propagation (up to 48hrs)
# Retry certificate generation in Coolify
# Check Coolify SSL logs
```

---

## Verification Checklist

After deployment, verify:

- [ ] Git repository pushed to origin
- [ ] Application created in Coolify
- [ ] Environment variables configured
- [ ] Domain DNS configured
- [ ] SSL certificate generated
- [ ] Both containers running
- [ ] Health check passing: `curl https://domain.com/api/health`
- [ ] Frontend loads in browser
- [ ] Upload test file successfully
- [ ] Download markdown output
- [ ] No errors in browser console
- [ ] No errors in container logs
- [ ] Monitoring alerts configured
- [ ] Auto-deploy enabled

---

## Quick Reference

**Service Ports:**
- Frontend: 3000
- Backend: 8080

**Container Names:**
- docling-frontend
- docling-backend

**Volume:**
- uploads: `/app/uploads`

**Network:**
- docling-network

**File Upload Limit:**
- 50MB

**Processing Timeout:**
- 10 minutes (600 seconds)

**Health Check Interval:**
- Every 30 seconds

**Restart Policy:**
- unless-stopped

---

## Support Resources

**Documentation:**
- [Coolify Official Docs](https://coolify.io/docs)
- [Project README](README.md)
- [Coolify Deployment Guide](docs/deployment/coolify-deployment.md)

**Logs Access:**
- Coolify Dashboard → Application → Logs
- Real-time streaming available

**Common Commands:**
```bash
# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# Check resource usage
docker stats

# Rebuild containers
docker-compose up --build -d
```

---

## Next Steps After Deployment

1. **Test thoroughly** with various file types
2. **Monitor resource usage** for first 24 hours
3. **Set up monitoring alerts**
4. **Document custom domain** for team
5. **Create user guide** for workshop attendees
6. **Performance test** with concurrent uploads
7. **Backup verification** (test restore process)

---

**Deployment Ready!** 🚀

Your application is configured and ready to deploy to Coolify. Follow the steps above and refer to the troubleshooting section if issues arise.
