# Story 1.7: DigitalOcean Deployment - Prerequisites & Manual Steps

## Story Status: Ready for Manual Deployment ✅

All automated/code-based tasks for Story 1.7 have been completed. The remaining tasks require manual setup through external dashboards (DigitalOcean, GitHub, Supabase).

---

## ✅ Completed Tasks (Automated)

### 1. DigitalOcean App Platform Configuration
- **File Created:** `.digitalocean/app.yaml`
- **Contents:**
  - Frontend service configuration (Next.js)
  - Backend service configuration (FastAPI)
  - Environment variable templates
  - Health check endpoints
  - Auto-scaling configuration
  - Resource allocation (instance sizes)

### 2. Health Check Endpoints
- **Backend:** `GET /api/health`
  - Location: [`backend/app/api/endpoints/health.py`](../backend/app/api/endpoints/health.py:1)
  - Checks: Database connectivity, Storage connectivity
  - Response: JSON with status, timestamp, version
  
- **Frontend:** `GET /`
  - Next.js root page serves as health check
  - Returns full application UI

### 3. Deployment Documentation
- **File Created:** [`docs/deployment-guide.md`](deployment-guide.md:1) (561 lines)
- **Sections:**
  - Supabase instance setup (staging & production)
  - DigitalOcean App Platform configuration
  - Service configuration (frontend & backend)
  - Environment variables reference
  - Health check configuration
  - CI/CD setup
  - Monitoring and logging
  - Rollback procedures
  - Troubleshooting guide
  - Cost optimization
  - Security checklist
  - Post-deployment checklist

---

## 📋 Manual Steps Required

The following steps require human interaction with web dashboards and cannot be automated:

### Step 1: Prepare Git Repository
**Estimated Time:** 5 minutes

```bash
# Ensure all changes are committed
git add .
git commit -m "feat: add DigitalOcean deployment configuration"

# Push to GitHub (or GitLab)
git push origin main
```

**Prerequisites:**
- GitHub or GitLab account
- Repository created and configured

---

### Step 2: Verify Supabase Instance Setup
**Estimated Time:** 5-10 minutes
**Dashboard:** Your self-hosted Supabase instance (e.g., Coolify)

> **Note**: If you're using a self-hosted Supabase instance via Coolify (as currently configured), verify the following setup. For managed Supabase Cloud users, see the deployment guide for alternative instructions.

**Current Configuration (Self-Hosted):**
- Supabase URL: `https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/`
- Using service role key for backend authentication

**Verification Steps:**

1. **Verify Database Schema**
   - Access your Supabase Studio (via Coolify dashboard)
   - Go to SQL Editor
   - Verify the `documents` table exists:
     ```sql
     SELECT * FROM documents LIMIT 1;
     ```
   - If table doesn't exist, run migration from [`backend/supabase/migrations/001_create_documents_table.sql`](../backend/supabase/migrations/001_create_documents_table.sql:1)

2. **Verify Storage Buckets**
   - Navigate to Storage section
   - Verify buckets exist:
     - ✅ `uploads` (Private)
     - ✅ `processed` (Private)
   - If buckets don't exist, create them now

3. **Verify Credentials**
   - Settings → API
   - Confirm you have:
     - ✅ Project URL: Your self-hosted URL
     - ✅ Anon/Public Key: `eyJxxx...`
     - ✅ Service Role Key: `eyJxxx...` (keep secret!)

4. **Environment Variable Strategy**
   - **Option 1**: Use same Supabase instance with bucket prefixes
     - Staging: `staging-uploads`, `staging-processed`
     - Production: `production-uploads`, `production-processed`
   - **Option 2**: Deploy separate self-hosted instances (if available)
   - **Current Setup**: Single instance (recommended for workshop MVP)

---

### Step 3: Deploy to DigitalOcean App Platform
**Estimated Time:** 15-20 minutes  
**Dashboard:** https://cloud.digitalocean.com

1. **Create App**
   - Go to Apps → Create App
   - Source: GitHub
   - Repository: Select your repository
   - Branch: `main`
   - Autodeploy: ✅ Enable

