# Supabase Credentials Reference - Self-Hosted Instance

## ⚠️ SECURITY WARNING
**This file contains sensitive credentials. DO NOT commit to public repositories.**

---

## Supabase Instance Details

### Instance Information
- **Hosting**: Self-hosted via Coolify
- **URL**: `https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/`
- **Environment**: Shared (staging/production using same instance)

---

## API Credentials

### Anon Key (Public - Frontend & Backend)
```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoiYW5vbiJ9.9N2FNNrBisKwF-AIj-jdeB4pGRNNBol-kXTNL3RCBFY
```

**Usage**: Frontend API calls (limited permissions via RLS)

### Service Role Key (Secret - Backend Only)
```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoic2VydmljZV9yb2xlIn0.EnOpR72H05QVdHsjZPsw2IC3vSnOUcwOWd8MreYffR4
```

**Usage**: Backend database operations (full access, bypasses RLS)

### JWT Secret
```
XPJ0e4UUK0liOadb9nuky0DJHqtjeOKG
```

**Usage**: Token signing/verification (keep highly secure)

---

## Environment Variable Configuration

### Backend (.env)
```bash
# Supabase Configuration
SUPABASE_URL=https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/
SUPABASE_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoic2VydmljZV9yb2xlIn0.EnOpR72H05QVdHsjZPsw2IC3vSnOUcwOWd8MreYffR4

# Application Settings
DEBUG=false
APP_NAME=Workshop Document Processor
VERSION=1.0.0

# CORS Settings
ALLOWED_ORIGINS=["https://your-app.ondigitalocean.app"]

# File Processing
MAX_FILE_SIZE=10485760
PROCESSING_TIMEOUT=300
DEFAULT_OCR_ENABLED=false
DEFAULT_PROCESSING_MODE=fast
```

### Frontend (.env.local)
```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoiYW5vbiJ9.9N2FNNrBisKwF-AIj-jdeB4pGRNNBol-kXTNL3RCBFY

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## DigitalOcean App Platform Configuration

### Update `.digitalocean/app.yaml`

**Frontend Service (lines 22-34):**
```yaml
envs:
  - key: NEXT_PUBLIC_API_URL
    value: ${backend.PUBLIC_URL}
    type: SECRET
  - key: NEXT_PUBLIC_SUPABASE_URL
    value: https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/
    type: SECRET
  - key: NEXT_PUBLIC_SUPABASE_ANON_KEY
    value: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoiYW5vbiJ9.9N2FNNrBisKwF-AIj-jdeB4pGRNNBol-kXTNL3RCBFY
    type: SECRET
  - key: NODE_ENV
    value: production
```

**Backend Service (lines 69-85):**
```yaml
envs:
  - key: SUPABASE_URL
    value: https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/
    type: SECRET
  - key: SUPABASE_KEY
    value: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoic2VydmljZV9yb2xlIn0.EnOpR72H05QVdHsjZPsw2IC3vSnOUcwOWd8MreYffR4
    type: SECRET
  - key: MAX_FILE_SIZE
    value: "10485760"
  - key: PROCESSING_TIMEOUT
    value: "300"
  - key: ALLOWED_ORIGINS
    value: ${frontend.PUBLIC_URL}
    type: SECRET
  - key: ENVIRONMENT
    value: staging
```

---

## Security Checklist

### ✅ Safe Practices
- [x] Anon key used only in frontend (limited by RLS policies)
- [x] Service role key used only in backend (never exposed to client)
- [x] JWT secret never committed to repository
- [x] All keys marked as `type: SECRET` in DigitalOcean
- [x] CORS configured with specific allowed origins

### ⚠️ Important Reminders
- **Never commit this file** to public repositories
- **Rotate keys** if accidentally exposed
- **Use different credentials** for production if possible
- **Monitor access logs** in Supabase dashboard
- **Enable rate limiting** for production deployment

---

## Network Requirements

### Coolify/Self-Hosted Supabase
Ensure your Coolify instance allows:
- ✅ Inbound HTTPS (443) from DigitalOcean IP ranges
- ✅ SSL certificate is valid and not self-signed
- ✅ No IP whitelist restrictions (or whitelist DigitalOcean)

### Test Connectivity
```bash
# From local machine
curl https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/

# Test with anon key
curl -H "apikey: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
     https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/rest/v1/documents
```

---

## Quick Deployment Checklist

- [ ] Copy anon key to `.digitalocean/app.yaml` (line 30)
- [ ] Verify service role key in `.digitalocean/app.yaml` (line 73)
- [ ] Test network connectivity to self-hosted Supabase
- [ ] Verify database migration is applied (`documents` table exists)
- [ ] Verify storage buckets exist (`uploads`, `processed`)
- [ ] Push to GitHub repository
- [ ] Deploy via DigitalOcean App Platform
- [ ] Test health check: `https://your-app.ondigitalocean.app/api/health`
- [ ] Run smoke test with sample PDF

---

## Support

If you encounter issues:
1. Verify Coolify firewall settings
2. Check Supabase logs in Coolify dashboard
3. Test API connectivity from external network
4. Review DigitalOcean deployment logs

---

**Last Updated**: 2025-10-04  
**Instance**: Self-hosted via Coolify  
**Status**: Ready for deployment