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
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Upload failed' }));
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