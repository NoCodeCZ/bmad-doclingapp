# Coolify Deployment - Separate Services Approach

## Problem with Docker Compose Approach

The docker-compose approach has an issue: **the frontend (running in browser) cannot access `http://backend:8080`** because that's an internal Docker network address.

## Recommended Solution: Deploy as Two Separate Services

Deploy backend and frontend as **separate services in Coolify**, each with their own domain.

### Architecture

```
User Browser
    ↓
Frontend: https://docling.yourdomain.com (Port 3000)
    ↓
Backend: https://api-docling.yourdomain.com (Port 8080)
    ↓
Supabase: https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/
```

---

## Deployment Steps

### Step 1: Deploy Backend Service

1. **Create New Application in Coolify**
   - Name: `docling-backend`
   - Type: Dockerfile
   - Repository: `https://github.com/NoCodeCZ/bmad-doclingapp.git`
   - Branch: `main`
   - Dockerfile: `backend/Dockerfile`
   - Build Context: `backend/`

2. **Environment Variables**
   ```bash
   SUPABASE_URL=https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/
   SUPABASE_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoic2VydmljZV9yb2xlIn0.EnOpR72H05QVdHsjZPsw2IC3vSnOUcwOWd8MreYffR4
   MAX_FILE_SIZE=52428800
   PROCESSING_TIMEOUT=600
   ALLOWED_ORIGINS=https://docling.yourdomain.com
   ENVIRONMENT=production
   ```

3. **Domain Configuration**
   - Domain: `api-docling.yourdomain.com`
   - Port: 8080
   - Health Check Path: `/api/health`

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Verify health check: `curl https://api-docling.yourdomain.com/api/health`

---

### Step 2: Deploy Frontend Service

1. **Create New Application in Coolify**
   - Name: `docling-frontend`
   - Type: Dockerfile
   - Repository: `https://github.com/NoCodeCZ/bmad-doclingapp.git`
   - Branch: `main`
   - Dockerfile: `frontend/Dockerfile`
   - Build Context: `frontend/`

2. **Environment Variables** (CRITICAL: These must be set BEFORE building)

   In Coolify, go to **Build Variables** (not Runtime Variables):
   ```bash
   NEXT_PUBLIC_SUPABASE_URL=https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoiYW5vbiJ9.9N2FNNrBisKwF-AIj-jdeB4pGRNNBol-kXTNL3RCBFY
   NEXT_PUBLIC_API_URL=https://api-docling.yourdomain.com
   ```

   **Note**: Replace `yourdomain.com` with your actual domain from Step 1!

3. **Domain Configuration**
   - Domain: `docling.yourdomain.com`
   - Port: 3000

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Visit `https://docling.yourdomain.com`

---

## DNS Configuration

Configure two A records:

```
Type: A
Name: api-docling
Value: [Your Coolify Server IP]
TTL: 300

Type: A
Name: docling
Value: [Your Coolify Server IP]
TTL: 300
```

---

## Verification Checklist

- [ ] Backend deployed and running
- [ ] Backend health check passing: `curl https://api-docling.yourdomain.com/api/health`
- [ ] Frontend deployed and running
- [ ] Frontend loads in browser: `https://docling.yourdomain.com`
- [ ] CORS configured correctly (ALLOWED_ORIGINS in backend)
- [ ] File upload works end-to-end
- [ ] SSL certificates auto-generated for both domains

---

## Alternative: Single Domain with Path-Based Routing

If you prefer a single domain, you can use Coolify's reverse proxy to route paths:

- `docling.yourdomain.com/` → Frontend (port 3000)
- `docling.yourdomain.com/api/*` → Backend (port 8080)

This requires configuring a reverse proxy in Coolify (advanced setup).

---

## Why Not Docker Compose?

Docker Compose works great when:
- Services communicate only internally
- All traffic goes through a single entry point (reverse proxy)

For this app:
- **Browser** needs to directly call backend API
- Docker Compose internal networking (`http://backend:8080`) isn't accessible from browser
- Would need additional nginx/traefik proxy configuration

**Separate services = simpler deployment in Coolify**

---

## Cost Comparison

**Separate Services**:
- Backend: Uses ~2GB RAM, 1 core
- Frontend: Uses ~512MB RAM, 1 core
- Total: ~2.5GB RAM, 2 cores

**Same as Docker Compose** - no additional cost!

---

## Troubleshooting

### Backend Health Check Fails
```bash
# Check logs in Coolify
# Verify SUPABASE_URL and SUPABASE_KEY are set
# Ensure port 8080 is exposed
```

### Frontend Build Fails
```bash
# Ensure build variables (not runtime) are set:
#   NEXT_PUBLIC_SUPABASE_URL
#   NEXT_PUBLIC_SUPABASE_ANON_KEY
#   NEXT_PUBLIC_API_URL
# Check build logs for actual error
```

### CORS Error in Browser
```bash
# Update backend ALLOWED_ORIGINS:
ALLOWED_ORIGINS=https://docling.yourdomain.com

# Can use comma-separated for multiple:
ALLOWED_ORIGINS=https://docling.yourdomain.com,https://www.docling.yourdomain.com
```

### File Upload Fails
```bash
# Verify API_URL points to correct backend domain
# Check browser Network tab for actual request URL
# Ensure backend is accessible from browser
```

---

## Next Steps

1. Deploy backend first
2. Note backend URL
3. Deploy frontend with backend URL in build variables
4. Test end-to-end
5. Configure monitoring and alerts

