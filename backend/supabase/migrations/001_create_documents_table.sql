-- Create documents table for tracking document processing jobs
CREATE TABLE IF NOT EXISTS documents (
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

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
CREATE INDEX IF NOT EXISTS idx_documents_filename ON documents(filename);

-- Create storage buckets for file uploads
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'uploads',
    'uploads',
    false,
    10485760, -- 10MB
    ARRAY[
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]
) ON CONFLICT (id) DO NOTHING;

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'processed',
    'processed',
    false,
    10485760, -- 10MB
    ARRAY['text/markdown', 'text/plain']
) ON CONFLICT (id) DO NOTHING;

-- Enable Row Level Security
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for documents table
-- Allow all operations for now (since no authentication required for workshop)
CREATE POLICY "Allow all operations on documents" ON documents
    FOR ALL USING (true)
    WITH CHECK (true);

-- Create RLS policies for storage buckets
-- Allow all operations on uploads bucket
CREATE POLICY "Allow all operations on uploads bucket" ON storage.objects
    FOR ALL USING (bucket_id = 'uploads')
    WITH CHECK (bucket_id = 'uploads');

-- Allow all operations on processed bucket
CREATE POLICY "Allow all operations on processed bucket" ON storage.objects
    FOR ALL USING (bucket_id = 'processed')
    WITH CHECK (bucket_id = 'processed');

-- Create function to update completed_at timestamp
CREATE OR REPLACE FUNCTION update_completed_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'complete' AND OLD.status != 'complete' THEN
        NEW.completed_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update completed_at
CREATE TRIGGER trigger_update_completed_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_completed_at();

-- Create view for document statistics
CREATE OR REPLACE VIEW document_stats AS
SELECT 
    status,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_processing_time_seconds
FROM documents 
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY status;

-- Grant permissions
GRANT ALL ON documents TO authenticated;
GRANT ALL ON documents TO anon;
GRANT ALL ON storage.objects TO authenticated;
GRANT ALL ON storage.objects TO anon;
GRANT SELECT ON document_stats TO authenticated;
GRANT SELECT ON document_stats TO anon;