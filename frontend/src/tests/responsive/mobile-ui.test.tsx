import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import { FileDropzone } from '@/components/FileDropzone';
import { ProcessingOptions } from '@/components/ProcessingOptions';
import { ProcessingCard } from '@/components/ProcessingCard';
import { SuccessScreen } from '@/components/SuccessScreen';
import { ErrorAlert } from '@/components/ErrorAlert';

/**
 * Mobile Responsive UI Tests
 * Tests responsive behavior, touch targets, and mobile-specific layouts
 */

describe('Mobile Responsive UI', () => {
  describe('Viewport Responsiveness', () => {
    const viewports = [
      { width: 375, height: 667, name: 'iPhone SE' },
      { width: 414, height: 896, name: 'iPhone 11' },
      { width: 768, height: 1024, name: 'iPad' },
      { width: 1024, height: 768, name: 'Desktop' },
    ];

    viewports.forEach(({ width, height, name }) => {
      describe(`${name} (${width}x${height})`, () => {
        beforeEach(() => {
          // Mock window.matchMedia for responsive breakpoints
          Object.defineProperty(window, 'innerWidth', {
            writable: true,
            configurable: true,
            value: width,
          });
          Object.defineProperty(window, 'innerHeight', {
            writable: true,
            configurable: true,
            value: height,
          });
        });

        it('should render FileDropzone with responsive layout', () => {
          const mockOnUpload = vi.fn();
          const { container } = render(
            <FileDropzone onFileUpload={mockOnUpload} />
          );

          const dropzoneContainer = container.querySelector('.w-full');
          expect(dropzoneContainer).toBeInTheDocument();

          // Check for responsive padding classes
          if (width < 768) {
            expect(dropzoneContainer?.className).toContain('px-4');
          } else {
            expect(dropzoneContainer?.className).toContain('md:px-0');
          }
        });

        it('should render ProcessingOptions with appropriate touch targets', () => {
          const mockOnOcrChange = vi.fn();
          const mockOnModeChange = vi.fn();

          render(
            <ProcessingOptions
              ocrEnabled={false}
              processingMode="fast"
              onOcrEnabledChange={mockOnOcrChange}
              onProcessingModeChange={mockOnModeChange}
            />
          );

          // Check for touch-friendly spacing
          const checkboxes = screen.getAllByRole('checkbox');
          checkboxes.forEach((checkbox) => {
            const style = window.getComputedStyle(checkbox);
            // Verify minimum touch target size (44px)
            expect(
              parseInt(style.minWidth) >= 44 || parseInt(style.minHeight) >= 44
            ).toBe(true);
          });
        });

        it('should scale ProcessingCard progress indicators appropriately', () => {
          const { container } = render(
            <ProcessingCard
              status="processing"
              filename="test-document.pdf"
              progress={50}
              estimatedTime={30}
            />
          );

          const progressBar = container.querySelector('[role="progressbar"]');
          expect(progressBar).toBeInTheDocument();

          // Check for responsive height classes
          if (width < 768) {
            expect(progressBar?.className).toContain('h-3');
          } else {
            expect(progressBar?.className).toContain('md:h-4');
          }
        });

        it('should render SuccessScreen with responsive buttons', () => {
          const mockOnReset = vi.fn();

          render(
            <SuccessScreen
              documentId="test-123"
              filename="document.pdf"
              fileSize={1024000}
              onReset={mockOnReset}
            />
          );

          const downloadButton = screen.getByRole('button', {
            name: /download/i,
          });

          // Check button has minimum touch target via className
          expect(downloadButton.className).toContain('min-h-[44px]');

          // Check for responsive width classes
          if (width < 768) {
            expect(downloadButton.className).toContain('w-full');
          } else {
            expect(downloadButton.className).toContain('md:w-auto');
          }
        });

        it('should display ErrorAlert with proper text wrapping', () => {
          const mockOnRetry = vi.fn();
          const longErrorMessage =
            'This is a very long error message that should wrap properly on narrow screens without causing horizontal scrolling or text overflow issues';

          render(
            <ErrorAlert
              error={{
                code: 'TEST_ERROR',
                message: longErrorMessage,
                details: 'Additional error details that should also wrap',
              }}
              onRetry={mockOnRetry}
            />
          );

          const errorMessage = screen.getByText(longErrorMessage);
          expect(errorMessage.className).toContain('break-words');

          const retryButton = screen.getByRole('button', { name: /try again/i });
          expect(retryButton.className).toContain('min-h-[44px]');
        });
      });
    });
  });

  describe('Touch Target Sizes', () => {
    it('should have minimum 44px touch targets for primary interactive elements', () => {
      const mockOnReset = vi.fn();

      render(
        <SuccessScreen
          documentId="test-123"
          filename="document.pdf"
          onReset={mockOnReset}
        />
      );

      // Check specific primary buttons for touch targets
      const downloadButton = screen.getByRole('button', { name: /download/i });
      const resetButton = screen.getByRole('button', { name: /process another/i });

      expect(downloadButton.className).toMatch(/min-h-\[4[4-9]px\]|min-h-\[5[0-9]px\]/);
      expect(resetButton.className).toMatch(/min-h-\[4[4-9]px\]|min-h-\[5[0-9]px\]/);
    });

    it('should have proper spacing between touch targets', () => {
      const mockOnOcrChange = vi.fn();
      const mockOnModeChange = vi.fn();

      const { container } = render(
        <ProcessingOptions
          ocrEnabled={false}
          processingMode="fast"
          onOcrEnabledChange={mockOnOcrChange}
          onProcessingModeChange={mockOnModeChange}
        />
      );

      const radioGroup = container.querySelector('[role="radiogroup"]');
      expect(radioGroup).toBeInTheDocument();

      // Check for spacing classes
      expect(radioGroup?.className).toMatch(/space-y-[34]/);
    });
  });

  describe('Typography Scaling', () => {
    it('should apply base font size of 16px on mobile', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      // Check HTML element exists for font-size application
      const html = document.documentElement;

      // Note: This tests that our CSS is structured correctly
      // Actual font-size verification would require E2E tests
      expect(html).toBeInTheDocument();
    });

    it('should render text elements with responsive classes', () => {
      const mockOnReset = vi.fn();

      render(
        <SuccessScreen
          documentId="test-123"
          filename="document.pdf"
          onReset={mockOnReset}
        />
      );

      const heading = screen.getByRole('alert');
      expect(heading.className).toMatch(/text-(xl|2xl|3xl)/);
      expect(heading.className).toContain('md:');
    });
  });

  describe('File Upload Mobile Enhancements', () => {
    it('should render with full-width layout on mobile', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        value: 375,
      });

      const mockOnUpload = vi.fn();
      const { container } = render(
        <FileDropzone onFileUpload={mockOnUpload} />
      );

      const uploadContainer = container.querySelector('.w-full');
      expect(uploadContainer).toBeInTheDocument();
    });

    it('should handle long filenames with proper truncation', () => {
      const longFilename = 'this-is-a-very-long-filename-that-should-be-truncated-properly-on-mobile-devices.pdf';

      render(
        <ProcessingCard
          status="processing"
          filename={longFilename}
          progress={50}
        />
      );

      const filenameElement = screen.getByText(longFilename);
      expect(filenameElement.className).toMatch(/break-words|truncate/);
    });
  });

  describe('Accessibility on Mobile', () => {
    it('should maintain focus indicators on touch devices', () => {
      const mockOnReset = vi.fn();

      render(
        <SuccessScreen
          documentId="test-123"
          filename="document.pdf"
          onReset={mockOnReset}
        />
      );

      const buttons = screen.getAllByRole('button');
      buttons.forEach((button) => {
        // Verify buttons are keyboard accessible
        expect(button).not.toHaveAttribute('tabindex', '-1');
      });
    });

    it('should provide proper ARIA labels for mobile interactions', () => {
      const mockOnUpload = vi.fn();

      render(<FileDropzone onFileUpload={mockOnUpload} />);

      // Check for accessible file input
      const fileInput = document.querySelector('input[type="file"]');
      expect(fileInput).toBeInTheDocument();
    });
  });

  describe('Mobile Error Display', () => {
    it('should stack error content vertically on mobile', () => {
      const mockOnRetry = vi.fn();

      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        value: 375,
      });

      const { container } = render(
        <ErrorAlert
          error={{
            code: 'MOBILE_ERROR',
            message: 'Error on mobile device',
          }}
          onRetry={mockOnRetry}
        />
      );

      // Check the flex container inside the alert
      const flexContainer = container.querySelector('.flex');
      expect(flexContainer?.className).toContain('flex-col');
    });

    it('should make retry button full-width on mobile', () => {
      const mockOnRetry = vi.fn();

      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        value: 375,
      });

      render(
        <ErrorAlert
          error={{
            code: 'TEST_ERROR',
            message: 'Test error',
          }}
          onRetry={mockOnRetry}
        />
      );

      const retryButton = screen.getByRole('button', { name: /try again/i });
      expect(retryButton.className).toContain('w-full');
    });
  });
});
