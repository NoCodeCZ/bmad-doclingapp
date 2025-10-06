import { useState, useCallback } from 'react';

export interface ErrorState {
  code?: string;
  message: string;
  details?: string;
  timestamp?: string;
  requestId?: string;
}

export interface UseErrorHandlerReturn {
  error: ErrorState | null;
  setError: (error: ErrorState | null) => void;
  clearError: () => void;
  retryAction?: () => void;
  setRetryAction: (action: (() => void) | undefined) => void;
}

/**
 * useErrorHandler Hook
 *
 * Manages error state with retry functionality for the application.
 * Implements AC 7: Error state management with reset functionality
 */
export const useErrorHandler = (): UseErrorHandlerReturn => {
  const [error, setErrorState] = useState<ErrorState | null>(null);
  const [retryAction, setRetryActionState] = useState<(() => void) | undefined>(
    undefined
  );

  const setError = useCallback((errorData: ErrorState | null) => {
    if (errorData) {
      setErrorState({
        ...errorData,
        timestamp: errorData.timestamp || new Date().toISOString(),
      });
    } else {
      setErrorState(null);
    }
  }, []);

  const clearError = useCallback(() => {
    setErrorState(null);
    setRetryActionState(undefined);
  }, []);

  const setRetryAction = useCallback((action: (() => void) | undefined) => {
    setRetryActionState(() => action);
  }, []);

  return {
    error,
    setError,
    clearError,
    retryAction,
    setRetryAction,
  };
};
