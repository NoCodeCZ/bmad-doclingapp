# Coolify Deployment - Single Domain

## Architecture

Everything runs under **ONE domain**:

```
yourdomain.com/          → Frontend (Next.js)
yourdomain.com/api/*     → Backend (FastAPI)
```

Nginx reverse proxy handles the routing inside Docker.

---

## Deployment in Coolify

### Step 1: Create Application

1. **New Application** → **Docker Compose**
2. **Name**: `docling-app`
3. **Repository**: `https://github.com/NoCodeCZ/bmad-doclingapp.git`
4. **Branch**: `main`
5. **Docker Compose File**: `docker-compose.yml` (default)
6. **Build Context**: `/` (root)

### Step 2: Set Environment Variables

Copy these into Coolify's Environment Variables section:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key-here
SUPABASE_ANON_KEY=your-anon-key-here
MAX_FILE_SIZE=52428800
PROCESSING_TIMEOUT=600
ENVIRONMENT=production
```

That's it! Only 5 environment variables needed.

### Step 3: Configure Domain

1. **Domain**: `docling.yourdomain.com` (or any domain you want)
2. **Port**: `80` (Nginx listens on port 80)
3. **Enable SSL**: ✅ (Coolify auto-generates via Let's Encrypt)

### Step 4: Deploy

1. Click **"Deploy"**
2. Wait for all 3 services to build:
   - ✅ Nginx (30 seconds)
   - ✅ Backend (3-5 minutes - Docling dependencies)
   - ✅ Frontend (2-3 minutes - Next.js build)
3. Total deploy time: ~5-8 minutes

---

## Verification

### 1. Check Health
```bash
curl https://docling.yourdomain.com/api/health
# Should return: {"status":"ok","timestamp":"..."}
```

### 2. Check Frontend
Open browser: `https://docling.yourdomain.com`
- Should see upload interface
- No errors in console (F12)

### 3. Test Upload
1. Upload a test PDF
2. Verify processing works
3. Download markdown output

---

## How It Works

```
Browser Request: https://docling.yourdomain.com/
    ↓
Coolify (Port 80 with SSL)
    ↓
Nginx Container (Port 80)
    ↓
    ├─ / → Frontend Container (Port 3000)
    └─ /api/* → Backend Container (Port 8080)
```

**Key Points**:
- Nginx is the entry point (only exposed port)
- Frontend and Backend are internal (not exposed)
- All requests go through ONE domain
- SSL handled by Coolify
- 50MB file uploads supported

---

## DNS Configuration

Point your domain to Coolify server:

```
Type: A
Name: docling (or your chosen subdomain)
Value: [Your Coolify Server IP]
TTL: 300
```

Wait for DNS propagation, then Coolify auto-generates SSL certificate.

---

## Troubleshooting

### Build fails with "No such file or directory"

**Cause**: Build context issue

**Fix**: Make sure Build Context is set to `/` (root directory)

### Frontend build fails - exit code 1

**Cause**: Missing environment variables

**Fix**:
1. Check all 5 env vars are set in Coolify
2. Frontend has defaults, so it should build even without them
3. Check build logs for actual error

### "502 Bad Gateway" error

**Cause**: Backend or Frontend container not running

**Fix**:
```bash
# In Coolify, check container status:
# - docling-nginx: Running
# - docling-backend: Running
# - docling-frontend: Running

# Check logs for each container
```

### API calls fail with CORS error

**Cause**: Backend not accepting requests

**Fix**: Backend is configured with `ALLOWED_ORIGINS=*` so this shouldn't happen. If it does, check backend logs.

### File upload fails

**Cause**: Nginx timeout or size limit

**Fix**: Already configured in nginx.conf:
- `client_max_body_size 50M`
- `proxy_read_timeout 600s`

If still failing, check backend logs for processing errors.

---

## Advantages

✅ **Single Domain**: Everything at one URL
✅ **Simple Setup**: Only 5 environment variables
✅ **No CORS Issues**: Same-origin requests
✅ **SSL Included**: Auto via Let's Encrypt
✅ **50MB Uploads**: Configured throughout stack
✅ **Auto Restart**: All containers restart on failure
✅ **Health Checks**: Backend monitored automatically

---

## Resource Usage

- **Nginx**: ~10MB RAM
- **Backend**: ~2GB RAM (Docling processing)
- **Frontend**: ~512MB RAM
- **Total**: ~2.5GB RAM

**Disk**: 10GB for upload volume

---

## Next Steps After Deployment

1. ✅ Verify health endpoint
2. ✅ Test file upload end-to-end
3. ✅ Configure monitoring alerts in Coolify
4. ✅ Set up backup strategy for uploads volume
5. ✅ Document domain for workshop attendees

---

**You're ready to deploy!** 🚀

Just create the Docker Compose application in Coolify, paste the 5 environment variables, set your domain, and deploy.
