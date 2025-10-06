/**
 * Supabase client configuration for frontend
 */
import { createClient } from '@supabase/supabase-js';
import { Database } from '@/types/database';

let supabaseClient: any = null;

const getSupabaseClient = () => {
  if (supabaseClient) return supabaseClient;

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  // Create a mock client for development when env vars are not set
  const createMockClient = () => ({
    from: () => ({
      select: () => ({
        eq: () => ({
          single: () => Promise.resolve({ data: null, error: null }),
        }),
        insert: () => Promise.resolve({ data: null, error: new Error('Supabase not configured') }),
        update: () => Promise.resolve({ data: null, error: new Error('Supabase not configured') }),
        delete: () => Promise.resolve({ data: null, error: new Error('Supabase not configured') }),
      }),
    }),
    storage: {
      from: () => ({
        upload: () => Promise.resolve({ data: null, error: new Error('Supabase not configured') }),
        download: () => Promise.resolve({ data: null, error: new Error('Supabase not configured') }),
        getPublicUrl: () => ({ data: { publicUrl: '' } }),
        createSignedUrl: () => Promise.resolve({ data: null, error: new Error('Supabase not configured') }),
        remove: () => Promise.resolve({ data: null, error: new Error('Supabase not configured') }),
      }),
    },
  });

  if (supabaseUrl && supabaseAnonKey && supabaseUrl !== 'https://placeholder.supabase.co') {
    supabaseClient = createClient<Database>(supabaseUrl, supabaseAnonKey, {
      auth: {
        persistSession: false,
        autoRefreshToken: false,
      },
    });
  } else {
    supabaseClient = createMockClient();
  }

  return supabaseClient;
};

export const supabase = getSupabaseClient();

// Storage bucket names
export const STORAGE_BUCKETS = {
  UPLOADS: 'uploads',
  PROCESSED: 'processed',
} as const;

// Helper functions for file operations
export const generateFilePath = (documentId: string, filename: string): string => {
  const timestamp = Date.now();
  const extension = filename.split('.').pop();
  const baseName = filename.replace(`.${extension}`, '');
  return `${documentId}/${baseName}-${timestamp}.${extension}`;
};

export const generateProcessedFilePath = (documentId: string, originalFilename: string): string => {
  const baseName = originalFilename.replace(/\.[^/.]+$/, ''); // Remove extension
  return `${documentId}/${baseName}.md`;
};

// File validation helpers
export const ALLOWED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
} as const;

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export const isFileTypeAllowed = (file: File): boolean => {
  return Object.keys(ALLOWED_FILE_TYPES).indexOf(file.type) !== -1;
};

export const isFileSizeAllowed = (file: File): boolean => {
  return file.size <= MAX_FILE_SIZE;
};

export const getFileExtension = (filename: string): string => {
  return filename.split('.').pop()?.toLowerCase() || '';
};

export const validateFile = (file: File): { valid: boolean; error?: string } => {
  if (!isFileTypeAllowed(file)) {
    return {
      valid: false,
      error: `Unsupported file type. Allowed types: PDF, DOCX, PPTX, XLSX`,
    };
  }

  if (!isFileSizeAllowed(file)) {
    return {
      valid: false,
      error: `File too large. Maximum size is 10MB`,
    };
  }

  return { valid: true };
};

// Database helpers
export const createDocumentRecord = async (
  filename: string,
  processingOptions: {
    ocr_enabled: boolean;
    processing_mode: 'fast' | 'quality';
  }
) => {
  const { data, error } = await supabase
    .from('documents')
    .insert({
      filename,
      status: 'queued',
      processing_options: processingOptions,
    })
    .select()
    .single();

  if (error) {
    throw new Error(`Failed to create document record: ${error.message}`);
  }

  return data;
};

export const getDocument = async (documentId: string) => {
  const { data, error } = await supabase
    .from('documents')
    .select('*')
    .eq('id', documentId)
    .single();

  if (error && error.code !== 'PGRST116') {
    throw new Error(`Failed to get document: ${error.message}`);
  }

  return data;
};

export const updateDocumentStatus = async (
  documentId: string,
  status: 'queued' | 'processing' | 'complete' | 'failed',
  errorMessage?: string
) => {
  const updateData: any = { status };

  if (status === 'complete') {
    updateData.completed_at = new Date().toISOString();
  }

  if (errorMessage) {
    updateData.error_message = errorMessage;
  }

  const { data, error } = await supabase
    .from('documents')
    .update(updateData)
    .eq('id', documentId)
    .select()
    .single();

  if (error) {
    throw new Error(`Failed to update document status: ${error.message}`);
  }

  return data;
};

// Storage helpers
export const uploadFile = async (
  bucket: string,
  path: string,
  file: File
): Promise<{ data: any; error: any }> => {
  return await supabase.storage.from(bucket).upload(path, file, {
    cacheControl: '3600',
    upsert: false,
  });
};

export const getPublicUrl = (bucket: string, path: string) => {
  return supabase.storage.from(bucket).getPublicUrl(path);
};

export const createSignedUrl = async (
  bucket: string,
  path: string,
  expiresIn: number = 3600
) => {
  const { data, error } = await supabase.storage
    .from(bucket)
    .createSignedUrl(path, expiresIn);

  if (error) {
    throw new Error(`Failed to create signed URL: ${error.message}`);
  }

  return data;
};

export const deleteFile = async (bucket: string, path: string) => {
  return await supabase.storage.from(bucket).remove([path]);
};