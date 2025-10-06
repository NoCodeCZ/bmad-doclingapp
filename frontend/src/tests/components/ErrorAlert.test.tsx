/**
 * ErrorAlert Component Tests
 *
 * Tests AC 1: Error messages displayed in prominent error UI component
 * Tests AC 7: Error states include "Try Again" button
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ErrorAlert } from '@/components/ErrorAlert';

describe('ErrorAlert', () => {
  it('should display error message with retry button', () => {
    const mockRetry = vi.fn();
    const error = {
      code: 'FILE_TOO_LARGE',
      message: 'File too large (15MB) - maximum size is 10MB. Try compressing your PDF or splitting into multiple files.',
      timestamp: '2025-10-06T13:00:00Z',
    };

    render(<ErrorAlert error={error} onRetry={mockRetry} />);

    // Error message should be displayed
    expect(
      screen.getByText(/File too large \(15MB\) - maximum size is 10MB/)
    ).toBeInTheDocument();

    // Try Again button should be present
    const retryButton = screen.getByRole('button', { name: /try again/i });
    expect(retryButton).toBeInTheDocument();

    // Clicking retry button should call onRetry
    fireEvent.click(retryButton);
    expect(mockRetry).toHaveBeenCalledTimes(1);
  });

  it('should display unsupported format error with allowed formats', () => {
    const error = {
      code: 'UNSUPPORTED_FORMAT',
      message: 'Cannot process .txt files - supported formats: PDF, DOCX, PPTX, XLSX.',
    };

    render(<ErrorAlert error={error} />);

    expect(
      screen.getByText(/Cannot process \.txt files - supported formats/)
    ).toBeInTheDocument();
  });

  it('should display processing timeout error', () => {
    const error = {
      code: 'PROCESSING_TIMEOUT',
      message:
        'Processing took too long - try enabling Fast mode or reducing document complexity.',
    };

    render(<ErrorAlert error={error} />);

    expect(
      screen.getByText(/Processing took too long - try enabling Fast mode/)
    ).toBeInTheDocument();
  });

  it('should display corrupted file error', () => {
    const error = {
      code: 'CORRUPTED_FILE',
      message:
        "Unable to process file - ensure the document isn't password-protected or corrupted.",
    };

    render(<ErrorAlert error={error} />);

    expect(
      screen.getByText(
        /Unable to process file - ensure the document isn't password-protected/
      )
    ).toBeInTheDocument();
  });

  it('should display service error with user-friendly message', () => {
    const error = {
      code: 'SERVICE_ERROR',
      message: 'Processing failed due to server error - please try again.',
      requestId: 'test-request-id-123',
    };

    render(<ErrorAlert error={error} />);

    expect(
      screen.getByText(/Processing failed due to server error/)
    ).toBeInTheDocument();

    // Request ID should be displayed for debugging
    expect(screen.getByText(/Reference ID: test-request-id-123/)).toBeInTheDocument();
  });

  it('should have proper accessibility attributes', () => {
    const error = {
      code: 'TEST_ERROR',
      message: 'Test error message',
    };

    render(<ErrorAlert error={error} />);

    const alert = screen.getByRole('alert');
    expect(alert).toHaveAttribute('aria-live', 'assertive');
    expect(alert).toHaveAttribute('aria-labelledby', 'error-alert-title');
    expect(alert).toHaveAttribute('aria-describedby', 'error-alert-message');
  });

  it('should display error details when provided', () => {
    const error = {
      code: 'TEST_ERROR',
      message: 'Main error message',
      details: 'Additional error details for debugging',
    };

    render(<ErrorAlert error={error} />);

    expect(screen.getByText('Main error message')).toBeInTheDocument();
    expect(
      screen.getByText('Additional error details for debugging')
    ).toBeInTheDocument();
  });

  it('should not display retry button when onRetry is not provided', () => {
    const error = {
      code: 'TEST_ERROR',
      message: 'Test error message',
    };

    render(<ErrorAlert error={error} />);

    expect(screen.queryByRole('button', { name: /try again/i })).not.toBeInTheDocument();
  });

  it('should apply custom className when provided', () => {
    const error = {
      code: 'TEST_ERROR',
      message: 'Test error message',
    };

    const { container } = render(
      <ErrorAlert error={error} className="custom-class" />
    );

    const alert = container.querySelector('.custom-class');
    expect(alert).toBeInTheDocument();
  });

  it('should have proper error icon', () => {
    const error = {
      code: 'TEST_ERROR',
      message: 'Test error message',
    };

    const { container } = render(<ErrorAlert error={error} />);

    // Check for alert icon (AlertTriangle from lucide-react)
    const icon = container.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });
});
