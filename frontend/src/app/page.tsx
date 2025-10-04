'use client';

import { useState, useEffect } from 'react';
import { FileDropzone } from '@/components/FileDropzone';
import { ProcessingCard } from '@/components/ProcessingCard';
import { useFileUpload } from '@/hooks/useFileUpload';
import { ProcessingOptions, DocumentStatus } from '@/types/database';

interface DocumentStatusResponse {
  id: string;
  filename: string;
  status: DocumentStatus;
  processing_options: ProcessingOptions;
  created_at: string;
  completed_at?: string;
  error_message?: string;
  progress_stage?: string;
  elapsed_time?: number;
  download_url?: string;
}

export default function Home() {
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [documentStatus, setDocumentStatus] = useState<DocumentStatusResponse | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const { uploadFile, isUploading, uploadProgress, error, reset } = useFileUpload();

  const handleFileUpload = async (file: File, options: ProcessingOptions) => {
    const uploadedDocumentId = await uploadFile(file, options);

    if (uploadedDocumentId) {
      setDocumentId(uploadedDocumentId);
      setIsPolling(true);
      // Start polling for status immediately
      pollDocumentStatus(uploadedDocumentId);
    }
  };

  const pollDocumentStatus = async (docId: string) => {
    try {
      const response = await fetch(`/api/status/${docId}`);
      if (!response.ok) {
        throw new Error('Failed to get document status');
      }

      const status: DocumentStatusResponse = await response.json();
      setDocumentStatus(status);

      // Continue polling if still processing
      if (status.status === 'queued' || status.status === 'processing') {
        setTimeout(() => pollDocumentStatus(docId), 2000); // Poll every 2 seconds
      } else {
        setIsPolling(false);
      }
    } catch (err) {
      console.error('Error polling document status:', err);
      setIsPolling(false);
    }
  };

  const handleReset = () => {
    reset();
    setDocumentId(null);
    setDocumentStatus(null);
    setIsPolling(false);
  };

  const handleDownload = () => {
    if (documentStatus?.download_url) {
      window.open(documentStatus.download_url, '_blank');
    }
  };

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Workshop Document Processor</h1>
              <p className="text-muted-foreground mt-1">
                Convert office documents to AI-optimized markdown format
              </p>
            </div>
            <a
              href="#instructions"
              className="text-primary hover:underline text-sm font-medium"
            >
              How to use in Open WebUI →
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {!documentId ? (
            <div className="space-y-8">
              {/* Instructions */}
              <div className="text-center space-y-4">
                <h2 className="text-2xl font-semibold">
                  Upload Your Document
                </h2>
                <p className="text-muted-foreground max-w-2xl mx-auto">
                  Transform your PDF, DOCX, PPTX, or XLSX files into clean,
                  AI-optimized markdown format perfect for use in Open WebUI's RAG system.
                </p>
              </div>

              {/* File Upload Component */}
              <FileDropzone
                onFileUpload={handleFileUpload}
                isUploading={isUploading}
                uploadProgress={uploadProgress}
                error={error}
              />

              {/* Features */}
              <div className="grid md:grid-cols-3 gap-6 mt-12">
                <div className="text-center space-y-2">
                  <div className="text-2xl">🚀</div>
                  <h3 className="font-medium">Fast Processing</h3>
                  <p className="text-sm text-muted-foreground">
                    Get your markdown files in under 2 minutes
                  </p>
                </div>
                <div className="text-center space-y-2">
                  <div className="text-2xl">🎯</div>
                  <h3 className="font-medium">AI Optimized</h3>
                  <p className="text-sm text-muted-foreground">
                    Perfect formatting for RAG and LLM applications
                  </p>
                </div>
                <div className="text-center space-y-2">
                  <div className="text-2xl">🔒</div>
                  <h3 className="font-medium">Secure</h3>
                  <p className="text-sm text-muted-foreground">
                    Your files are processed securely and privately
                  </p>
                </div>
              </div>
            </div>
          ) : documentStatus ? (
            /* Processing Status */
            <div className="space-y-6">
              <ProcessingCard
                status={documentStatus.status}
                filename={documentStatus.filename}
                progress={
                  documentStatus.status === 'processing' ? 50 :
                  documentStatus.status === 'complete' ? 100 : 0
                }
                estimatedTime={
                  documentStatus.status === 'processing' ?
                  (documentStatus.processing_options.processing_mode === 'fast' ? 30 : 120) : undefined
                }
                errorMessage={documentStatus.error_message}
                processingMode={documentStatus.processing_options.processing_mode}
                ocrEnabled={documentStatus.processing_options.ocr_enabled}
              />

              {/* Action Buttons */}
              <div className="text-center space-y-4">
                {documentStatus.status === 'complete' && documentStatus.download_url && (
                  <button
                    onClick={handleDownload}
                    className="inline-flex items-center px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                  >
                    Download Markdown
                  </button>
                )}

                <button
                  onClick={handleReset}
                  className="inline-flex items-center px-6 py-3 border border-input bg-background hover:bg-accent hover:text-accent-foreground rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary ml-0 sm:ml-4"
                >
                  Process Another Document
                </button>
              </div>
            </div>
          ) : null}
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t mt-16">
        <div className="container mx-auto px-4 py-6">
          <p className="text-center text-sm text-muted-foreground">
            Built for the October 17, 2025 Workshop • Internal Use Only
          </p>
        </div>
      </footer>
    </main>
  );
}