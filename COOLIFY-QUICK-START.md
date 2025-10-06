# Coolify Quick Start - Exact Configuration

## Repository
`https://github.com/NoCodeCZ/bmad-doclingapp.git`

---

## Service 1: Backend API

### Basic Settings
- **Name**: `docling-backend`
- **Source**: Public Repository
- **Repository URL**: `https://github.com/NoCodeCZ/bmad-doclingapp.git`
- **Branch**: `main`
- **Build Pack**: Dockerfile
- **Dockerfile Location**: `backend/Dockerfile`
- **Base Directory**: `backend` ⚠️ CRITICAL - set this!
- **Publish Directory**: (leave empty)

### Port Configuration
- **Port**: `8080`

### Domain
- Set your domain (e.g., `api-docling.yourdomain.com`)
- Enable SSL (auto via Let's Encrypt)

### Environment Variables (Runtime)
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key-here
MAX_FILE_SIZE=52428800
PROCESSING_TIMEOUT=600
ALLOWED_ORIGINS=https://YOUR-FRONTEND-DOMAIN.com
ENVIRONMENT=production
```

⚠️ **Replace `YOUR-FRONTEND-DOMAIN.com`** with the domain you'll use for frontend (set this in Step 2)

### Health Check
- **Path**: `/api/health`
- **Port**: `8080`
- **Interval**: `30s`

### Deploy
Click "Deploy" and wait for build to complete (~3-5 minutes for Docling dependencies)

### Verify
```bash
curl https://api-docling.yourdomain.com/api/health
# Should return: {"status":"ok","timestamp":"..."}
```

---

## Service 2: Frontend Web App

### Basic Settings
- **Name**: `docling-frontend`
- **Source**: Public Repository
- **Repository URL**: `https://github.com/NoCodeCZ/bmad-doclingapp.git`
- **Branch**: `main`
- **Build Pack**: Dockerfile
- **Dockerfile Location**: `frontend/Dockerfile`
- **Base Directory**: `frontend` ⚠️ CRITICAL - set this!
- **Publish Directory**: (leave empty)

### Port Configuration
- **Port**: `3000`

### Domain
- Set your domain (e.g., `docling.yourdomain.com`)
- Enable SSL (auto via Let's Encrypt)

### Build Arguments (⚠️ Set as BUILD ARGS, not runtime env vars)

In Coolify, look for "Build Arguments" or "Build Variables" section:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
NEXT_PUBLIC_API_URL=https://api-docling.yourdomain.com
```

⚠️ **Replace `api-docling.yourdomain.com`** with your actual backend domain from Step 1!

### Environment Variables (Runtime - Optional)
You can also set these as runtime vars (same values as build args above), but build args are what matters for Next.js build.

### Deploy
Click "Deploy" and wait for build to complete (~2-3 minutes)

### Verify
- Open browser: `https://docling.yourdomain.com`
- Should see the upload interface
- Check browser console (F12) for errors

---

## Common Issues

### Issue: "Base Directory" not available

If Coolify doesn't show "Base Directory" option:
- Look for "Build Context" or "Context Directory"
- Set to `backend` for backend, `frontend` for frontend

### Issue: Backend build fails - "No such file or directory"

**Cause**: Build context not set to `backend/` directory

**Fix**:
- In Coolify, set Base Directory = `backend`
- Or set Build Context = `backend`
- The Dockerfile needs to be able to find `requirements.txt`

### Issue: Frontend build fails - exit code 1

**Cause**: Missing build arguments

**Fix**:
1. Make sure you set **Build Arguments** (not runtime env vars)
2. In Coolify UI:
   - Look for "Build Args" section
   - Or "Build-time Environment Variables"
   - NOT "Runtime Environment Variables"
3. If Coolify doesn't separate them, the Dockerfile has defaults that should work

### Issue: Frontend builds but shows errors in browser

**Cause**: `NEXT_PUBLIC_API_URL` points to wrong backend

**Fix**:
- Check browser Network tab (F12)
- See what URL it's trying to call
- Update frontend build args with correct backend URL
- Redeploy frontend

### Issue: CORS error in browser

**Cause**: Backend `ALLOWED_ORIGINS` doesn't match frontend domain

**Fix**:
- Update backend env var: `ALLOWED_ORIGINS=https://docling.yourdomain.com`
- Restart backend service
- Clear browser cache and retry

---

## If Coolify Doesn't Support Build Args

If Coolify doesn't allow setting build args separately, the Dockerfile has safe defaults:

**Backend**: No build args needed ✅

**Frontend**: Has defaults in Dockerfile (line 14-16):
```dockerfile
ARG NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
ARG NEXT_PUBLIC_API_URL=/api
```

**BUT** you MUST update `NEXT_PUBLIC_API_URL` default to match your backend domain!

Let me know your backend domain and I'll update the Dockerfile with the correct default.

---

## DNS Configuration

After deploying both services, configure DNS:

```
# Backend
Type: A
Name: api-docling (or your chosen subdomain)
Value: [Coolify Server IP]

# Frontend
Type: A
Name: docling (or your chosen subdomain)
Value: [Coolify Server IP]
```

Wait for DNS propagation (5-60 minutes), then Coolify will auto-generate SSL certs.

---

## Architecture Diagram

```
User Browser
    ↓
    ↓ HTTPS
    ↓
[Frontend: docling.yourdomain.com:3000]
    ↓
    ↓ HTTPS (from browser, not server)
    ↓
[Backend: api-docling.yourdomain.com:8080]
    ↓
    ↓ HTTPS
    ↓
[Supabase: your-project.supabase.co]
```

**Important**: Frontend and backend are separate services. Browser makes API calls directly to backend.

---

## What Should Work Now

With the latest code pushed to GitHub:

1. ✅ Backend Dockerfile standalone ready
2. ✅ Frontend Dockerfile with build arg defaults
3. ✅ Both can build independently
4. ⚠️ Frontend needs correct backend URL (either via build args or Dockerfile update)

**Tell me your backend domain** and I can update the frontend Dockerfile default to match!
