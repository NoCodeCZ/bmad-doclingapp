# Upload Failure Troubleshooting Guide

## Quick Checklist

Before debugging, verify these are set up correctly in Coolify:

### 1. Environment Variables (in Coolify)
Make sure these are set:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key-here
SUPABASE_ANON_KEY=your-anon-key-here
MAX_FILE_SIZE=52428800
PROCESSING_TIMEOUT=600
ENVIRONMENT=production
```

### 2. Supabase Buckets Must Exist

**CRITICAL:** You need to create the storage buckets in Supabase!

1. Go to your Supabase project dashboard
2. Navigate to **Storage** in the left sidebar
3. Create two buckets:
   - **uploads** (for uploaded files)
   - **processed** (for markdown outputs)
4. Both should be **private** (not public)

### 3. Database Table Must Exist

Run this SQL in Supabase SQL Editor:

```sql
-- See: backend/supabase/migrations/001_create_documents_table.sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    status TEXT NOT NULL,
    processing_options JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    completed_at TIMESTAMP WITH TIME ZONE
);
```

---

## Common Error Messages

### "Supabase client not configured"
**Cause:** SUPABASE_URL or SUPABASE_KEY not set in Coolify environment variables
**Fix:** Add the environment variables in Coolify dashboard

### "Bucket not found" or "Storage permission denied"
**Cause:** Storage buckets don't exist or have wrong permissions
**Fix:**
1. Create `uploads` and `processed` buckets in Supabase Storage
2. Make sure they are **private** (not public)
3. Check RLS policies allow service_role access

### "Failed to create document record"
**Cause:** Documents table doesn't exist in database
**Fix:** Run the migration SQL (see section 3 above)

### "CORS policy" error in browser console
**Cause:** Frontend can't reach backend due to CORS restrictions
**Fix:** Already handled - backend uses `ALLOWED_ORIGINS=*`

### "Network error" or "Failed to fetch"
**Cause:** Frontend can't reach backend API
**Fix:**
1. Check that all 3 containers are running in Coolify:
   - nginx (should be healthy)
   - backend (should be healthy)
   - frontend (should be healthy)
2. Check nginx logs for routing issues

---

## How to Debug

### Step 1: Check Container Logs

In Coolify, check logs for each service:

**Backend logs** (look for):
```
INFO: Starting Uvicorn server
INFO: Application startup complete
```

**Frontend logs** (look for):
```
✓ Ready in X ms
```

**Nginx logs** (look for):
```
nginx: [emerg] or [error]
```

### Step 2: Test Backend Health Endpoint

```bash
curl https://your-domain.com/api/health
```

Should return:
```json
{"status":"ok","timestamp":"..."}
```

### Step 3: Check Browser Console

1. Open browser DevTools (F12)
2. Go to **Console** tab
3. Try to upload a file
4. Look for errors:
   - Red messages indicate errors
   - Check **Network** tab for failed requests

### Step 4: Test Upload Directly

You can test the backend directly using curl:

```bash
curl -X POST https://your-domain.com/api/upload \
  -F "file=@test.pdf" \
  -F "ocr_enabled=false" \
  -F "processing_mode=fast"
```

Expected responses:
- **Success (200)**: `{"id":"...","filename":"test.pdf","status":"queued"}`
- **File too large (400)**: `{"error":{"code":"FILE_TOO_LARGE",...}}`
- **Unsupported type (400)**: `{"error":{"code":"UNSUPPORTED_FORMAT",...}}`
- **Supabase error (400)**: `{"error":{"code":"SUPABASE_ERROR",...}}`

---

## Quick Fixes

### If buckets are missing:
1. Log into your Supabase dashboard
2. Go to **Storage**
3. Click **New bucket**
4. Create `uploads` (private)
5. Create `processed` (private)

### If table is missing:
1. Go to **SQL Editor** in Supabase
2. Copy content from `backend/supabase/migrations/001_create_documents_table.sql`
3. Paste and **Run**

### If environment variables are wrong:
1. In Coolify, go to your application
2. Click **Environment Variables**
3. Verify all 5 variables are set correctly
4. **Redeploy** after making changes

---

## Still Not Working?

Check these in order:

1. **All containers running?** → Check Coolify service status
2. **Health endpoint works?** → Test `/api/health`
3. **Buckets exist?** → Check Supabase Storage
4. **Table exists?** → Check Supabase Database
5. **Environment variables set?** → Check Coolify settings
6. **File size under 50MB?** → Check file size
7. **Supported file type?** → PDF, DOCX, PPTX, XLSX only

If all above are OK, check:
- Backend logs for Python errors
- Frontend browser console for JavaScript errors
- Nginx logs for routing errors
