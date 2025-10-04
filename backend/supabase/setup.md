# Supabase Setup Guide

This guide walks you through setting up Supabase for the Workshop Document Processor project.

## Prerequisites

- A Supabase account (https://supabase.com)
- Node.js and Python installed locally

## Step 1: Create a New Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Project Name**: `workshop-document-processor`
   - **Database Password**: Generate a strong password and save it
   - **Region**: Choose the closest region to your users
5. Click "Create new project"
6. Wait for the project to be provisioned (2-3 minutes)

## Step 2: Get Project Credentials

1. In your Supabase project dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (looks like `https://xxxxxxxx.supabase.co`)
   - **anon public** key (starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)
   - **service_role** key (starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

## Step 3: Set Up Database Schema

1. In your Supabase project, go to **SQL Editor**
2. Click "New query"
3. Copy and paste the contents of `backend/supabase/migrations/001_create_documents_table.sql`
4. Click "Run" to execute the migration
5. Verify that:
   - The `documents` table was created
   - Two storage buckets (`uploads` and `processed`) were created
   - RLS policies were enabled

## Step 4: Configure Environment Variables

### Backend (.env)

Create a `.env` file in the `backend` directory:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-service-role-key-here

# Application Settings
DEBUG=true
APP_NAME=Workshop Document Processor
VERSION=1.0.0

# CORS Settings
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:3001"]

# File Processing
MAX_FILE_SIZE=10485760
PROCESSING_TIMEOUT=300
DEFAULT_OCR_ENABLED=false
DEFAULT_PROCESSING_MODE=fast
```

### Frontend (.env.local)

Update the `frontend/.env.local` file:

```bash
# Local development environment variables
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Step 5: Verify Storage Buckets

1. In Supabase, go to **Storage**
2. You should see two buckets:
   - `uploads` (for original files)
   - `processed` (for markdown output)
3. Both buckets should be private (not public)

## Step 6: Test Database Connection

### Backend Test

Run the backend server and test the health endpoint:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Test with:
```bash
curl http://localhost:8000/api/health
```

### Frontend Test

Run the frontend server:

```bash
cd frontend
npm run dev
```

Visit http://localhost:3000 and check the browser console for any Supabase connection errors.

## Step 7: Verify RLS Policies

1. In Supabase, go to **Authentication** → **Policies**
2. Check that the following policies exist:
   - `Allow all operations on documents` on the `documents` table
   - `Allow all operations on uploads bucket` on storage
   - `Allow all operations on processed bucket` on storage

## Step 8: Test File Upload (Optional)

You can test the complete setup by:

1. Starting both backend and frontend servers
2. Using the application to upload a test file
3. Checking in Supabase that:
   - A record appears in the `documents` table
   - The file appears in the `uploads` storage bucket

## Production Environment

For production deployment:

1. Create a separate Supabase project for production
2. Update environment variables in your hosting platform (DigitalOcean)
3. Run the same migration script on the production database
4. Ensure CORS settings include your production domain

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure your frontend URL is in the `ALLOWED_ORIGINS` list
2. **Storage Permission Denied**: Check that RLS policies are correctly configured
3. **Database Connection Failed**: Verify Supabase URL and keys are correct
4. **File Upload Fails**: Check that storage buckets exist and have correct permissions

### Debugging

1. Check browser console for frontend errors
2. Check backend logs for database/storage errors
3. Use Supabase dashboard to verify data and files
4. Test SQL queries directly in the Supabase SQL Editor

## Security Notes

- The service role key should never be exposed to the frontend
- For production, consider implementing proper authentication
- Storage buckets are configured as private for security
- RLS policies allow all operations for MVP (workshop use case)

## Next Steps

After setup is complete:

1. Test the document upload and processing workflow
2. Verify that files are stored correctly in both buckets
3. Test the status polling and download functionality
4. Proceed with the remaining implementation tasks