2. **Configure Frontend Service**
   - Name: `frontend`
   - Build Command: `cd frontend && npm ci && npm run build`
   - Run Command: `cd frontend && npm start`
   - HTTP Port: `3000`
   - Instance Size: Basic (512 MB RAM) - $5/month
   
   **Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL = ${backend.PUBLIC_URL}
   NEXT_PUBLIC_SUPABASE_URL = https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/
   NEXT_PUBLIC_SUPABASE_ANON_KEY = eyJxxx... (your anon key from Supabase)
   NODE_ENV = production
   ```
   
   **Note**: Replace with your actual Supabase anon key from Settings → API

3. **Configure Backend Service**
   - Name: `backend`
   - Build Command: `cd backend && pip install --upgrade pip && pip install -r requirements.txt`
   - Run Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8080`
   - HTTP Port: `8080`
   - Instance Size: Basic (1 GB RAM) - $12/month
   
   **Environment Variables:**
   ```
   SUPABASE_URL = https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/
   SUPABASE_KEY = eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoic2VydmljZV9yb2xlIn0.EnOpR72H05QVdHsjZPsw2IC3vSnOUcwOWd8MreYffR4
   MAX_FILE_SIZE = 10485760
   PROCESSING_TIMEOUT = 300
   ALLOWED_ORIGINS = ${frontend.PUBLIC_URL}
   ENVIRONMENT = staging
   ```
   
   **Note**: Using your self-hosted Supabase instance credentials

4. **Configure Health Checks**
   - Frontend: HTTP Path `/`, Initial Delay 30s
   - Backend: HTTP Path `/api/health`, Initial Delay 30s

5. **Review and Deploy**
   - App Name: `workshop-doc-processor-staging`
   - Region: NYC3 or SFO3
   - Click "Create Resources"

---

### Step 4: Verify Deployment
**Estimated Time:** 10 minutes

1. **Check Build Logs**
   - Monitor frontend build (5-7 minutes)
   - Monitor backend build (3-5 minutes)
   - Ensure no errors

2. **Test Health Checks**
   ```bash
   # Backend health check
   curl https://your-app.ondigitalocean.app/api/health
   
   # Expected response:
   # {
   #   "status": "healthy",
   #   "timestamp": "2025-10-04T14:30:00Z",
   #   "version": "1.0.0",
   #   "database_connected": true,
   #   "storage_connected": true
   # }
   ```

3. **Access Frontend**
   - Open `https://your-app.ondigitalocean.app` in browser
   - Verify page loads without errors

---

### Step 5: Run Smoke Test
**Estimated Time:** 5 minutes

1. **Prepare Test Document**
   - Use a small PDF file (< 1MB)
   - Example: A simple 2-page document

2. **Complete Upload Workflow**
   - Open frontend URL
   - Drag-and-drop test PDF
   - Select processing options:
     - OCR: Off
     - Mode: Fast
   - Click "Upload"

3. **Verify Processing**
   - Wait for status updates
   - Status should transition: queued → processing → complete
   - Download button should appear

4. **Verify Database**
   - Go to Supabase dashboard
   - Table Editor → `documents`
   - Verify new record exists with status 'complete'

5. **Verify Storage**
   - Storage → `uploads` bucket
   - Confirm original PDF exists
   - Storage → `processed` bucket
   - Confirm markdown file exists

6. **Download and Verify Output**
   - Click "Download Markdown"
   - Open downloaded `.md` file
   - Verify content is readable markdown

---

## ✅ Story 1.7 Acceptance Criteria Review

### From Implementation Plan ([`docs/implementation-plan.md:293-301`](implementation-plan.md:293))

1. ✅ **DigitalOcean App Platform configured with two services**
   - Configuration file: [`.digitalocean/app.yaml`](../.digitalocean/app.yaml:1)
   - Frontend service: Next.js
   - Backend service: FastAPI
   - Both deploying from monorepo ✓

