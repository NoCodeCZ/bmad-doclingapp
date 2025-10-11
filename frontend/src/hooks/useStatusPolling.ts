import { useState, useCallback, useRef, useEffect } from 'react';

export interface ProcessingOptions {
  mode: 'fast' | 'quality';
  ocr_enabled: boolean;
}

export interface StatusState {
  status: 'uploading' | 'queued' | 'processing' | 'finalizing' | 'complete' | 'failed';
  progress: number; // 0-100
  progress_stage: string;
  elapsed_time: number; // seconds
  estimated_time_remaining: number; // seconds
  filename: string;
  processing_options: ProcessingOptions;
  error_message?: string | null;
  download_url?: string | null;
}

export interface UseStatusPollingReturn {
  status: StatusState | null;
  isPolling: boolean;
  error: string | null;
  startPolling: (documentId: string) => void;
  stopPolling: () => void;
}

const POLL_INTERVAL = 2000; // 2 seconds
const MAX_RETRIES = 3;
const TERMINAL_STATES = ['complete', 'failed'];

/**
 * Hook for polling document processing status with automatic retry logic.
 *
 * Features:
 * - Polls every 2 seconds for status updates
 * - Automatically stops polling on terminal states (complete/failed)
 * - Exponential backoff retry on errors (2s, 4s, 8s)
 * - Proper cleanup on unmount
 * - Time estimation based on processing options
 */
export const useStatusPolling = (): UseStatusPollingReturn => {
  const [status, setStatus] = useState<StatusState | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const retryCountRef = useRef(0);
  const documentIdRef = useRef<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  /**
   * Calculate estimated time remaining based on processing options and elapsed time
   */
  const calculateEstimatedTime = useCallback((
    processingOptions: ProcessingOptions,
    elapsedTime: number,
    currentStatus: string
  ): number => {
    // Base time estimates
    const baseTime = processingOptions.mode === 'fast' ? 30 : 90;
    const ocrMultiplier = processingOptions.ocr_enabled ? 2 : 1;
    const estimatedTotal = baseTime * ocrMultiplier;

    // Return 0 for terminal states
    if (TERMINAL_STATES.includes(currentStatus)) {
      return 0;
    }

    // Adjust if exceeding estimate
    if (elapsedTime > estimatedTotal) {
      // Cap at 5 minutes (300 seconds)
      return Math.min(estimatedTotal * 1.5, 300);
    }

    // Minimum 5 seconds remaining
    return Math.max(estimatedTotal - elapsedTime, 5);
  }, []);

  /**
   * Transform backend response to StatusState format
   */
  const transformResponse = useCallback((data: any): StatusState => {
    const processingOptions = {
      mode: data.processing_options?.mode || 'fast',
      ocr_enabled: data.processing_options?.ocr_enabled || false,
    };

    const elapsedTime = data.elapsed_time || 0;
    const estimatedTimeRemaining = calculateEstimatedTime(
      processingOptions,
      elapsedTime,
      data.status
    );

    return {
      status: data.status,
      progress: calculateProgress(data.status, elapsedTime, processingOptions),
      progress_stage: data.progress_stage || 'Unknown',
      elapsed_time: elapsedTime,
      estimated_time_remaining: estimatedTimeRemaining,
      filename: data.filename,
      processing_options: processingOptions,
      error_message: data.error_message,
      download_url: data.download_url,
    };
  }, [calculateEstimatedTime]);

  /**
   * Calculate progress percentage based on status and elapsed time
   */
  const calculateProgress = (
    currentStatus: string,
    elapsedTime: number,
    processingOptions: ProcessingOptions
  ): number => {
    if (currentStatus === 'complete') {
      return 100;
    } else if (currentStatus === 'failed') {
      return 0;
    } else if (currentStatus === 'queued') {
      return Math.min(elapsedTime || 0, 10); // 0-10% for queued
    } else if (currentStatus === 'processing') {
      // Estimate based on processing mode and elapsed time
      const baseTime = processingOptions.mode === 'fast' ? 30 : 90;
      const ocrMultiplier = processingOptions.ocr_enabled ? 2 : 1;
      const estimatedTotal = baseTime * ocrMultiplier;

      const progress = 10 + Math.min((elapsedTime || 0) / estimatedTotal * 80, 80);
      return Math.min(Math.round(progress), 95); // Cap at 95% until complete
    }
    return 0;
  };

  /**
   * Poll for status updates with retry logic
   */
  const poll = useCallback(async (documentId: string, attempt: number = 0) => {
    try {
      // Create new AbortController for this request
      abortControllerRef.current = new AbortController();

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      // Don't add /api prefix if apiUrl already ends with /api (nginx proxy setup)
      const endpoint = apiUrl.endsWith('/api')
        ? `${apiUrl}/status/${documentId}`
        : `${apiUrl}/api/status/${documentId}`;
      const response = await fetch(endpoint, {
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      const transformedStatus = transformResponse(data);

      setStatus(transformedStatus);
      setError(null);
      retryCountRef.current = 0; // Reset retry count on success

      // Stop polling for terminal states
      if (TERMINAL_STATES.includes(transformedStatus.status)) {
        setIsPolling(false);
        if (pollingIntervalRef.current) {
          clearTimeout(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
        return;
      }

      // Schedule next poll
      if (isPolling) {
        pollingIntervalRef.current = setTimeout(() => {
          poll(documentId, 0);
        }, POLL_INTERVAL);
      }

    } catch (err) {
      // Ignore aborted requests
      if (err instanceof Error && err.name === 'AbortError') {
        return;
      }

      console.error('Status polling error:', err);

      if (attempt < MAX_RETRIES) {
        // Exponential backoff: 2s, 4s, 8s
        const delay = POLL_INTERVAL * Math.pow(2, attempt);
        console.log(`Retrying in ${delay}ms (attempt ${attempt + 1}/${MAX_RETRIES})`);

        pollingIntervalRef.current = setTimeout(() => {
          poll(documentId, attempt + 1);
        }, delay);
      } else {
        setError('Unable to get status updates. Please refresh the page.');
        setIsPolling(false);
      }
    }
  }, [isPolling, transformResponse]);

  /**
   * Start polling for a document
   */
  const startPolling = useCallback((documentId: string) => {
    // Stop any existing polling
    if (pollingIntervalRef.current) {
      clearTimeout(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }

    // Abort any in-flight requests
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Reset state
    documentIdRef.current = documentId;
    retryCountRef.current = 0;
    setError(null);
    setIsPolling(true);

    // Start polling immediately
    poll(documentId, 0);
  }, [poll]);

  /**
   * Stop polling
   */
  const stopPolling = useCallback(() => {
    setIsPolling(false);

    // Clear polling interval
    if (pollingIntervalRef.current) {
      clearTimeout(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }

    // Abort any in-flight requests
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);

  return {
    status,
    isPolling,
    error,
    startPolling,
    stopPolling,
  };
};
