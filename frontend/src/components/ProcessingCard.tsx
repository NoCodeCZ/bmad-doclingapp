import React from 'react';
import { Loader2, CheckCircle2, AlertTriangle, Clock, Upload, FileCheck } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { cn } from '@/lib/utils';
import { DocumentStatus } from '@/types/database';
import { SuccessScreen } from '@/components/SuccessScreen';

interface ProcessingCardProps {
  status: DocumentStatus;
  filename: string;
  progress?: number;
  estimatedTime?: number;
  errorMessage?: string | null;
  processingMode?: 'fast' | 'quality';
  ocrEnabled?: boolean;
  progressStage?: string;
  documentId?: string;
  fileSize?: number;
  onReset?: () => void;
}

export const ProcessingCard: React.FC<ProcessingCardProps> = ({
  status,
  filename,
  progress = 0,
  estimatedTime,
  errorMessage,
  processingMode = 'fast',
  ocrEnabled = false,
  progressStage,
  documentId,
  fileSize,
  onReset,
}) => {
  // Show SuccessScreen when processing is complete
  if (status === 'complete' && documentId) {
    const handleReset = () => {
      if (onReset) {
        onReset();
      } else {
        // Default: redirect to home page
        window.location.href = '/';
      }
    };

    return (
      <SuccessScreen
        documentId={documentId}
        filename={filename}
        fileSize={fileSize}
        onReset={handleReset}
      />
    );
  }
  /**
   * Get animated status icon with visual differentiation per stage
   * - Uploading: Blue pulse animation
   * - Processing: Amber spinner
   * - Complete: Green checkmark
   * - Failed: Red error icon
   */
  const getStatusIcon = () => {
    const stage = progressStage?.toLowerCase() || '';

    // Uploading stage - blue pulse
    if (stage.includes('uploading')) {
      return (
        <div className="relative">
          <Upload className="h-8 w-8 sm:h-10 sm:w-10 lg:h-12 lg:w-12 text-blue-500" />
          <Upload className="absolute inset-0 h-8 w-8 sm:h-10 sm:w-10 lg:h-12 lg:w-12 text-blue-500 animate-ping opacity-75" />
        </div>
      );
    }

    // Finalizing stage - amber spinner with check overlay
    if (stage.includes('finalizing')) {
      return (
        <div className="relative">
          <Loader2 className="h-8 w-8 sm:h-10 sm:w-10 lg:h-12 lg:w-12 text-amber-500 animate-spin" />
          <FileCheck className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 h-4 w-4 text-amber-700" />
        </div>
      );
    }

    switch (status) {
      case 'queued':
        return (
          <div className="relative">
            <Clock className="h-8 w-8 sm:h-10 sm:w-10 lg:h-12 lg:w-12 text-blue-500" />
            <div className="absolute inset-0 h-8 w-8 sm:h-10 sm:w-10 lg:h-12 lg:w-12 rounded-full border-2 border-blue-500 animate-pulse" />
          </div>
        );
      case 'processing':
        return <Loader2 className="h-8 w-8 sm:h-10 sm:w-10 lg:h-12 lg:w-12 text-amber-500 animate-spin" />;
      case 'complete':
        return (
          <div className="relative">
            <CheckCircle2 className="h-8 w-8 sm:h-10 sm:w-10 lg:h-12 lg:w-12 text-green-500 transition-all duration-300" />
            <div className="absolute inset-0 h-8 w-8 sm:h-10 sm:w-10 lg:h-12 lg:w-12 rounded-full bg-green-500 animate-ping opacity-20" />
          </div>
        );
      case 'failed':
        return <AlertTriangle className="h-8 w-8 sm:h-10 sm:w-10 lg:h-12 lg:w-12 text-red-500" />;
      default:
        return <Loader2 className="h-8 w-8 sm:h-10 sm:w-10 lg:h-12 lg:w-12 text-gray-500" />;
    }
  };

  const getStatusText = () => {
    // Use progress_stage if available for more detailed status
    if (progressStage) {
      return progressStage;
    }

    switch (status) {
      case 'queued':
        return 'Queued for processing...';
      case 'processing':
        return 'Processing document...';
      case 'complete':
        return 'Processing complete!';
      case 'failed':
        return 'Processing failed';
      default:
        return 'Preparing...';
    }
  };

  const getStatusDescription = () => {
    switch (status) {
      case 'queued':
        return 'Your document is in the queue and will be processed shortly.';
      case 'processing':
        return `Converting using ${processingMode} mode${ocrEnabled ? ' with OCR' : ''}...`;
      case 'complete':
        return 'Your document has been successfully converted to markdown.';
      case 'failed':
        return errorMessage || 'An error occurred while processing your document.';
      default:
        return '';
    }
  };

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `~${seconds} seconds`;
    return `~${Math.ceil(seconds / 60)} minute${seconds > 60 ? 's' : ''}`;
  };

  return (
    <Card className={cn(
      "w-full px-4 md:px-0 max-w-sm sm:max-w-md md:max-w-lg lg:max-w-2xl mx-auto transition-all duration-300",
      (status === 'processing' || status === 'queued') && "animate-in fade-in slide-in-from-bottom-4"
    )}>
      <CardHeader className="text-center p-4 md:p-6">
        <div className="flex justify-center mb-3 md:mb-4 transition-transform duration-300">
          {getStatusIcon()}
        </div>
        <CardTitle className={cn(
          "text-base md:text-lg lg:text-xl transition-all duration-300",
          (status === 'processing' || status === 'queued') && "animate-pulse"
        )}>
          {getStatusText()}
        </CardTitle>
        <p className="text-sm md:text-base text-muted-foreground break-words px-2 md:px-4">
          {filename}
        </p>
      </CardHeader>

      <CardContent className="space-y-4 md:space-y-6 p-4 md:p-6">
        {/* Progress Bar with smooth animations */}
        {(status === 'processing' || status === 'queued') && (
          <div className="space-y-2 transition-all duration-300 animate-in fade-in slide-in-from-top-2">
            <div className="flex justify-between text-sm md:text-base">
              <span className="font-medium">Progress</span>
              <span className="font-semibold tabular-nums">{progress}%</span>
            </div>
            <Progress
              value={progress}
              className={cn(
                "w-full h-3 md:h-4 transition-all duration-500",
                // Add gradient based on status/stage
                progressStage?.toLowerCase().includes('uploading') && "bg-blue-100 dark:bg-blue-900",
                progressStage?.toLowerCase().includes('finalizing') && "bg-amber-100 dark:bg-amber-900",
                status === 'processing' && !progressStage?.toLowerCase().includes('finalizing') && "bg-amber-100 dark:bg-amber-900"
              )}
            />
            {/* Pulsing indicator bar underneath for active processing */}
            <div className="h-1 w-full bg-gradient-to-r from-transparent via-primary/30 to-transparent animate-pulse rounded-full" />
          </div>
        )}

        {/* Status Description with smooth transitions */}
        <Alert className={cn(
          "transition-all duration-300",
          status === 'failed' && 'border-red-500 bg-red-50 dark:bg-red-950',
          status === 'complete' && 'border-green-500 bg-green-50 dark:bg-green-950',
          status === 'processing' && 'border-amber-500 bg-amber-50 dark:bg-amber-950',
          status === 'queued' && 'border-blue-500 bg-blue-50 dark:bg-blue-950'
        )}>
          <AlertDescription className="text-sm md:text-base break-words">
            {getStatusDescription()}
          </AlertDescription>
        </Alert>

        {/* Estimated Time with smooth fade-in */}
        {status === 'processing' && estimatedTime !== undefined && estimatedTime > 0 && (
          <div className="text-center text-sm md:text-base text-muted-foreground animate-in fade-in duration-300">
            <div className="flex items-center justify-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin text-amber-500" />
              <span className="font-medium">Estimated time remaining:</span>{' '}
              <span className="font-semibold text-amber-600 dark:text-amber-400 tabular-nums">
                {formatTime(estimatedTime)}
              </span>
            </div>
          </div>
        )}

        {/* Processing Options Display */}
        {(status === 'processing' || status === 'queued') && (
          <div className="text-center text-sm md:text-base text-muted-foreground space-y-1 transition-opacity duration-300">
            <div>
              Mode: <span className="font-medium text-foreground">{processingMode === 'fast' ? 'Fast' : 'Quality'}</span>
            </div>
            {ocrEnabled && (
              <div>
                OCR: <span className="font-medium text-foreground">Enabled</span>
              </div>
            )}
          </div>
        )}

        {/* Error Actions - Mobile-friendly touch targets (min 44px) */}
        {status === 'failed' && (
          <div className="text-center space-y-4 animate-in fade-in duration-300">
            <p className="text-xs sm:text-sm text-muted-foreground px-4">
              Please try again or contact support if the problem persists.
            </p>
            <div className="flex flex-col sm:flex-row gap-2 sm:gap-4 justify-center">
              <button className="w-full sm:w-auto min-h-[44px] px-6 py-3 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 active:scale-95 transition-all duration-200 font-medium">
                Try Again
              </button>
              <button className="w-full sm:w-auto min-h-[44px] px-6 py-3 border border-input bg-background hover:bg-accent hover:text-accent-foreground rounded-md active:scale-95 transition-all duration-200 font-medium">
                Contact Support
              </button>
            </div>
          </div>
        )}

        {/* Success Actions - Mobile-friendly touch targets (min 44px) */}
        {status === 'complete' && (
          <div className="text-center space-y-4 animate-in fade-in duration-300">
            <p className="text-xs sm:text-sm text-muted-foreground px-4">
              Your markdown file is ready for download.
            </p>
            <div className="flex flex-col sm:flex-row gap-2 sm:gap-4 justify-center">
              <button className="w-full sm:w-auto min-h-[44px] px-8 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 active:scale-95 transition-all duration-200 font-medium shadow-sm">
                Download Markdown
              </button>
              <button className="w-full sm:w-auto min-h-[44px] px-6 py-3 border border-input bg-background hover:bg-accent hover:text-accent-foreground rounded-md active:scale-95 transition-all duration-200 font-medium">
                Process Another Document
              </button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};