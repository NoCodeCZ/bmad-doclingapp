import React from 'react';
import { Loader2, CheckCircle2, AlertTriangle, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { cn } from '@/lib/utils';
import { DocumentStatus } from '@/types/database';

interface ProcessingCardProps {
  status: DocumentStatus;
  filename: string;
  progress?: number;
  estimatedTime?: number;
  errorMessage?: string | null;
  processingMode?: 'fast' | 'quality';
  ocrEnabled?: boolean;
}

export const ProcessingCard: React.FC<ProcessingCardProps> = ({
  status,
  filename,
  progress = 0,
  estimatedTime,
  errorMessage,
  processingMode = 'fast',
  ocrEnabled = false,
}) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'queued':
        return <Clock className="h-8 w-8 text-blue-500" />;
      case 'processing':
        return <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />;
      case 'complete':
        return <CheckCircle2 className="h-8 w-8 text-green-500" />;
      case 'failed':
        return <AlertTriangle className="h-8 w-8 text-red-500" />;
      default:
        return <Loader2 className="h-8 w-8 text-gray-500" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'queued':
        return 'Waiting to process...';
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
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader className="text-center">
        <div className="flex justify-center mb-4">
          {getStatusIcon()}
        </div>
        <CardTitle className="text-xl">
          {getStatusText()}
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          {filename}
        </p>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Progress Bar */}
        {(status === 'processing' || status === 'queued') && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Progress</span>
              <span>{progress}%</span>
            </div>
            <Progress value={progress} className="w-full" />
          </div>
        )}

        {/* Status Description */}
        <Alert className={cn(
          status === 'failed' && 'border-destructive',
          status === 'complete' && 'border-green-500 bg-green-50 dark:bg-green-950'
        )}>
          <AlertDescription>
            {getStatusDescription()}
          </AlertDescription>
        </Alert>

        {/* Estimated Time */}
        {status === 'processing' && estimatedTime && (
          <div className="text-center text-sm text-muted-foreground">
            Estimated time remaining: {formatTime(estimatedTime)}
          </div>
        )}

        {/* Processing Options Display */}
        {(status === 'processing' || status === 'queued') && (
          <div className="text-center text-sm text-muted-foreground space-y-1">
            <div>Mode: <span className="font-medium">{processingMode === 'fast' ? 'Fast' : 'Quality'}</span></div>
            {ocrEnabled && (
              <div>OCR: <span className="font-medium">Enabled</span></div>
            )}
          </div>
        )}

        {/* Error Actions */}
        {status === 'failed' && (
          <div className="text-center space-y-4">
            <p className="text-sm text-muted-foreground">
              Please try again or contact support if the problem persists.
            </p>
            <div className="space-y-2">
              <button className="w-full sm:w-auto px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors">
                Try Again
              </button>
              <button className="w-full sm:w-auto px-4 py-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground rounded-md transition-colors ml-0 sm:ml-2">
                Contact Support
              </button>
            </div>
          </div>
        )}

        {/* Success Actions */}
        {status === 'complete' && (
          <div className="text-center space-y-4">
            <p className="text-sm text-muted-foreground">
              Your markdown file is ready for download.
            </p>
            <div className="space-y-2">
              <button className="w-full sm:w-auto px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors">
                Download Markdown
              </button>
              <button className="w-full sm:w-auto px-4 py-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground rounded-md transition-colors ml-0 sm:ml-2">
                Process Another Document
              </button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};