import React, { useState } from 'react';
import { CheckCircle2, Download, FileText, RefreshCw, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { ErrorAlert } from '@/components/ErrorAlert';
import { cn } from '@/lib/utils';

export interface SuccessScreenProps {
  documentId: string;
  filename: string;
  fileSize?: number;
  onReset: () => void;
  className?: string;
}

/**
 * SuccessScreen Component
 *
 * Displays success confirmation with download functionality after document processing.
 * Implements AC 1: Green checkmark, "Processing Complete!" heading, filename with .md preview
 * Implements AC 2: Large, prominent "Download Markdown" button
 * Implements AC 4: File size display in success message
 * Implements AC 5: "Process Another Document" button with state reset
 */
export const SuccessScreen: React.FC<SuccessScreenProps> = ({
  documentId,
  filename,
  fileSize,
  onReset,
  className,
}) => {
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<{
    message: string;
    details?: string;
  } | null>(null);

  /**
   * Format file size for display
   */
  const formatFileSize = (bytes?: number): string => {
    if (!bytes || bytes === 0) return '';

    if (bytes < 1024) {
      return `${bytes} B`;
    } else if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    } else {
      return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }
  };

  /**
   * Get filename with .md extension for preview
   */
  const getMarkdownFilename = (originalFilename: string): string => {
    // Remove common document extensions and replace with .md
    const nameWithoutExt = originalFilename.replace(/\.(pdf|docx|pptx|xlsx)$/i, '');
    return `${nameWithoutExt}.md`;
  };

  /**
   * Handle download with error handling
   * Implements AC 2: Download with proper content-disposition header
   * Implements AC 7: Actionable error messages for download failures
   */
  const handleDownload = async () => {
    try {
      setIsDownloading(true);
      setDownloadError(null);

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      // Don't add /api prefix if apiUrl already ends with /api (nginx proxy setup)
      const endpoint = apiUrl.endsWith('/api')
        ? `${apiUrl}/download/${documentId}`
        : `${apiUrl}/api/download/${documentId}`;
      const response = await fetch(endpoint);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail ||
          'Download failed - file may have been moved or deleted. Please process document again.'
        );
      }

      // Get filename from Content-Disposition header or use default
      const contentDisposition = response.headers.get('Content-Disposition');
      let downloadFilename = getMarkdownFilename(filename);

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+?)"?$/);
        if (filenameMatch) {
          downloadFilename = filenameMatch[1];
        }
      }

      // Create blob and trigger download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = downloadFilename;
      a.setAttribute('aria-label', `Download ${downloadFilename}`);

      // Append to body, click, and cleanup
      document.body.appendChild(a);
      a.click();

      // Cleanup
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

    } catch (error) {
      console.error('Download error:', error);
      setDownloadError({
        message: error instanceof Error
          ? error.message
          : 'Download failed - file may have been moved or deleted. Please process document again.',
        details: 'If this problem persists, please try processing the document again.',
      });
    } finally {
      setIsDownloading(false);
    }
  };

  /**
   * Handle retry after download error
   */
  const handleRetry = () => {
    setDownloadError(null);
    handleDownload();
  };

  const markdownFilename = getMarkdownFilename(filename);
  const formattedFileSize = formatFileSize(fileSize);

  return (
    <Card
      className={cn(
        'w-full px-4 md:px-0 max-w-sm sm:max-w-md md:max-w-lg lg:max-w-2xl mx-auto',
        'transition-all duration-300 animate-in fade-in slide-in-from-bottom-4',
        className
      )}
    >
      <CardHeader className="text-center pb-4 p-4 md:p-6">
        {/* Success Icon - AC1: Green checkmark */}
        <div className="flex justify-center mb-3 md:mb-4">
          <div className="relative">
            <CheckCircle2
              className="h-14 w-14 md:h-16 md:w-16 lg:h-20 lg:w-20 text-green-500 transition-all duration-300"
              aria-hidden="true"
            />
            <div className="absolute inset-0 h-14 w-14 md:h-16 md:w-16 lg:h-20 lg:w-20 rounded-full bg-green-500 animate-ping opacity-20" />
          </div>
        </div>

        {/* Success Heading - AC1: "Processing Complete!" */}
        <h1
          className="text-xl md:text-2xl lg:text-3xl font-bold text-green-700 dark:text-green-400 mb-2"
          role="alert"
          aria-live="polite"
        >
          Processing Complete!
        </h1>

        {/* Filename Preview - AC1: Original filename with .md extension */}
        <div className="flex items-center justify-center gap-2 text-sm md:text-base text-muted-foreground">
          <FileText className="h-4 w-4 md:h-5 md:w-5 flex-shrink-0" aria-hidden="true" />
          <p className="font-medium break-words max-w-full px-2">
            {markdownFilename}
            {formattedFileSize && (
              <span className="text-xs md:text-sm ml-2 text-green-600 dark:text-green-400">
                ({formattedFileSize})
              </span>
            )}
          </p>
        </div>

        {/* Success Message - AC4: File size in message */}
        <p className="text-sm md:text-base text-muted-foreground mt-2 px-2">
          Your markdown file is ready for download
        </p>
      </CardHeader>

      <CardContent className="space-y-4 p-4 md:p-6">
        {/* Download Error Alert */}
        {downloadError && (
          <ErrorAlert
            error={{
              message: downloadError.message,
              details: downloadError.details,
              code: 'DOWNLOAD_ERROR',
            }}
            onRetry={handleRetry}
            className="animate-in fade-in duration-200"
          />
        )}

        {/* Download Button - AC2: Large, prominent button */}
        <div className="flex flex-col gap-3 md:gap-4">
          <Button
            size="lg"
            onClick={handleDownload}
            disabled={isDownloading}
            className={cn(
              'w-full md:w-auto md:mx-auto md:min-w-[280px] min-h-[44px] md:min-h-[52px] text-base md:text-lg font-semibold',
              'bg-green-600 hover:bg-green-700 text-white',
              'shadow-md hover:shadow-lg transition-all duration-200',
              'active:scale-[0.98]',
              isDownloading && 'opacity-75 cursor-wait'
            )}
            aria-label={`Download ${markdownFilename}`}
          >
            {isDownloading ? (
              <>
                <Loader2 className="h-5 w-5 mr-2 animate-spin" aria-hidden="true" />
                Downloading...
              </>
            ) : (
              <>
                <Download className="h-5 w-5 mr-2" aria-hidden="true" />
                Download Markdown
              </>
            )}
          </Button>

          {/* Process Another Document Button - AC5: Reset state */}
          <Button
            variant="outline"
            size="lg"
            onClick={onReset}
            disabled={isDownloading}
            className={cn(
              'w-full md:w-auto md:mx-auto md:min-w-[280px] min-h-[44px] md:min-h-[48px] text-sm md:text-base',
              'border-2 transition-all duration-200',
              'active:scale-[0.98]',
              isDownloading && 'opacity-50 cursor-not-allowed'
            )}
            aria-label="Process another document"
          >
            <RefreshCw className="h-4 w-4 mr-2" aria-hidden="true" />
            Process Another Document
          </Button>
        </div>

        {/* Additional Information */}
        <div className="text-center text-xs text-muted-foreground pt-2">
          <p>Your document has been successfully converted to markdown format.</p>
        </div>

        {/* Next Steps Link */}
        <div className="text-center pt-4 border-t">
          <p className="text-sm font-medium mb-2">Next Steps</p>
          <a
            href="/instructions"
            className="text-sm text-primary hover:underline inline-flex items-center gap-1"
          >
            How to use this markdown in Open WebUI →
          </a>
        </div>
      </CardContent>
    </Card>
  );
};

SuccessScreen.displayName = 'SuccessScreen';
