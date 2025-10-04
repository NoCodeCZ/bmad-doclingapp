# Supabase Integration Guide

This document provides comprehensive information about the Supabase integration for the Workshop Document Processor project.

## Overview

Supabase is used as the backend database and storage solution for the Workshop Document Processor. It provides:

- **PostgreSQL Database**: Stores document metadata, processing status, and error logs
- **Object Storage**: Private buckets for original uploads and processed files
- **Real-time Subscriptions**: Future enhancement for live status updates
- **Row Level Security (RLS)**: Data protection and access control

## Architecture

### Database Schema

The application uses a single `documents` table with the following structure:

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('queued', 'processing', 'complete', 'failed')),
    processing_options JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    file_size BIGINT,
    content_type TEXT,
    processed_file_path TEXT,
    original_file_path TEXT
);
```

### Storage Buckets

Two private storage buckets are configured:

1. **`uploads`**: Stores original uploaded files
   - File size limit: 10MB
   - Allowed MIME types: PDF, DOCX, PPTX, XLSX
   - Access: Private (backend only)

2. **`processed`**: Stores processed markdown files
   - File size limit: 10MB
   - Allowed MIME types: text/markdown, text/plain
   - Access: Private (backend only)

### Security Model

- **Row Level Security (RLS)**: Enabled on all tables
- **Private Buckets**: All storage buckets are private
- **Service Role Authentication**: Backend uses service role key for full access
- **Anonymous Access**: Frontend uses anon key with limited permissions

## Configuration

### Environment Variables

#### Backend (.env)

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-service-role-key-here
```

#### Frontend (.env.local)

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
```

### Client Configuration

#### Backend (Python)

```python
from supabase import create_client

supabase_client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_KEY
)
```

#### Frontend (TypeScript)

```typescript
import { createClient } from '@supabase/supabase-js';

export const supabase = createClient<Database>(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);
```

## Database Operations

### Document Lifecycle

1. **Upload**: Document record created with status `queued`
2. **Processing**: Status updated to `processing`
3. **Completion**: Status updated to `complete` with `completed_at` timestamp
4. **Error**: Status updated to `failed` with `error_message`

### Common Operations

#### Create Document

```python
result = supabase.table('documents').insert({
    'filename': 'document.pdf',
    'status': 'queued',
    'processing_options': {'ocr_enabled': False, 'processing_mode': 'fast'}
}).execute()
```

#### Update Status

```python
result = supabase.table('documents').update({
    'status': 'complete',
    'completed_at': 'now()'
}).eq('id', document_id).execute()
```

#### Query Documents

```python
result = supabase.table('documents').select('*').eq('status', 'complete').execute()
```

## Storage Operations

### File Upload

```python
result = supabase.storage.from_('uploads').upload(
    path='document-id/original.pdf',
    file=file_content,
    file_options={'content-type': 'application/pdf'}
)
```

### File Download

```python
result = supabase.storage.from_('processed').download('document-id/processed.md')
```

### Signed URLs

```python
result = supabase.storage.from_('processed').create_signed_url(
    path='document-id/processed.md',
    expires_in=3600
)
```

## Row Level Security Policies

### Documents Table

```sql
-- Allow all operations for workshop MVP (no authentication)
CREATE POLICY "Allow all operations on documents" ON documents
    FOR ALL USING (true)
    WITH CHECK (true);
```

### Storage Buckets

```sql
-- Allow all operations on uploads bucket
CREATE POLICY "Allow all operations on uploads bucket" ON storage.objects
    FOR ALL USING (bucket_id = 'uploads')
    WITH CHECK (bucket_id = 'uploads');

-- Allow all operations on processed bucket
CREATE POLICY "Allow all operations on processed bucket" ON storage.objects
    FOR ALL USING (bucket_id = 'processed')
    WITH CHECK (bucket_id = 'processed');
```

## Migration Scripts

### Initial Setup

Run the initial migration to create the database schema:

```bash
# Execute in Supabase SQL Editor
-- File: backend/supabase/migrations/001_create_documents_table.sql
```

### Automated Migrations

For production deployments, consider using Supabase CLI:

```bash
# Install Supabase CLI
npm install -g supabase

# Link to project
supabase link --project-ref your-project-id

# Push migrations
supabase db push
```

## Monitoring and Maintenance

### Health Checks

The health check endpoint (`/api/health`) verifies:
- Database connectivity
- Storage bucket access
- Overall system status

### Statistics

A database view provides document processing statistics:

```sql
CREATE VIEW document_stats AS
SELECT 
    status,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_processing_time_seconds
FROM documents 
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY status;
```

### Cleanup Strategies

For production maintenance, consider:

1. **Automatic Cleanup**: Remove old documents after 30 days
2. **Storage Limits**: Monitor storage usage and implement quotas
3. **Error Logging**: Regular review of failed processing attempts

## Performance Optimization

### Database Indexes

```sql
-- Performance indexes
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created_at ON documents(created_at);
CREATE INDEX idx_documents_filename ON documents(filename);
```

### Connection Pooling

- Use connection pooling in production
- Configure appropriate pool size based on expected load
- Monitor connection usage during peak times

### Storage Optimization

- Implement file compression for processed markdown
- Use CDN distribution for frequently accessed files
- Monitor storage bandwidth usage

## Security Considerations

### Key Management

- **Service Role Key**: Never expose to frontend
- **Anon Key**: Limited permissions for frontend access
- **Environment Variables**: Store securely in deployment platform

### Data Protection

- **Private Buckets**: All files stored in private buckets
- **Signed URLs**: Temporary access for downloads
- **Input Validation**: Validate all file uploads and parameters

### Access Control

- **RLS Policies**: Implement appropriate access restrictions
- **CORS Configuration**: Limit allowed origins
- **Rate Limiting**: Consider implementing for production

## Troubleshooting

### Common Issues

1. **Connection Failed**: Check Supabase URL and keys
2. **Permission Denied**: Verify RLS policies and bucket permissions
3. **File Upload Failed**: Check file size and type restrictions
4. **Storage Access**: Ensure buckets exist and are properly configured

### Debugging Tools

1. **Supabase Dashboard**: Monitor database and storage usage
2. **Application Logs**: Check backend logs for detailed error information
3. **Health Endpoint**: Verify system connectivity
4. **Network Tools**: Test API endpoints and storage access

### Performance Issues

1. **Slow Queries**: Check database query performance
2. **Storage Delays**: Monitor storage operation times
3. **Connection Limits**: Verify connection pool configuration
4. **Resource Usage**: Monitor CPU and memory usage

## Future Enhancements

### Authentication

- Implement user authentication for multi-tenant usage
- Add user-specific document isolation
- Implement OAuth providers (Google, GitHub)

### Real-time Features

- WebSocket connections for live status updates
- Real-time processing progress indicators
- Collaborative document processing

### Advanced Features

- Document versioning and history
- Batch processing capabilities
- Advanced search and filtering
- Export to multiple formats

## Support

For issues related to Supabase integration:

1. Check the [Supabase Documentation](https://supabase.com/docs)
2. Review the [Troubleshooting Guide](#troubleshooting)
3. Check application logs for detailed error information
4. Verify environment variables and configuration