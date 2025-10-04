import React, { useState, useCallback, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';
import { ALLOWED_FILE_TYPES, MAX_FILE_SIZE } from '@/lib/validation';
import { ProcessingOptions, DocumentUpload } from '@/types/database';

interface FileDropzoneProps {
  onFileUpload: (file: File, options: ProcessingOptions) => Promise<void>;
  isUploading?: boolean;
  uploadProgress?: number;
  error?: string | null;
}

export const FileDropzone: React.FC<FileDropzoneProps> = ({
  onFileUpload,
  isUploading = false,
  uploadProgress = 0,
  error = null,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [ocrEnabled, setOcrEnabled] = useState(false);
  const [processingMode, setProcessingMode] = useState<'fast' | 'quality'>('fast');
  const [validationError, setValidationError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      setValidationError(null);
      
      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0];
        if (rejection.errors.some((e: any) => e.code === 'file-too-large')) {
          setValidationError(`File too large. Maximum size is ${MAX_FILE_SIZE / 1024 / 1024}MB`);
        } else if (rejection.errors.some((e: any) => e.code === 'file-invalid-type')) {
          setValidationError(`Unsupported file type. Allowed types: PDF, DOCX, PPTX, XLSX`);
        } else {
          setValidationError('Invalid file. Please check the file type and size.');
        }
        return;
      }

      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        // Client-side validation
        const isValidType = Object.keys(ALLOWED_FILE_TYPES).indexOf(file.type) !== -1;
        const isValidSize = file.size <= MAX_FILE_SIZE;
        
        if (!isValidType) {
          setValidationError(`Unsupported file type. Allowed types: PDF, DOCX, PPTX, XLSX`);
          return;
        }
        
        if (!isValidSize) {
          setValidationError(`File too large. Maximum size is ${MAX_FILE_SIZE / 1024 / 1024}MB`);
          return;
        }
        
        setSelectedFile(file);
      }
    },
    []
  );

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragAccept,
    isDragReject,
  } = useDropzone({
    onDrop,
    accept: ALLOWED_FILE_TYPES,
    maxSize: MAX_FILE_SIZE,
    multiple: false,
    disabled: isUploading,
  });

  const handleFileSelect = () => {
    if (!isUploading && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setValidationError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    
    const options: ProcessingOptions = {
      ocr_enabled: ocrEnabled,
      processing_mode: processingMode,
    };
    
    try {
      await onFileUpload(selectedFile, options);
    } catch (err) {
      // Error is handled by parent component
      console.error('Upload failed:', err);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (file: File) => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf':
        return '📄';
      case 'docx':
        return '📝';
      case 'pptx':
        return '📊';
      case 'xlsx':
        return '📈';
      default:
        return '📄';
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Upload Area */}
      <Card>
        <CardContent className="p-6">
          <div
            {...getRootProps()}
            className={cn(
              "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
              isDragActive && "border-primary bg-primary/5",
              isDragAccept && "border-green-500 bg-green-50 dark:bg-green-950",
              isDragReject && "border-red-500 bg-red-50 dark:bg-red-950",
              !isDragActive && !isDragAccept && !isDragReject && "border-gray-300 hover:border-gray-400",
              isUploading && "cursor-not-allowed opacity-50"
            )}
            onClick={handleFileSelect}
          >
            <input {...getInputProps()} ref={fileInputRef} />
            
            <div className="flex flex-col items-center space-y-4">
              {isUploading ? (
                <Loader2 className="h-12 w-12 animate-spin text-primary" />
              ) : (
                <Upload className="h-12 w-12 text-gray-400" />
              )}
              
              <div className="space-y-2">
                <p className="text-lg font-medium">
                  {isUploading 
                    ? 'Uploading...' 
                    : isDragActive
                      ? 'Drop your document here'
                      : 'Drag your document here or click to browse'
                  }
                </p>
                <p className="text-sm text-muted-foreground">
                  Supports PDF, DOCX, PPTX, XLSX (max {MAX_FILE_SIZE / 1024 / 1024}MB)
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* File Preview */}
      {selectedFile && !isUploading && (
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{getFileIcon(selectedFile)}</span>
                <div>
                  <p className="font-medium">{selectedFile.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleRemoveFile}
                disabled={isUploading}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Processing Options */}
      {!isUploading && (
        <Card>
          <CardContent className="p-6 space-y-4">
            <h3 className="text-lg font-medium">Processing Options</h3>
            
            {/* OCR Toggle */}
            <div className="flex items-start space-x-3">
              <Checkbox
                id="ocr"
                checked={ocrEnabled}
                onCheckedChange={(checked) => setOcrEnabled(checked as boolean)}
              />
              <div className="space-y-1">
                <Label htmlFor="ocr" className="font-medium">
                  Enable OCR for scanned documents
                </Label>
                <p className="text-sm text-muted-foreground">
                  Use this option for PDFs that contain scanned images or text that can&apos;t be selected
                </p>
              </div>
            </div>

            {/* Processing Mode */}
            <div className="space-y-3">
              <Label className="font-medium">Processing Mode</Label>
              <RadioGroup
                value={processingMode}
                onValueChange={(value) => setProcessingMode(value as 'fast' | 'quality')}
              >
                <div className="flex items-start space-x-3">
                  <RadioGroupItem value="fast" id="fast" />
                  <div className="space-y-1">
                    <Label htmlFor="fast" className="font-medium">
                      Fast
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      Quick processing (~30 seconds). Best for text-heavy documents.
                    </p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <RadioGroupItem value="quality" id="quality" />
                  <div className="space-y-1">
                    <Label htmlFor="quality" className="font-medium">
                      Quality
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      Thorough processing (~2 minutes). Better for complex layouts and images.
                    </p>
                  </div>
                </div>
              </RadioGroup>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Upload Progress */}
      {isUploading && (
        <Card>
          <CardContent className="p-6 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Uploading {selectedFile?.name}</span>
              <span className="text-sm text-muted-foreground">{uploadProgress}%</span>
            </div>
            <Progress value={uploadProgress} className="w-full" />
          </CardContent>
        </Card>
      )}

      {/* Error Messages */}
      {validationError && (
        <Alert variant="destructive">
          <AlertDescription>{validationError}</AlertDescription>
        </Alert>
      )}
      
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Upload Button */}
      {selectedFile && !isUploading && (
        <Button 
          onClick={handleUpload} 
          className="w-full" 
          size="lg"
          disabled={!selectedFile || isUploading}
        >
          Upload Document
        </Button>
      )}
    </div>
  );
};