2. ⏳ **Staging environment deployed with separate Supabase instance**
   - Instructions provided in deployment guide
   - **Requires manual setup** (Step 2 above)

3. ✅ **Environment variables configured for both services**
   - Complete list in [`.digitalocean/app.yaml`](../.digitalocean/app.yaml:1)
   - Documented in [`deployment-guide.md`](deployment-guide.md:1)
   - Templates ready for manual input ✓

4. ✅ **Health check endpoints configured in DigitalOcean**
   - Backend: `/api/health` endpoint implemented
   - Frontend: `/` root page
   - Configuration in app.yaml ✓

5. ⏳ **Deployment succeeds for both services with publicly accessible URLs**
   - **Requires manual deployment** (Step 3 above)

6. ⏳ **Basic smoke test passes**
   - **Requires manual testing** (Step 5 above)

7. ✅ **Deployment documentation includes rollback procedure**
   - Comprehensive guide in [`deployment-guide.md`](deployment-guide.md:1)
   - Rollback section included ✓

---

## 📊 Summary

### What Can Be Automated (Completed)
- [x] App Platform configuration file
- [x] Health check endpoint implementation
- [x] Environment variable templates
- [x] Deployment documentation
- [x] Rollback procedures
- [x] Monitoring setup documentation
- [x] Troubleshooting guide

### What Requires Manual Setup
- [ ] Create DigitalOcean account (if not already created)
- [ ] Connect GitHub repository to DigitalOcean
- [ ] Verify self-hosted Supabase instance is properly configured
  - [ ] Database migration executed
  - [ ] Storage buckets created (`uploads`, `processed`)
  - [ ] Credentials accessible
- [ ] Configure environment variables in DO dashboard
- [ ] Deploy via DigitalOcean App Platform
- [ ] Verify health checks pass
- [ ] Run smoke test with sample document

---

## 📦 Deliverables

### Configuration Files
- [`.digitalocean/app.yaml`](../.digitalocean/app.yaml:1) - App Platform specification
  - **Note**: Update `NEXT_PUBLIC_SUPABASE_ANON_KEY` with your actual anon key from Supabase Settings → API
  - Self-hosted Supabase URL is already configured: `https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/`
  - Backend service role key is already configured

### Documentation
- [`docs/deployment-guide.md`](deployment-guide.md:1) - Complete deployment guide (updated for self-hosted Supabase)
- [`docs/story-1.7-deployment-prerequisites.md`](story-1.7-deployment-prerequisites.md:1) - This file

### Implementation
- [`backend/app/api/endpoints/health.py`](../backend/app/api/endpoints/health.py:1) - Health check endpoint

---

## 🎯 Next Steps

1. **Review the deployment guide**: [`docs/deployment-guide.md`](deployment-guide.md:1)
2. **Follow manual setup steps** above (estimated 45 minutes total)
3. **Run smoke test** to verify deployment
4. **Mark Story 1.7 as complete** once smoke test passes

---

## ⚠️ Important Notes

- **Self-Hosted Supabase:** You're using a self-hosted Supabase instance via Coolify. Ensure it's accessible from DigitalOcean's network.
- **Anon Key Required:** Before deploying, retrieve your Supabase anon key from Settings → API and update `.digitalocean/app.yaml`
- **Network Access:** Verify your Coolify-hosted Supabase allows connections from DigitalOcean's IP ranges
- **Cost Awareness:** Staging environment costs ~$17/month on DigitalOcean. Destroy when not in use to save costs.
- **Health Checks:** Must pass before deployment is considered successful.
- **Rollback Plan:** Documented in deployment guide. Test rollback procedure once.

---

## 📞 Support Resources

- **DigitalOcean Docs:** https://docs.digitalocean.com/products/app-platform/
- **Supabase Docs:** https://supabase.com/docs
- **Deployment Guide:** [`docs/deployment-guide.md`](deployment-guide.md:1)

---

**Story 1.7 Status: Ready for Manual Deployment** ✅

All automatable tasks completed. Manual deployment required to fully satisfy acceptance criteria.