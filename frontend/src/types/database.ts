/**
 * Database types for Supabase integration
 * Generated types for the documents table and related structures
 */

export type DocumentStatus = 'uploading' | 'queued' | 'processing' | 'finalizing' | 'complete' | 'failed';

export type ProcessingMode = 'fast' | 'quality';

export interface ProcessingOptions {
  ocr_enabled: boolean;
  processing_mode: ProcessingMode;
}

export interface Document {
  id: string;
  filename: string;
  status: DocumentStatus;
  processing_options: ProcessingOptions;
  created_at: string;
  completed_at: string | null;
  error_message: string | null;
  file_size: number | null;
  content_type: string | null;
  processed_file_path: string | null;
  original_file_path: string | null;
}

export interface DocumentUpload {
  filename: string;
  file_size: number;
  processing_options: ProcessingOptions;
}

export interface DocumentResponse {
  id: string;
  filename: string;
  status: DocumentStatus;
}

export interface DocumentStatusResponse {
  id: string;
  filename: string;
  status: DocumentStatus;
  processing_options: ProcessingOptions;
  created_at: string;
  completed_at: string | null;
  error_message: string | null;
  download_url?: string;
  progress_stage?: 'uploading' | 'queued' | 'processing' | 'finalizing';
  elapsed_time?: number;
}

export interface DocumentStats {
  status: DocumentStatus;
  count: number;
  avg_processing_time_seconds: number | null;
}

// Database table types
export interface Database {
  public: {
    Tables: {
      documents: {
        Row: Document;
        Insert: Omit<Document, 'id' | 'created_at' | 'completed_at'>;
        Update: Partial<Document>;
      };
    };
    Views: {
      document_stats: {
        Row: DocumentStats;
      };
    };
    Functions: {
      update_completed_at: {
        Args: Record<PropertyKey, never>;
        Returns: void;
      };
    };
  };
}

// Storage bucket types
export interface StorageBucket {
  id: string;
  name: string;
  public: boolean;
  file_size_limit: number;
  allowed_mime_types: string[];
}

export interface StorageObject {
  id: string;
  bucket_id: string;
  name: string;
  owner: string | null;
  created_at: string;
  updated_at: string;
  last_accessed_at: string | null;
  metadata: Record<string, any> | null;
}

// API response types
export interface ApiResponse<T = any> {
  data?: T;
  error?: {
    message: string;
    code?: string;
    details?: any;
  };
}

export interface UploadResponse extends ApiResponse<DocumentResponse> {}
export interface StatusResponse extends ApiResponse<DocumentStatusResponse> {}
export interface DownloadResponse extends ApiResponse<{ url: string }> {}

// Error types
export interface DocumentError {
  message: string;
  code?: string;
  type?: 'validation' | 'processing' | 'storage' | 'network';
  details?: any;
}