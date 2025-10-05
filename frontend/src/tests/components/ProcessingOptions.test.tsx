import { render, screen, fireEvent } from '@testing-library/react';
import { ProcessingOptions } from '@/components/ProcessingOptions';
import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('ProcessingOptions', () => {
  const mockOnOcrEnabledChange = vi.fn();
  const mockOnProcessingModeChange = vi.fn();

  const defaultProps = {
    ocrEnabled: false,
    processingMode: 'fast' as const,
    onOcrEnabledChange: mockOnOcrEnabledChange,
    onProcessingModeChange: mockOnProcessingModeChange,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render processing options heading', () => {
    render(<ProcessingOptions {...defaultProps} />);
    expect(screen.getByText('Processing Options')).toBeInTheDocument();
  });

  it('should render OCR checkbox with correct default state (unchecked)', () => {
    render(<ProcessingOptions {...defaultProps} />);
    const checkbox = screen.getByRole('checkbox', { name: /enable ocr/i });
    expect(checkbox).toBeInTheDocument();
    expect(checkbox).not.toBeChecked();
  });

  it('should render OCR checkbox as checked when ocrEnabled is true', () => {
    render(<ProcessingOptions {...defaultProps} ocrEnabled={true} />);
    const checkbox = screen.getByRole('checkbox', { name: /enable ocr/i });
    expect(checkbox).toBeChecked();
  });

  it('should call onOcrEnabledChange when OCR checkbox is toggled', () => {
    render(<ProcessingOptions {...defaultProps} />);
    const checkbox = screen.getByRole('checkbox', { name: /enable ocr/i });
    
    fireEvent.click(checkbox);
    expect(mockOnOcrEnabledChange).toHaveBeenCalledWith(true);
  });

  it('should display OCR help text correctly', () => {
    render(<ProcessingOptions {...defaultProps} />);
    expect(
      screen.getByText(/use this option for pdfs that contain scanned images/i)
    ).toBeInTheDocument();
  });

  it('should render processing mode radio group with Fast option', () => {
    render(<ProcessingOptions {...defaultProps} />);
    const fastRadio = screen.getByRole('radio', { name: /fast/i });
    expect(fastRadio).toBeInTheDocument();
    expect(fastRadio).toBeChecked();
  });

  it('should render processing mode radio group with Quality option', () => {
    render(<ProcessingOptions {...defaultProps} />);
    const qualityRadio = screen.getByRole('radio', { name: /quality/i });
    expect(qualityRadio).toBeInTheDocument();
    expect(qualityRadio).not.toBeChecked();
  });

  it('should show Quality mode as selected when processingMode is quality', () => {
    render(<ProcessingOptions {...defaultProps} processingMode="quality" />);
    const qualityRadio = screen.getByRole('radio', { name: /quality/i });
    expect(qualityRadio).toBeChecked();
  });

  it('should call onProcessingModeChange when processing mode is changed', () => {
    render(<ProcessingOptions {...defaultProps} />);
    const qualityRadio = screen.getByRole('radio', { name: /quality/i });
    
    fireEvent.click(qualityRadio);
    expect(mockOnProcessingModeChange).toHaveBeenCalledWith('quality');
  });

  it('should display Fast mode help text correctly', () => {
    render(<ProcessingOptions {...defaultProps} />);
    expect(
      screen.getByText(/quick processing \(~30 seconds\)/i)
    ).toBeInTheDocument();
  });

  it('should display Quality mode help text correctly', () => {
    render(<ProcessingOptions {...defaultProps} />);
    expect(
      screen.getByText(/thorough processing \(~2 minutes\)/i)
    ).toBeInTheDocument();
  });

  it('should disable OCR checkbox when disabled prop is true', () => {
    render(<ProcessingOptions {...defaultProps} disabled={true} />);
    const checkbox = screen.getByRole('checkbox', { name: /enable ocr/i });
    expect(checkbox).toBeDisabled();
  });

  it('should disable radio buttons when disabled prop is true', () => {
    render(<ProcessingOptions {...defaultProps} disabled={true} />);
    const fastRadio = screen.getByRole('radio', { name: /fast/i });
    const qualityRadio = screen.getByRole('radio', { name: /quality/i });
    
    expect(fastRadio).toBeDisabled();
    expect(qualityRadio).toBeDisabled();
  });

  it('should have proper ARIA labels for OCR checkbox', () => {
    render(<ProcessingOptions {...defaultProps} />);
    const checkbox = screen.getByRole('checkbox', { name: /enable ocr/i });
    expect(checkbox).toHaveAttribute('aria-describedby', 'ocr-description');
  });

  it('should have proper ARIA labels for Fast mode radio', () => {
    render(<ProcessingOptions {...defaultProps} />);
    const fastRadio = screen.getByRole('radio', { name: /fast/i });
    expect(fastRadio).toHaveAttribute('aria-describedby', 'fast-description');
  });

  it('should have proper ARIA labels for Quality mode radio', () => {
    render(<ProcessingOptions {...defaultProps} />);
    const qualityRadio = screen.getByRole('radio', { name: /quality/i });
    expect(qualityRadio).toHaveAttribute('aria-describedby', 'quality-description');
  });

  it('should support keyboard navigation for checkbox', () => {
    render(<ProcessingOptions {...defaultProps} />);
    const checkbox = screen.getByRole('checkbox', { name: /enable ocr/i });
    
    checkbox.focus();
    expect(checkbox).toHaveFocus();
    
    fireEvent.keyDown(checkbox, { key: ' ', code: 'Space' });
    expect(mockOnOcrEnabledChange).toHaveBeenCalledWith(true);
  });

  it('should support keyboard navigation for radio group', () => {
    render(<ProcessingOptions {...defaultProps} />);
    const qualityRadio = screen.getByRole('radio', { name: /quality/i });
    
    qualityRadio.focus();
    expect(qualityRadio).toHaveFocus();
    
    fireEvent.click(qualityRadio);
    expect(mockOnProcessingModeChange).toHaveBeenCalledWith('quality');
  });

  it('should render with all options at once', () => {
    render(<ProcessingOptions {...defaultProps} ocrEnabled={true} processingMode="quality" />);
    
    const checkbox = screen.getByRole('checkbox', { name: /enable ocr/i });
    const qualityRadio = screen.getByRole('radio', { name: /quality/i });
    
    expect(checkbox).toBeChecked();
    expect(qualityRadio).toBeChecked();
  });

  it('should maintain component state correctly when toggling between modes', () => {
    const { rerender } = render(<ProcessingOptions {...defaultProps} />);
    
    // Initially Fast mode
    let fastRadio = screen.getByRole('radio', { name: /fast/i });
    expect(fastRadio).toBeChecked();
    
    // Change to Quality mode
    rerender(<ProcessingOptions {...defaultProps} processingMode="quality" />);
    let qualityRadio = screen.getByRole('radio', { name: /quality/i });
    expect(qualityRadio).toBeChecked();
    
    // Change back to Fast mode
    rerender(<ProcessingOptions {...defaultProps} processingMode="fast" />);
    fastRadio = screen.getByRole('radio', { name: /fast/i });
    expect(fastRadio).toBeChecked();
  });
});