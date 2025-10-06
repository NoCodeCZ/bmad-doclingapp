import React from 'react';
import { AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export interface ErrorAlertProps {
  error: {
    code?: string;
    message: string;
    details?: string;
    timestamp?: string;
    requestId?: string;
  };
  onRetry?: () => void;
  className?: string;
}

/**
 * ErrorAlert Component
 *
 * Displays error messages in a prominent, accessible manner with retry functionality.
 * Implements AC 1: Error messages displayed in prominent error UI component (red banner or modal) with error icon
 * Implements AC 7: All error states include "Try Again" button that resets to upload screen
 */
export const ErrorAlert: React.FC<ErrorAlertProps> = ({
  error,
  onRetry,
  className,
}) => {
  return (
    <div
      role="alert"
      aria-live="assertive"
      aria-labelledby="error-alert-title"
      aria-describedby="error-alert-message"
      className={cn(
        'bg-red-50 border border-red-200 rounded-lg p-4 md:p-5 shadow-sm',
        className
      )}
    >
      <div className="flex flex-col sm:flex-row items-start gap-3 md:gap-4">
        {/* Error Icon */}
        <div className="flex-shrink-0">
          <AlertTriangle
            className="h-5 w-5 md:h-6 md:w-6 text-red-600"
            aria-hidden="true"
          />
        </div>

        {/* Error Content */}
        <div className="flex-1 min-w-0 w-full">
          {/* Error Title */}
          <h3
            id="error-alert-title"
            className="text-base md:text-sm font-semibold text-red-800 mb-1"
          >
            Error
          </h3>

          {/* Error Message */}
          <div
            id="error-alert-message"
            className="text-sm md:text-base text-red-700 space-y-1"
          >
            <p className="break-words">{error.message}</p>

            {/* Optional Details */}
            {error.details && (
              <p className="text-sm md:text-xs text-red-600 mt-2 break-words">
                {error.details}
              </p>
            )}

            {/* Request ID for debugging (if available) */}
            {error.requestId && (
              <p className="text-sm md:text-xs text-red-500 mt-2 font-mono break-all">
                Reference ID: {error.requestId}
              </p>
            )}
          </div>

          {/* Try Again Button */}
          {onRetry && (
            <div className="mt-4">
              <Button
                variant="outline"
                size="sm"
                onClick={onRetry}
                aria-label="Try again after error"
                className="w-full sm:w-auto min-h-[44px] border-red-300 text-red-700 hover:bg-red-100 hover:text-red-800 hover:border-red-400 focus:ring-red-500"
              >
                Try Again
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

ErrorAlert.displayName = 'ErrorAlert';
