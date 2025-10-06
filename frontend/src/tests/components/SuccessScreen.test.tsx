/**
 * Tests for SuccessScreen component
 *
 * Covers:
 * - Component rendering with all required elements
 * - Download functionality
 * - Error handling for download failures
 * - Reset functionality
 * - Accessibility features
 * - Filename display and cleaning
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { SuccessScreen } from '@/components/SuccessScreen';

// Mock fetch globally
global.fetch = vi.fn();

describe('SuccessScreen', () => {
  const mockProps = {
    documentId: 'test-doc-123',
    filename: 'sample_report.pdf',
    fileSize: 45000, // 45 KB
    onReset: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Component Rendering', () => {
    it('should render success heading', () => {
      render(<SuccessScreen {...mockProps} />);

      const heading = screen.getByRole('alert');
      expect(heading).toHaveTextContent('Processing Complete!');
    });

    it('should display green checkmark icon', () => {
      const { container } = render(<SuccessScreen {...mockProps} />);

      // Check for green color class
      const icon = container.querySelector('.text-green-500');
      expect(icon).toBeInTheDocument();
    });

    it('should display filename with .md extension', () => {
      render(<SuccessScreen {...mockProps} />);

      expect(screen.getByText(/sample_report\.md/i)).toBeInTheDocument();
    });

    it('should display file size when provided', () => {
      render(<SuccessScreen {...mockProps} />);

      // 45000 bytes = 43.9 KB, should display as "43.9 KB" or "44.0 KB"
      expect(screen.getByText(/\(4[34]\.\d KB\)/)).toBeInTheDocument();
    });

    it('should not display file size when not provided', () => {
      const propsWithoutSize = { ...mockProps, fileSize: undefined };
      render(<SuccessScreen {...propsWithoutSize} />);

      const text = screen.queryByText(/KB|MB/);
      expect(text).not.toBeInTheDocument();
    });

    it('should display download button', () => {
      render(<SuccessScreen {...mockProps} />);

      const downloadButton = screen.getByRole('button', { name: /download.*markdown/i });
      expect(downloadButton).toBeInTheDocument();
    });

    it('should display process another document button', () => {
      render(<SuccessScreen {...mockProps} />);

      const resetButton = screen.getByRole('button', { name: /process another document/i });
      expect(resetButton).toBeInTheDocument();
    });
  });

  describe('Download Functionality', () => {
    it('should trigger download when download button is clicked', async () => {
      const mockBlob = new Blob(['# Test markdown content'], { type: 'text/markdown' });

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        headers: new Headers({
          'Content-Disposition': 'attachment; filename="sample_report.md"',
        }),
        blob: () => Promise.resolve(mockBlob),
      });

      // Mock URL.createObjectURL and revokeObjectURL
      const mockObjectURL = 'blob:mock-url';
      global.URL.createObjectURL = vi.fn(() => mockObjectURL);
      global.URL.revokeObjectURL = vi.fn();

      render(<SuccessScreen {...mockProps} />);

      const downloadButton = screen.getByRole('button', { name: /download.*markdown/i });
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/download/test-doc-123');
      });

      expect(global.URL.createObjectURL).toHaveBeenCalledWith(mockBlob);
      expect(global.URL.revokeObjectURL).toHaveBeenCalledWith(mockObjectURL);
    });

    it('should show downloading state while download is in progress', async () => {
      // Mock a slow response
      (global.fetch as any).mockImplementationOnce(
        () =>
          new Promise((resolve) =>
            setTimeout(
              () =>
                resolve({
                  ok: true,
                  headers: new Headers(),
                  blob: () => Promise.resolve(new Blob(['test'])),
                }),
              100
            )
          )
      );

      render(<SuccessScreen {...mockProps} />);

      const downloadButton = screen.getByRole('button', { name: /download.*markdown/i });
      fireEvent.click(downloadButton);

      // Check for downloading state
      expect(screen.getByText(/downloading\.\.\./i)).toBeInTheDocument();
    });

    it('should use cleaned filename from content-disposition header', async () => {
      const mockBlob = new Blob(['content'], { type: 'text/markdown' });

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        headers: new Headers({
          'Content-Disposition': 'attachment; filename="cleaned_filename.md"',
        }),
        blob: () => Promise.resolve(mockBlob),
      });

      global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
      global.URL.revokeObjectURL = vi.fn();

      // Mock document.createElement to spy on download link
      const mockLink = document.createElement('a');
      const createElementSpy = vi.spyOn(document, 'createElement').mockReturnValue(mockLink);

      render(<SuccessScreen {...mockProps} />);

      const downloadButton = screen.getByRole('button', { name: /download.*markdown/i });
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(mockLink.download).toBe('cleaned_filename.md');
      });

      createElementSpy.mockRestore();
    });
  });

  describe('Error Handling', () => {
    it('should display error message when download fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: () =>
          Promise.resolve({
            detail: 'Download failed - file may have been moved or deleted.',
          }),
      });

      render(<SuccessScreen {...mockProps} />);

      const downloadButton = screen.getByRole('button', { name: /download.*markdown/i });
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(screen.getByText(/download failed/i)).toBeInTheDocument();
      });
    });

    it('should display actionable error message for 404', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: () =>
          Promise.resolve({
            detail: 'Download failed - file may have been moved or deleted. Please process document again.',
          }),
      });

      render(<SuccessScreen {...mockProps} />);

      const downloadButton = screen.getByRole('button', { name: /download.*markdown/i });
      fireEvent.click(downloadButton);

      await waitFor(() => {
        const errorMessage = screen.getByText(/file may have been moved or deleted/i);
        expect(errorMessage).toBeInTheDocument();
      });
    });

    it('should show retry button when download fails', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: 'Download failed' }),
      });

      render(<SuccessScreen {...mockProps} />);

      const downloadButton = screen.getByRole('button', { name: /download.*markdown/i });
      fireEvent.click(downloadButton);

      await waitFor(() => {
        const retryButton = screen.getByRole('button', { name: /try again/i });
        expect(retryButton).toBeInTheDocument();
      });
    });

    it('should retry download when retry button is clicked', async () => {
      // First call fails
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: 'Download failed' }),
      });

      render(<SuccessScreen {...mockProps} />);

      const downloadButton = screen.getByRole('button', { name: /download.*markdown/i });
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(screen.getByText(/download failed/i)).toBeInTheDocument();
      });

      // Second call succeeds
      const mockBlob = new Blob(['content'], { type: 'text/markdown' });
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        headers: new Headers(),
        blob: () => Promise.resolve(mockBlob),
      });

      global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
      global.URL.revokeObjectURL = vi.fn();

      const retryButton = screen.getByRole('button', { name: /try again/i });
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledTimes(2);
      });
    });

    it('should handle network errors gracefully', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      render(<SuccessScreen {...mockProps} />);

      const downloadButton = screen.getByRole('button', { name: /download.*markdown/i });
      fireEvent.click(downloadButton);

      await waitFor(() => {
        const errorMessage = screen.getByText(/download failed/i);
        expect(errorMessage).toBeInTheDocument();
      });
    });
  });

  describe('Reset Functionality', () => {
    it('should call onReset when Process Another Document is clicked', async () => {
      render(<SuccessScreen {...mockProps} />);

      const resetButton = screen.getByRole('button', { name: /process another document/i });
      fireEvent.click(resetButton);

      expect(mockProps.onReset).toHaveBeenCalledTimes(1);
    });

    it('should not allow reset while download is in progress', async () => {
      // Mock a slow download
      (global.fetch as any).mockImplementationOnce(
        () =>
          new Promise((resolve) =>
            setTimeout(
              () =>
                resolve({
                  ok: true,
                  headers: new Headers(),
                  blob: () => Promise.resolve(new Blob(['test'])),
                }),
              100
            )
          )
      );

      render(<SuccessScreen {...mockProps} />);

      const downloadButton = screen.getByRole('button', { name: /download.*markdown/i });
      fireEvent.click(downloadButton);

      const resetButton = screen.getByRole('button', { name: /process another document/i });
      expect(resetButton).toBeDisabled();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels on download button', () => {
      render(<SuccessScreen {...mockProps} />);

      const downloadButton = screen.getByRole('button', { name: /download sample_report\.md/i });
      expect(downloadButton).toHaveAccessibleName();
    });

    it('should have alert role on success heading', () => {
      render(<SuccessScreen {...mockProps} />);

      const heading = screen.getByRole('alert');
      expect(heading).toBeInTheDocument();
    });

    it('should be keyboard navigable', () => {
      render(<SuccessScreen {...mockProps} />);

      const downloadButton = screen.getByRole('button', { name: /download.*markdown/i });
      const resetButton = screen.getByRole('button', { name: /process another document/i });

      // Both buttons should be in the tab order
      expect(downloadButton).not.toHaveAttribute('tabindex', '-1');
      expect(resetButton).not.toHaveAttribute('tabindex', '-1');
    });

    it('should announce error state to screen readers', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: 'Download failed' }),
      });

      render(<SuccessScreen {...mockProps} />);

      const downloadButton = screen.getByRole('button', { name: /download.*markdown/i });
      fireEvent.click(downloadButton);

      await waitFor(() => {
        const errorAlert = screen.getByRole('alert');
        expect(errorAlert).toHaveAttribute('aria-live', 'assertive');
      });
    });
  });

  describe('Filename Handling', () => {
    it('should convert .pdf extension to .md', () => {
      render(<SuccessScreen {...mockProps} filename="document.pdf" />);

      expect(screen.getByText(/document\.md/i)).toBeInTheDocument();
    });

    it('should convert .docx extension to .md', () => {
      render(<SuccessScreen {...mockProps} filename="report.docx" />);

      expect(screen.getByText(/report\.md/i)).toBeInTheDocument();
    });

    it('should convert .pptx extension to .md', () => {
      render(<SuccessScreen {...mockProps} filename="presentation.pptx" />);

      expect(screen.getByText(/presentation\.md/i)).toBeInTheDocument();
    });

    it('should convert .xlsx extension to .md', () => {
      render(<SuccessScreen {...mockProps} filename="spreadsheet.xlsx" />);

      expect(screen.getByText(/spreadsheet\.md/i)).toBeInTheDocument();
    });

    it('should preserve filename without extension changes', () => {
      render(<SuccessScreen {...mockProps} filename="My_Report_2024.pdf" />);

      expect(screen.getByText(/My_Report_2024\.md/i)).toBeInTheDocument();
    });
  });

  describe('File Size Display', () => {
    it('should format bytes correctly', () => {
      render(<SuccessScreen {...mockProps} fileSize={500} />);

      expect(screen.getByText(/500 B/)).toBeInTheDocument();
    });

    it('should format kilobytes correctly', () => {
      render(<SuccessScreen {...mockProps} fileSize={45000} />);

      expect(screen.getByText(/43\.9 KB|44\.0 KB/)).toBeInTheDocument();
    });

    it('should format megabytes correctly', () => {
      render(<SuccessScreen {...mockProps} fileSize={2500000} />);

      expect(screen.getByText(/2\.4 MB/)).toBeInTheDocument();
    });

    it('should handle zero fileSize', () => {
      render(<SuccessScreen {...mockProps} fileSize={0} />);

      expect(screen.queryByText(/KB|MB|B/)).not.toBeInTheDocument();
    });
  });
});
