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
      <CardContent className="p-6 space-y-4">
        <h3 className="text-lg font-medium">Processing Options</h3>
        
        {/* OCR Toggle */}
        <div className="flex items-start space-x-3">
          <Checkbox
            id="ocr"
            checked={ocrEnabled}
            onCheckedChange={(checked) => onOcrEnabledChange(checked as boolean)}
            disabled={disabled}
            aria-describedby="ocr-description"
          />
          <div className="space-y-1 flex-1">
            <Label 
              htmlFor="ocr" 
              className={`font-medium cursor-pointer ${disabled ? 'opacity-50' : ''}`}
            >
              Enable OCR for scanned documents
            </Label>
            <p 
              id="ocr-description" 
              className="text-sm text-muted-foreground"
            >
              Use this option for PDFs that contain scanned images or text that can&apos;t be selected
            </p>
          </div>
        </div>

        {/* Processing Mode */}
        <fieldset className="space-y-3" disabled={disabled}>
          <legend className="font-medium">Processing Mode</legend>
          <RadioGroup
            value={processingMode}
            onValueChange={(value) => onProcessingModeChange(value as 'fast' | 'quality')}
            disabled={disabled}
          >
            <div className="flex items-start space-x-3">
              <RadioGroupItem 
                value="fast" 
                id="fast"
                aria-describedby="fast-description"
              />
              <div className="space-y-1 flex-1">
                <Label 
                  htmlFor="fast" 
                  className={`font-medium cursor-pointer ${disabled ? 'opacity-50' : ''}`}
                >
                  Fast
                </Label>
                <p 
                  id="fast-description" 
                  className="text-sm text-muted-foreground"
                >
                  Quick processing (~30 seconds). Best for text-heavy documents.
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <RadioGroupItem 
                value="quality" 
                id="quality"
                aria-describedby="quality-description"
              />
              <div className="space-y-1 flex-1">
                <Label 
                  htmlFor="quality" 
                  className={`font-medium cursor-pointer ${disabled ? 'opacity-50' : ''}`}
                >
                  Quality
                </Label>
                <p 
                  id="quality-description" 
                  className="text-sm text-muted-foreground"
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