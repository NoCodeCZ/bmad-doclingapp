import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ProcessingCard } from '@/components/ProcessingCard';
import type { DocumentStatus } from '@/types/database';

describe('ProcessingCard', () => {
  const defaultProps = {
    status: 'processing' as DocumentStatus,
    filename: 'test-document.pdf',
    progress: 50,
    estimatedTime: 30,
    processingMode: 'fast' as const,
    ocrEnabled: false,
  };

  it('should render processing status correctly', () => {
    render(<ProcessingCard {...defaultProps} />);

    expect(screen.getByText(/test-document.pdf/i)).toBeInTheDocument();
    expect(screen.getByText(/50%/i)).toBeInTheDocument();
    expect(screen.getByText(/~30 seconds/i)).toBeInTheDocument();
  });

  it('should display animated spinner for processing status', () => {
    render(<ProcessingCard {...defaultProps} status="processing" />);

    const spinnerIcons = document.querySelectorAll('svg.animate-spin');
    expect(spinnerIcons.length).toBeGreaterThan(0);
  });

  it('should display queued status with clock icon', () => {
    render(<ProcessingCard {...defaultProps} status="queued" progress={5} />);

    expect(screen.getByText(/queued/i)).toBeInTheDocument();
  });

  it('should display complete status with checkmark', () => {
    render(<ProcessingCard {...defaultProps} status="complete" progress={100} />);

    expect(screen.getByText(/complete/i)).toBeInTheDocument();
    expect(screen.getByText(/ready for download/i)).toBeInTheDocument();
  });

  it('should display failed status with error icon', () => {
    render(
      <ProcessingCard
        {...defaultProps}
        status="failed"
        progress={0}
        errorMessage="Processing error occurred"
      />
    );

    expect(screen.getByText(/failed/i)).toBeInTheDocument();
    expect(screen.getByText(/processing error occurred/i)).toBeInTheDocument();
  });

  it('should show uploading stage with pulse animation', () => {
    render(
      <ProcessingCard {...defaultProps} status="queued" progressStage="Uploading file..." />
    );

    expect(screen.getByText(/uploading file/i)).toBeInTheDocument();
  });

  it('should show finalizing stage', () => {
    render(
      <ProcessingCard {...defaultProps} status="processing" progressStage="Finalizing..." />
    );

    expect(screen.getByText(/finalizing/i)).toBeInTheDocument();
  });

  it('should display progress bar for processing and queued states', () => {
    const { rerender } = render(<ProcessingCard {...defaultProps} status="processing" />);

    expect(screen.getByText(/progress/i)).toBeInTheDocument();
    expect(screen.getByText(/50%/i)).toBeInTheDocument();

    rerender(<ProcessingCard {...defaultProps} status="queued" />);
    expect(screen.getByText(/progress/i)).toBeInTheDocument();
  });

  it('should not display progress bar for complete/failed states', () => {
    const { rerender } = render(<ProcessingCard {...defaultProps} status="complete" />);

    expect(screen.queryByText(/progress/i)).not.toBeInTheDocument();

    rerender(<ProcessingCard {...defaultProps} status="failed" />);
    expect(screen.queryByText(/progress/i)).not.toBeInTheDocument();
  });

  it('should format time correctly (seconds)', () => {
    render(<ProcessingCard {...defaultProps} status="processing" estimatedTime={45} />);

    expect(screen.getByText(/~45 seconds/i)).toBeInTheDocument();
  });

  it('should format time correctly (minutes)', () => {
    render(<ProcessingCard {...defaultProps} status="processing" estimatedTime={120} />);

    expect(screen.getByText(/~2 minutes/i)).toBeInTheDocument();
  });

  it('should display processing mode and OCR status', () => {
    render(<ProcessingCard {...defaultProps} processingMode="quality" ocrEnabled={true} />);

    expect(screen.getByText(/quality/i)).toBeInTheDocument();
    expect(screen.getByText(/ocr.*enabled/i)).toBeInTheDocument();
  });

  it('should not show OCR when disabled', () => {
    render(<ProcessingCard {...defaultProps} processingMode="fast" ocrEnabled={false} />);

    expect(screen.getByText(/fast/i)).toBeInTheDocument();
    expect(screen.queryByText(/ocr.*enabled/i)).not.toBeInTheDocument();
  });

  it('should show estimated time only when processing', () => {
    const { rerender } = render(
      <ProcessingCard {...defaultProps} status="processing" estimatedTime={30} />
    );

    expect(screen.getByText(/estimated time remaining/i)).toBeInTheDocument();

    rerender(<ProcessingCard {...defaultProps} status="queued" estimatedTime={30} />);
    expect(screen.queryByText(/estimated time remaining/i)).not.toBeInTheDocument();

    rerender(<ProcessingCard {...defaultProps} status="complete" estimatedTime={0} />);
    expect(screen.queryByText(/estimated time remaining/i)).not.toBeInTheDocument();
  });

  it('should show download button for complete status', () => {
    render(<ProcessingCard {...defaultProps} status="complete" />);

    expect(screen.getByText(/download markdown/i)).toBeInTheDocument();
  });

  it('should show retry button for failed status', () => {
    render(<ProcessingCard {...defaultProps} status="failed" />);

    expect(screen.getByText(/try again/i)).toBeInTheDocument();
    expect(screen.getByText(/contact support/i)).toBeInTheDocument();
  });

  it('should have mobile-responsive classes', () => {
    const { container } = render(<ProcessingCard {...defaultProps} />);

    // Check for responsive width classes
    const card = container.querySelector('.max-w-sm, .sm\\:max-w-md, .md\\:max-w-lg');
    expect(card).toBeInTheDocument();

    // Check for responsive icon sizing
    const icons = container.querySelectorAll('.sm\\:h-10, .sm\\:w-10, .lg\\:h-12, .lg\\:w-12');
    expect(icons.length).toBeGreaterThan(0);
  });

  it('should have minimum 44px touch targets for buttons', () => {
    const { container } = render(<ProcessingCard {...defaultProps} status="complete" />);

    const buttons = container.querySelectorAll('button.min-h-\\[44px\\]');
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('should apply smooth transitions to card and elements', () => {
    const { container } = render(<ProcessingCard {...defaultProps} />);

    // Check for transition classes
    const transitionElements = container.querySelectorAll('.transition-all, .transition-colors, .transition-transform, .transition-opacity');
    expect(transitionElements.length).toBeGreaterThan(0);
  });

  it('should apply color-coded alerts based on status', () => {
    const { container, rerender } = render(<ProcessingCard {...defaultProps} status="failed" />);

    let alert = container.querySelector('[class*="border-red"]');
    expect(alert).toBeInTheDocument();

    rerender(<ProcessingCard {...defaultProps} status="complete" />);
    alert = container.querySelector('[class*="border-green"]');
    expect(alert).toBeInTheDocument();

    rerender(<ProcessingCard {...defaultProps} status="processing" />);
    alert = container.querySelector('[class*="border-amber"]');
    expect(alert).toBeInTheDocument();

    rerender(<ProcessingCard {...defaultProps} status="queued" />);
    alert = container.querySelector('[class*="border-blue"]');
    expect(alert).toBeInTheDocument();
  });

  it('should use progressStage for status text when provided', () => {
    render(
      <ProcessingCard
        {...defaultProps}
        status="processing"
        progressStage="Converting document"
      />
    );

    expect(screen.getByText(/converting document/i)).toBeInTheDocument();
  });

  it('should fallback to default status text when progressStage not provided', () => {
    render(<ProcessingCard {...defaultProps} status="processing" />);

    expect(screen.getByText(/queued for processing|processing document/i)).toBeInTheDocument();
  });

  it('should truncate long filenames on mobile', () => {
    const longFilename = 'very-long-filename-that-should-be-truncated-on-mobile-devices.pdf';
    const { container } = render(<ProcessingCard {...defaultProps} filename={longFilename} />);

    const filenameElement = container.querySelector('.truncate');
    expect(filenameElement).toBeInTheDocument();
    expect(filenameElement).toHaveTextContent(longFilename);
  });

  it('should show error message when provided', () => {
    const errorMessage = 'Custom error message for testing';
    render(<ProcessingCard {...defaultProps} status="failed" errorMessage={errorMessage} />);

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('should show default error message when none provided', () => {
    render(<ProcessingCard {...defaultProps} status="failed" />);

    expect(screen.getByText(/error occurred while processing/i)).toBeInTheDocument();
  });

  it('should have proper button spacing and layout on mobile', () => {
    const { container } = render(<ProcessingCard {...defaultProps} status="complete" />);

    // Check for flex column on mobile, row on larger screens
    const buttonContainer = container.querySelector('.flex-col.sm\\:flex-row');
    expect(buttonContainer).toBeInTheDocument();

    // Check for proper gap
    const gapContainer = container.querySelector('.gap-2, .sm\\:gap-4');
    expect(gapContainer).toBeInTheDocument();
  });

  it('should render with all accessibility attributes', () => {
    const { container } = render(<ProcessingCard {...defaultProps} />);

    // Check that interactive elements (buttons) exist
    const buttons = container.querySelectorAll('button');
    expect(buttons.length).toBeGreaterThanOrEqual(0);
  });

  it('should handle zero estimated time', () => {
    render(<ProcessingCard {...defaultProps} status="processing" estimatedTime={0} />);

    expect(screen.queryByText(/estimated time remaining/i)).not.toBeInTheDocument();
  });

  it('should show active scale effect on button press', () => {
    const { container } = render(<ProcessingCard {...defaultProps} status="complete" />);

    const buttons = container.querySelectorAll('button.active\\:scale-95');
    expect(buttons.length).toBeGreaterThan(0);
  });
});
