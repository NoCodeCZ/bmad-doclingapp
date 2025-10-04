# DigitalOcean App.yaml Configuration Updates

## ✅ Credentials Received - Ready for Configuration

You've provided your Supabase credentials. This guide will help you update `.digitalocean/app.yaml` for deployment.

**Received:**
- ✅ Anon Key: `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...` (anon role)
- ✅ JWT Secret: `XPJ0e4UUK0liOadb9nuky0DJHqtjeOKG`

### Current Configuration Status

✅ **Configuration Status:**
- Supabase URL: `https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/`
- Backend Service Role Key: Already configured
- Frontend Anon Key: **Ready to apply** (see below)
- JWT Secret: Documented for reference

**Action Required:** Update `.digitalocean/app.yaml` with the anon key below

---

## ✅ Your Credentials (Already Retrieved)

**Anon Key (for frontend):**
```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoiYW5vbiJ9.9N2FNNrBisKwF-AIj-jdeB4pGRNNBol-kXTNL3RCBFY
```

**JWT Secret (for reference):**
```
XPJ0e4UUK0liOadb9nuky0DJHqtjeOKG
```

> **Note**: JWT secret is not needed in `.digitalocean/app.yaml` - it's only used internally by Supabase for token verification.

---

## Update `.digitalocean/app.yaml`

**File Location:** `.digitalocean/app.yaml`

**Line 29-31** (Frontend service):

```yaml
      - key: NEXT_PUBLIC_SUPABASE_ANON_KEY
        value: YOUR_ACTUAL_ANON_KEY_HERE  # Replace with key from Supabase Settings → API
        type: SECRET
```

**Replace `YOUR_ACTUAL_ANON_KEY_HERE`** with:
```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoiYW5vbiJ9.9N2FNNrBisKwF-AIj-jdeB4pGRNNBol-kXTNL3RCBFY
```

---

## Network Access Verification

Before deploying to DigitalOcean, verify:

### ✅ Checklist:
- [ ] Your Coolify-hosted Supabase is publicly accessible
- [ ] Test connectivity: `curl https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/`
- [ ] Firewall allows connections from external IPs (DigitalOcean will connect from their network)
- [ ] SSL certificate is valid (check HTTPS works)
- [ ] Supabase Storage buckets are accessible via API

### Network Requirements:
- **Inbound**: Allow HTTPS (443) from DigitalOcean IP ranges
- **Outbound**: Not required (DigitalOcean initiates connections to Supabase)

---

## Alternative: Environment Separation Strategy

Since you have one self-hosted Supabase instance, consider:

### Option 1: Single Instance with Bucket Prefixes (Recommended for Workshop)
```yaml
# Use same Supabase instance
# Differentiate by bucket names:
- uploads → staging-uploads, production-uploads
- processed → staging-processed, production-processed
```

### Option 2: Separate Instances
- Deploy second Supabase instance for production
- Keep staging on current instance
- Different credentials for each environment

---

## Deployment Steps Summary

1. **Get Supabase anon key** from Coolify → Supabase → Settings → API
2. **Update `.digitalocean/app.yaml`** line 30 with actual anon key
3. **Verify network access** to self-hosted Supabase
4. **Push to GitHub** (git push origin main)
5. **Follow manual deployment** in [`docs/story-1.7-deployment-prerequisites.md`](story-1.7-deployment-prerequisites.md:1)

---

## Security Considerations

### ✅ Safe to Expose (Public):
- `NEXT_PUBLIC_SUPABASE_URL` - Public URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Anon key (limited permissions)

### 🔒 Keep Secret (Never Expose):
- `SUPABASE_KEY` - Service role key (full database access)
- Database password
- Any other API keys

### DigitalOcean Environment Variables:
All environment variables in `app.yaml` are automatically encrypted by DigitalOcean when marked as `type: SECRET`.

---

## Troubleshooting

### Issue: "Connection refused" during deployment
**Solution:** Verify Coolify firewall allows external connections

### Issue: "Invalid JWT token"
**Solution:** Double-check anon key is copied correctly (no extra spaces)

### Issue: "CORS error" after deployment
**Solution:** Update `ALLOWED_ORIGINS` in backend to include DigitalOcean frontend URL

---

## Quick Reference: Full Environment Variables

### Frontend Service
```bash
NEXT_PUBLIC_API_URL=${backend.PUBLIC_URL}
NEXT_PUBLIC_SUPABASE_URL=https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoiYW5vbiJ9.9N2FNNrBisKwF-AIj-jdeB4pGRNNBol-kXTNL3RCBFY
NODE_ENV=production
```

### Backend Service
```bash
SUPABASE_URL=https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/
SUPABASE_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoic2VydmljZV9yb2xlIn0.EnOpR72H05QVdHsjZPsw2IC3vSnOUcwOWd8MreYffR4
MAX_FILE_SIZE=10485760
PROCESSING_TIMEOUT=300
ALLOWED_ORIGINS=${frontend.PUBLIC_URL}
ENVIRONMENT=staging
```

---

**Next Step:** Retrieve your Supabase anon key and update `.digitalocean/app.yaml`, then proceed with deployment.