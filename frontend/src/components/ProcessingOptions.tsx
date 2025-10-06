import React from 'react';
import { Checkbox } from '@/components/ui/checkbox';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';

interface ProcessingOptionsProps {
  ocrEnabled: boolean;
  processingMode: 'fast' | 'quality';
  onOcrEnabledChange: (enabled: boolean) => void;
  onProcessingModeChange: (mode: 'fast' | 'quality') => void;
  disabled?: boolean;
}

export const ProcessingOptions: React.FC<ProcessingOptionsProps> = ({
  ocrEnabled,
  processingMode,
  onOcrEnabledChange,
  onProcessingModeChange,
  disabled = false,
}) => {
  return (
    <Card>
      <CardContent className="p-4 md:p-6 space-y-4 md:space-y-6">
        <h3 className="text-base md:text-lg font-medium">Processing Options</h3>

        {/* OCR Toggle */}
        <div className="flex items-start space-x-3 md:space-x-4">
          <Checkbox
            id="ocr"
            checked={ocrEnabled}
            onCheckedChange={(checked) => onOcrEnabledChange(checked as boolean)}
            disabled={disabled}
            aria-describedby="ocr-description"
            className="mt-0.5 min-w-[20px] min-h-[20px]"
            style={{
              minWidth: '44px',
              minHeight: '44px',
              width: '20px',
              height: '20px'
            }}
          />
          <div className="space-y-1 flex-1 min-w-0">
            <Label
              htmlFor="ocr"
              className={`font-medium cursor-pointer text-base md:text-sm ${disabled ? 'opacity-50' : ''}`}
            >
              Enable OCR for scanned documents
            </Label>
            <p
              id="ocr-description"
              className="text-sm text-muted-foreground break-words"
            >
              Use this option for PDFs that contain scanned images or text that can&apos;t be selected
            </p>
          </div>
        </div>

        {/* Processing Mode */}
        <fieldset className="space-y-3 md:space-y-4" disabled={disabled}>
          <legend className="font-medium text-base md:text-sm">Processing Mode</legend>
          <RadioGroup
            value={processingMode}
            onValueChange={(value) => onProcessingModeChange(value as 'fast' | 'quality')}
            disabled={disabled}
            className="space-y-3 md:space-y-4"
          >
            <div className="flex items-start space-x-3 md:space-x-4">
              <RadioGroupItem
                value="fast"
                id="fast"
                aria-describedby="fast-description"
                className="mt-0.5"
                style={{
                  minWidth: '44px',
                  minHeight: '44px'
                }}
              />
              <div className="space-y-1 flex-1 min-w-0">
                <Label
                  htmlFor="fast"
                  className={`font-medium cursor-pointer text-base md:text-sm ${disabled ? 'opacity-50' : ''}`}
                >
                  Fast
                </Label>
                <p
                  id="fast-description"
                  className="text-sm text-muted-foreground break-words"
                >
                  Quick processing (~30 seconds). Best for text-heavy documents.
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3 md:space-x-4">
              <RadioGroupItem
                value="quality"
                id="quality"
                aria-describedby="quality-description"
                className="mt-0.5"
                style={{
                  minWidth: '44px',
                  minHeight: '44px'
                }}
              />
              <div className="space-y-1 flex-1 min-w-0">
                <Label
                  htmlFor="quality"
                  className={`font-medium cursor-pointer text-base md:text-sm ${disabled ? 'opacity-50' : ''}`}
                >
                  Quality
                </Label>
                <p
                  id="quality-description"
                  className="text-sm text-muted-foreground break-words"
                >
                  Thorough processing (~2 minutes). Better for complex layouts and images.
                </p>
              </div>
            </div>
          </RadioGroup>
        </fieldset>
      </CardContent>
    </Card>
  );
};