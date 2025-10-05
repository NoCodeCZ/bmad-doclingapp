'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ProcessingCard } from '@/components/ProcessingCard';
import { useStatusPolling } from '@/hooks/useStatusPolling';

interface ProcessingPageProps {
  params: {
    id: string;
  };
  searchParams?: {
    filename?: string;
    mode?: 'fast' | 'quality';
    ocr?: string;
  };
}

/**
 * Processing status page with real-time polling
 *
 * Features:
 * - Polls status every 2 seconds
 * - Displays animated progress indicators
 * - Shows estimated time remaining
 * - Auto-redirects on completion/failure
 * - Mobile-responsive design
 * - Accessibility support
 */
export default function ProcessingPage({ params, searchParams }: ProcessingPageProps) {
  const router = useRouter();
  const { status, isPolling, error, startPolling, stopPolling } = useStatusPolling();

  // Extract processing options from URL params
  const processingMode = searchParams?.mode || 'fast';
  const ocrEnabled = searchParams?.ocr === 'true';

  // Start polling when component mounts
  useEffect(() => {
    if (params.id) {
      startPolling(params.id);
    }

    // Cleanup on unmount
    return () => {
      stopPolling();
    };
  }, [params.id, startPolling, stopPolling]);

  // Handle navigation on terminal states (optional auto-redirect)
  useEffect(() => {
    if (status?.status === 'complete' && status.download_url) {
      // Auto-redirect to download page after 2 seconds
      const timer = setTimeout(() => {
        // For now, stay on this page - download will be handled by button
        // router.push(`/download/${params.id}`);
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [status?.status, status?.download_url, params.id, router]);

  // Loading state
  if (!status && isPolling) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading status...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="max-w-md w-full text-center space-y-4">
          <div className="text-red-500 text-4xl">⚠️</div>
          <h2 className="text-xl font-semibold">Connection Error</h2>
          <p className="text-muted-foreground">{error}</p>
          <button
            onClick={() => startPolling(params.id)}
            className="px-6 py-3 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // No status data
  if (!status) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center">
          <p className="text-muted-foreground">No status information available</p>
        </div>
      </div>
    );
  }

  return (
    <main
      className="min-h-screen flex items-center justify-center p-4 sm:p-6 lg:p-8"
      role="main"
      aria-label="Document processing status"
    >
      <div className="w-full max-w-2xl">
        {/* ARIA live region for status updates */}
        <div
          role="status"
          aria-live="polite"
          aria-atomic="true"
          className="sr-only"
        >
          {status.progress_stage}. {status.progress}% complete.
          {status.estimated_time_remaining > 0 &&
            ` Estimated time remaining: ${Math.ceil(status.estimated_time_remaining / 60)} minutes.`}
        </div>

        <ProcessingCard
          status={status.status}
          filename={status.filename}
          progress={status.progress}
          estimatedTime={status.estimated_time_remaining}
          errorMessage={status.error_message}
          processingMode={processingMode}
          ocrEnabled={ocrEnabled}
          progressStage={status.progress_stage}
        />

        {/* Processing info footer */}
        <div className="mt-6 text-center text-xs text-muted-foreground">
          <p>Document ID: {params.id}</p>
          {status.elapsed_time !== undefined && (
            <p className="mt-1">
              Elapsed time: {Math.floor(status.elapsed_time / 60)}m {status.elapsed_time % 60}s
            </p>
          )}
        </div>
      </div>
    </main>
  );
}
