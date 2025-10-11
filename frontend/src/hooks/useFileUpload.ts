import { useState, useCallback } from 'react';
import { ProcessingOptions, Document } from '@/types/database';

interface UseFileUploadState {
  isUploading: boolean;
  uploadProgress: number;
  error: string | null;
  documentId: string | null;
}

interface UseFileUploadReturn extends UseFileUploadState {
  uploadFile: (file: File, options: ProcessingOptions) => Promise<string | null>;
  reset: () => void;
}

// File validation constants
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB in bytes
const SUPPORTED_FORMATS = ['pdf', 'docx', 'pptx', 'xlsx'] as const;
const SUPPORTED_MIME_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
] as const;

/**
 * Validates file before upload
 * Implements AC 2: File validation errors show specific guidance
 * Implements AC 3: Unsupported format errors include allowed formats
 */
const validateFile = (file: File): { valid: boolean; error?: string } => {
  // File size validation (AC 2)
  if (file.size > MAX_FILE_SIZE) {
    const fileSizeMB = (file.size / (1024 * 1024)).toFixed(1);
    return {
      valid: false,
      error: `File too large (${fileSizeMB}MB) - maximum size is 50MB. Try compressing your ${getFileExtension(file.name).toUpperCase()} or splitting into multiple files.`,
    };
  }

  // File type validation (AC 3)
  const extension = getFileExtension(file.name);
  const isValidExtension = SUPPORTED_FORMATS.includes(extension as any);
  const isValidMimeType = SUPPORTED_MIME_TYPES.includes(file.type as any);

  if (!isValidExtension && !isValidMimeType) {
    return {
      valid: false,
      error: `Cannot process .${extension} files - supported formats: ${SUPPORTED_FORMATS.map(f => f.toUpperCase()).join(', ')}.`,
    };
  }

  return { valid: true };
};

/**
 * Gets file extension from filename
 */
const getFileExtension = (filename: string): string => {
  const parts = filename.split('.');
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : '';
};

/**
 * Formats file size for display
 */
const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
};

export const useFileUpload = (): UseFileUploadReturn => {
  const [state, setState] = useState<UseFileUploadState>({
    isUploading: false,
    uploadProgress: 0,
    error: null,
    documentId: null,
  });

  const reset = useCallback(() => {
    setState({
      isUploading: false,
      uploadProgress: 0,
      error: null,
      documentId: null,
    });
  }, []);

  const uploadFile = useCallback(async (
    file: File,
    options: ProcessingOptions
  ): Promise<string | null> => {
    // Validate file before upload
    const validation = validateFile(file);
    if (!validation.valid) {
      setState(prev => ({
        ...prev,
        isUploading: false,
        uploadProgress: 0,
        error: validation.error || 'File validation failed',
        documentId: null,
      }));
      return null;
    }

    setState(prev => ({
      ...prev,
      isUploading: true,
      uploadProgress: 0,
      error: null,
      documentId: null,
    }));

    try {
      // Create FormData for multipart upload
      const formData = new FormData();
      formData.append('file', file);
      formData.append('ocr_enabled', options.ocr_enabled.toString());
      formData.append('processing_mode', options.processing_mode);

      // Update progress
      setState(prev => ({ ...prev, uploadProgress: 10 }));

      // Make API call to upload endpoint
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      // Don't add /api prefix if apiUrl already ends with /api (nginx proxy setup)
      const endpoint = apiUrl.endsWith('/api')
        ? `${apiUrl}/upload`
        : `${apiUrl}/api/upload`;
      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Upload failed' }));

        // Parse structured error response
        if (errorData.error) {
          throw new Error(errorData.error.message || 'Upload failed');
        }

        throw new Error(errorData.detail || errorData.message || 'Upload failed');
      }

      const result = await response.json();

      // Update progress and state
      setState(prev => ({
        ...prev,
        isUploading: false,
        uploadProgress: 100,
        error: null,
        documentId: result.id,
      }));

      return result.id;

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed';

      setState(prev => ({
        ...prev,
        isUploading: false,
        uploadProgress: 0,
        error: errorMessage,
        documentId: null,
      }));

      return null;
    }
  }, []);

  return {
    ...state,
    uploadFile,
    reset,
  };
};