/**
 * useErrorHandler Hook Tests
 *
 * Tests AC 7: Error state management with reset functionality
 */

import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useErrorHandler } from '@/hooks/useErrorHandler';

describe('useErrorHandler', () => {
  it('should initialize with no error', () => {
    const { result } = renderHook(() => useErrorHandler());

    expect(result.current.error).toBeNull();
    expect(result.current.retryAction).toBeUndefined();
  });

  it('should set error with automatic timestamp', () => {
    const { result } = renderHook(() => useErrorHandler());

    act(() => {
      result.current.setError({
        code: 'TEST_ERROR',
        message: 'Test error message',
      });
    });

    expect(result.current.error).not.toBeNull();
    expect(result.current.error?.code).toBe('TEST_ERROR');
    expect(result.current.error?.message).toBe('Test error message');
    expect(result.current.error?.timestamp).toBeDefined();
  });

  it('should preserve timestamp when provided', () => {
    const { result } = renderHook(() => useErrorHandler());
    const customTimestamp = '2025-10-06T12:00:00Z';

    act(() => {
      result.current.setError({
        code: 'TEST_ERROR',
        message: 'Test error message',
        timestamp: customTimestamp,
      });
    });

    expect(result.current.error?.timestamp).toBe(customTimestamp);
  });

  it('should clear error', () => {
    const { result } = renderHook(() => useErrorHandler());

    // Set error
    act(() => {
      result.current.setError({
        code: 'TEST_ERROR',
        message: 'Test error message',
      });
    });

    expect(result.current.error).not.toBeNull();

    // Clear error
    act(() => {
      result.current.clearError();
    });

    expect(result.current.error).toBeNull();
    expect(result.current.retryAction).toBeUndefined();
  });

  it('should set and execute retry action', () => {
    const { result } = renderHook(() => useErrorHandler());
    let retryExecuted = false;

    const retryFn = () => {
      retryExecuted = true;
    };

    act(() => {
      result.current.setRetryAction(retryFn);
    });

    expect(result.current.retryAction).toBeDefined();

    // Execute retry action
    act(() => {
      result.current.retryAction?.();
    });

    expect(retryExecuted).toBe(true);
  });

  it('should handle error with all properties', () => {
    const { result } = renderHook(() => useErrorHandler());

    act(() => {
      result.current.setError({
        code: 'FILE_TOO_LARGE',
        message: 'File too large',
        details: 'Maximum size is 10MB',
        requestId: 'req-123',
      });
    });

    expect(result.current.error?.code).toBe('FILE_TOO_LARGE');
    expect(result.current.error?.message).toBe('File too large');
    expect(result.current.error?.details).toBe('Maximum size is 10MB');
    expect(result.current.error?.requestId).toBe('req-123');
  });

  it('should allow setting error to null explicitly', () => {
    const { result } = renderHook(() => useErrorHandler());

    // Set error
    act(() => {
      result.current.setError({
        code: 'TEST_ERROR',
        message: 'Test error message',
      });
    });

    expect(result.current.error).not.toBeNull();

    // Set error to null
    act(() => {
      result.current.setError(null);
    });

    expect(result.current.error).toBeNull();
  });

  it('should clear retry action when clearing error', () => {
    const { result } = renderHook(() => useErrorHandler());

    act(() => {
      result.current.setError({
        code: 'TEST_ERROR',
        message: 'Test error message',
      });
      result.current.setRetryAction(() => {});
    });

    expect(result.current.error).not.toBeNull();
    expect(result.current.retryAction).toBeDefined();

    act(() => {
      result.current.clearError();
    });

    expect(result.current.error).toBeNull();
    expect(result.current.retryAction).toBeUndefined();
  });
});
