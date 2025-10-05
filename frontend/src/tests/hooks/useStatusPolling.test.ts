import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useStatusPolling } from '@/hooks/useStatusPolling';

// Mock fetch globally
global.fetch = vi.fn();

describe('useStatusPolling', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.runOnlyPendingTimers();
    vi.useRealTimers();
  });

  it('should initialize with null status and not polling', () => {
    const { result } = renderHook(() => useStatusPolling());

    expect(result.current.status).toBeNull();
    expect(result.current.isPolling).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should start polling when startPolling is called', async () => {
    const mockResponse = {
      id: 'doc-123',
      filename: 'test.pdf',
      status: 'processing',
      processing_options: { mode: 'fast', ocr_enabled: false },
      created_at: new Date().toISOString(),
      completed_at: null,
      error_message: null,
      progress_stage: 'Converting document',
      elapsed_time: 10,
      progress: 25,
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const { result } = renderHook(() => useStatusPolling());

    act(() => {
      result.current.startPolling('doc-123');
    });

    await waitFor(() => {
      expect(result.current.isPolling).toBe(true);
    });

    await waitFor(() => {
      expect(result.current.status).not.toBeNull();
    });

    expect(global.fetch).toHaveBeenCalledWith('/api/status/doc-123', expect.any(Object));
    expect(result.current.status?.status).toBe('processing');
    expect(result.current.status?.filename).toBe('test.pdf');
  });

  it('should poll every 2 seconds for non-terminal states', async () => {
    const mockResponse = {
      id: 'doc-123',
      filename: 'test.pdf',
      status: 'processing',
      processing_options: { mode: 'fast', ocr_enabled: false },
      created_at: new Date().toISOString(),
      completed_at: null,
      error_message: null,
      progress_stage: 'Converting document',
      elapsed_time: 10,
      progress: 25,
    };

    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    });

    const { result } = renderHook(() => useStatusPolling());

    act(() => {
      result.current.startPolling('doc-123');
    });

    // Wait for initial poll
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    // Advance timer by 2 seconds
    act(() => {
      vi.advanceTimersByTime(2000);
    });

    // Wait for second poll
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    // Advance timer by another 2 seconds
    act(() => {
      vi.advanceTimersByTime(2000);
    });

    // Wait for third poll
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(3);
    });
  });

  it('should stop polling automatically when status is complete', async () => {
    const completeResponse = {
      id: 'doc-123',
      filename: 'test.pdf',
      status: 'complete',
      processing_options: { mode: 'fast', ocr_enabled: false },
      created_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
      error_message: null,
      progress_stage: 'Processing complete',
      elapsed_time: 30,
      progress: 100,
      download_url: 'https://example.com/download',
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => completeResponse,
    });

    const { result } = renderHook(() => useStatusPolling());

    act(() => {
      result.current.startPolling('doc-123');
    });

    await waitFor(() => {
      expect(result.current.status?.status).toBe('complete');
    });

    await waitFor(() => {
      expect(result.current.isPolling).toBe(false);
    });

    // Advance timer - should not poll again
    const callCount = (global.fetch as any).mock.calls.length;
    act(() => {
      vi.advanceTimersByTime(2000);
    });

    expect(global.fetch).toHaveBeenCalledTimes(callCount);
  });

  it('should stop polling automatically when status is failed', async () => {
    const failedResponse = {
      id: 'doc-123',
      filename: 'test.pdf',
      status: 'failed',
      processing_options: { mode: 'fast', ocr_enabled: false },
      created_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
      error_message: 'Processing error',
      progress_stage: 'Processing failed',
      elapsed_time: 15,
      progress: 0,
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => failedResponse,
    });

    const { result } = renderHook(() => useStatusPolling());

    act(() => {
      result.current.startPolling('doc-123');
    });

    await waitFor(() => {
      expect(result.current.status?.status).toBe('failed');
    });

    await waitFor(() => {
      expect(result.current.isPolling).toBe(false);
    });

    // Advance timer - should not poll again
    const callCount = (global.fetch as any).mock.calls.length;
    act(() => {
      vi.advanceTimersByTime(2000);
    });

    expect(global.fetch).toHaveBeenCalledTimes(callCount);
  });

  it('should handle polling errors with exponential backoff retry', async () => {
    (global.fetch as any)
      .mockRejectedValueOnce(new Error('Network error'))
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 'doc-123',
          filename: 'test.pdf',
          status: 'processing',
          processing_options: { mode: 'fast', ocr_enabled: false },
          created_at: new Date().toISOString(),
          completed_at: null,
          error_message: null,
          progress_stage: 'Converting document',
          elapsed_time: 10,
          progress: 25,
        }),
      });

    const { result } = renderHook(() => useStatusPolling());

    act(() => {
      result.current.startPolling('doc-123');
    });

    // First attempt fails
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    // Retry after 2 seconds
    act(() => {
      vi.advanceTimersByTime(2000);
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    // Retry after 4 seconds (exponential backoff)
    act(() => {
      vi.advanceTimersByTime(4000);
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(3);
      expect(result.current.status).not.toBeNull();
      expect(result.current.error).toBeNull();
    });
  });

  it('should set error after max retries exceeded', async () => {
    (global.fetch as any).mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => useStatusPolling());

    act(() => {
      result.current.startPolling('doc-123');
    });

    // First attempt
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    // Retry 1 (2s backoff)
    act(() => {
      vi.advanceTimersByTime(2000);
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    // Retry 2 (4s backoff)
    act(() => {
      vi.advanceTimersByTime(4000);
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(3);
    });

    // Retry 3 (8s backoff)
    act(() => {
      vi.advanceTimersByTime(8000);
    });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(4);
      expect(result.current.error).toBe('Unable to get status updates. Please refresh the page.');
      expect(result.current.isPolling).toBe(false);
    });
  });

  it('should stop polling when stopPolling is called', async () => {
    const mockResponse = {
      id: 'doc-123',
      filename: 'test.pdf',
      status: 'processing',
      processing_options: { mode: 'fast', ocr_enabled: false },
      created_at: new Date().toISOString(),
      completed_at: null,
      error_message: null,
      progress_stage: 'Converting document',
      elapsed_time: 10,
      progress: 25,
    };

    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    });

    const { result } = renderHook(() => useStatusPolling());

    act(() => {
      result.current.startPolling('doc-123');
    });

    await waitFor(() => {
      expect(result.current.isPolling).toBe(true);
    });

    act(() => {
      result.current.stopPolling();
    });

    expect(result.current.isPolling).toBe(false);

    // Advance timer - should not poll again
    const callCount = (global.fetch as any).mock.calls.length;
    act(() => {
      vi.advanceTimersByTime(2000);
    });

    expect(global.fetch).toHaveBeenCalledTimes(callCount);
  });

  it('should cleanup on component unmount', async () => {
    const mockResponse = {
      id: 'doc-123',
      filename: 'test.pdf',
      status: 'processing',
      processing_options: { mode: 'fast', ocr_enabled: false },
      created_at: new Date().toISOString(),
      completed_at: null,
      error_message: null,
      progress_stage: 'Converting document',
      elapsed_time: 10,
      progress: 25,
    };

    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    });

    const { result, unmount } = renderHook(() => useStatusPolling());

    act(() => {
      result.current.startPolling('doc-123');
    });

    await waitFor(() => {
      expect(result.current.isPolling).toBe(true);
    });

    unmount();

    // Advance timer - should not poll after unmount
    const callCount = (global.fetch as any).mock.calls.length;
    act(() => {
      vi.advanceTimersByTime(2000);
    });

    expect(global.fetch).toHaveBeenCalledTimes(callCount);
  });

  it('should calculate estimated time remaining correctly', async () => {
    const mockResponse = {
      id: 'doc-123',
      filename: 'test.pdf',
      status: 'processing',
      processing_options: { mode: 'fast', ocr_enabled: false },
      created_at: new Date().toISOString(),
      completed_at: null,
      error_message: null,
      progress_stage: 'Converting document',
      elapsed_time: 10,
      progress: 33,
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const { result } = renderHook(() => useStatusPolling());

    act(() => {
      result.current.startPolling('doc-123');
    });

    await waitFor(() => {
      expect(result.current.status).not.toBeNull();
    });

    // Fast mode without OCR: ~30s total, 10s elapsed = ~20s remaining
    expect(result.current.status?.estimated_time_remaining).toBeGreaterThan(15);
    expect(result.current.status?.estimated_time_remaining).toBeLessThan(25);
  });

  it('should calculate progress percentage correctly', async () => {
    const mockResponse = {
      id: 'doc-123',
      filename: 'test.pdf',
      status: 'processing',
      processing_options: { mode: 'quality', ocr_enabled: true },
      created_at: new Date().toISOString(),
      completed_at: null,
      error_message: null,
      progress_stage: 'Converting document',
      elapsed_time: 90, // Half of estimated 180s for quality+OCR
      progress: 50,
    };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    const { result } = renderHook(() => useStatusPolling());

    act(() => {
      result.current.startPolling('doc-123');
    });

    await waitFor(() => {
      expect(result.current.status).not.toBeNull();
    });

    // Quality mode with OCR: 90s * 2 = 180s total
    // Progress should be calculated based on elapsed time
    expect(result.current.status?.progress).toBeGreaterThan(10);
    expect(result.current.status?.progress).toBeLessThan(95);
  });
});
