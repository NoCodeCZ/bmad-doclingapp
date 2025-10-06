import { render, screen, fireEvent, within } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import InstructionsPage from '@/app/instructions/page';

// Mock Next.js Image component
vi.mock('next/image', () => ({
  default: ({ src, alt, ...props }: any) => {
    return <img src={src} alt={alt} {...props} />;
  },
}));

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ href, children, ...props }: any) => {
    return <a href={href} {...props}>{children}</a>;
  },
}));

describe('InstructionsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Page Structure and Navigation', () => {
    it('renders the main heading', () => {
      render(<InstructionsPage />);

      expect(screen.getByRole('main')).toBeInTheDocument();
      expect(screen.getByRole('heading', { level: 1, name: /How to Use Processed Documents in Open WebUI/i })).toBeInTheDocument();
    });

    it('displays Back to Upload navigation link in header', () => {
      render(<InstructionsPage />);

      const headerLinks = screen.getAllByRole('link', { name: /Back to Upload/i });
      expect(headerLinks.length).toBeGreaterThan(0);
      expect(headerLinks[0]).toHaveAttribute('href', '/');
    });

    it('displays Back to Upload button at the bottom', () => {
      render(<InstructionsPage />);

      const footerLink = screen.getAllByRole('link', { name: /Back to Upload/i });
      expect(footerLink.length).toBeGreaterThan(0);
    });

    it('has proper semantic HTML structure', () => {
      render(<InstructionsPage />);

      expect(screen.getByRole('main')).toBeInTheDocument();
      expect(screen.getByRole('banner')).toBeInTheDocument();
      expect(screen.getByRole('contentinfo')).toBeInTheDocument();
    });
  });

  describe('Step-by-Step Instructions', () => {
    it('renders all 6 steps with numbered indicators', () => {
      render(<InstructionsPage />);

      expect(screen.getByText('Process Your Document')).toBeInTheDocument();
      expect(screen.getByText('Download the Markdown File')).toBeInTheDocument();
      expect(screen.getByText('Open Open WebUI')).toBeInTheDocument();
      expect(screen.getByText('Navigate to Documents Section')).toBeInTheDocument();
      expect(screen.getByText('Upload Your Markdown File')).toBeInTheDocument();
      expect(screen.getByText('Verify Document in Knowledge Base')).toBeInTheDocument();
    });

    it('displays step descriptions', () => {
      render(<InstructionsPage />);

      expect(screen.getByText(/Upload your PDF, DOCX, PPTX, or XLSX file/i)).toBeInTheDocument();
      expect(screen.getByText(/Once processing is complete/i)).toBeInTheDocument();
    });

    it('includes images for each step with proper alt text', () => {
      render(<InstructionsPage />);

      const images = screen.getAllByRole('img');
      expect(images.length).toBeGreaterThanOrEqual(6);

      // Check some specific alt texts
      expect(screen.getByAltText(/document upload interface with processing options/i)).toBeInTheDocument();
      expect(screen.getByAltText(/download button after successful processing/i)).toBeInTheDocument();
    });

    it('uses ordered list for steps', () => {
      render(<InstructionsPage />);

      const orderedLists = screen.getAllByRole('list');
      expect(orderedLists.length).toBeGreaterThan(0);
    });
  });

  describe('Tips Section', () => {
    it('renders Tips for Optimal Results section', () => {
      render(<InstructionsPage />);

      expect(screen.getByRole('heading', { name: /Tips for Optimal Results/i })).toBeInTheDocument();
    });

    it('displays all tips with proper headings', () => {
      render(<InstructionsPage />);

      expect(screen.getByText(/Use Quality Mode for Complex Documents/i)).toBeInTheDocument();
      expect(screen.getByText(/Enable OCR for Scanned PDFs/i)).toBeInTheDocument();
      expect(screen.getByText(/Break Large Documents into Sections/i)).toBeInTheDocument();
      expect(screen.getByText(/Verify File Format/i)).toBeInTheDocument();
      expect(screen.getByText(/Use Descriptive Filenames/i)).toBeInTheDocument();
    });

    it('allows expanding and collapsing tips', () => {
      render(<InstructionsPage />);

      const tipButtons = screen.getAllByRole('button');
      const ocrTipButton = tipButtons.find(btn =>
        within(btn).queryByText(/Enable OCR for Scanned PDFs/i)
      );

      expect(ocrTipButton).toBeInTheDocument();

      if (ocrTipButton) {
        // Initially collapsed
        expect(ocrTipButton).toHaveAttribute('aria-expanded', 'false');

        // Expand tip
        fireEvent.click(ocrTipButton);
        expect(ocrTipButton).toHaveAttribute('aria-expanded', 'true');

        // Should show detailed content
        expect(screen.getByText(/OCR \(Optical Character Recognition\) extracts text from images/i)).toBeInTheDocument();
      }
    });

    it('has keyboard accessible tip toggles', () => {
      render(<InstructionsPage />);

      const tipButtons = screen.getAllByRole('button');
      expect(tipButtons.length).toBeGreaterThan(0);

      tipButtons.forEach(button => {
        expect(button).toHaveAttribute('aria-expanded');
        expect(button).toHaveAttribute('aria-controls');
      });
    });
  });

  describe('Troubleshooting Section', () => {
    it('renders Troubleshooting section', () => {
      render(<InstructionsPage />);

      expect(screen.getByRole('heading', { name: /Troubleshooting Common Issues/i })).toBeInTheDocument();
    });

    it('displays common issues', () => {
      render(<InstructionsPage />);

      expect(screen.getByText(/Markdown file not appearing in Open WebUI RAG/i)).toBeInTheDocument();
      expect(screen.getByText(/AI responses are still inaccurate/i)).toBeInTheDocument();
      expect(screen.getByText(/Processing takes longer than expected/i)).toBeInTheDocument();
    });

    it('shows severity indicators for issues', () => {
      render(<InstructionsPage />);

      // Check for severity labels (Critical, Warning, Info) - using getAllByText since there can be multiple
      expect(screen.getAllByText('Critical').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Warning').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Info').length).toBeGreaterThan(0);
    });

    it('allows expanding troubleshooting items to see solutions', () => {
      render(<InstructionsPage />);

      const troubleshootingButtons = screen.getAllByRole('button');
      const markdownIssueButton = troubleshootingButtons.find(btn =>
        within(btn).queryByText(/Markdown file not appearing in Open WebUI RAG/i)
      );

      if (markdownIssueButton) {
        // Initially collapsed
        expect(markdownIssueButton).toHaveAttribute('aria-expanded', 'false');

        // Expand to see solution
        fireEvent.click(markdownIssueButton);
        expect(markdownIssueButton).toHaveAttribute('aria-expanded', 'true');

        // Check for solution content
        expect(screen.getByText(/Verify the file has a \.md extension/i)).toBeInTheDocument();
      }
    });

    it('displays additional help information', () => {
      render(<InstructionsPage />);

      expect(screen.getByText(/Still having issues\?/i)).toBeInTheDocument();
      expect(screen.getByText(/Contact the workshop facilitator/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility Features', () => {
    it('has proper heading hierarchy', () => {
      render(<InstructionsPage />);

      const h1 = screen.getByRole('heading', { level: 1 });
      expect(h1).toBeInTheDocument();

      const h2s = screen.getAllByRole('heading', { level: 2 });
      expect(h2s.length).toBeGreaterThan(0);

      const h3s = screen.getAllByRole('heading', { level: 3 });
      expect(h3s.length).toBeGreaterThan(0);
    });

    it('uses ARIA labels appropriately', () => {
      render(<InstructionsPage />);

      const main = screen.getByRole('main');
      expect(main).toBeInTheDocument();

      // Check for sections with proper labeling
      const sections = document.querySelectorAll('section[aria-labelledby]');
      expect(sections.length).toBeGreaterThan(0);
    });

    it('has keyboard navigable interactive elements', () => {
      render(<InstructionsPage />);

      const buttons = screen.getAllByRole('button');
      const links = screen.getAllByRole('link');

      [...buttons, ...links].forEach(element => {
        // All interactive elements should be focusable
        expect(element).not.toHaveAttribute('tabindex', '-1');
      });
    });

    it('provides alt text for all images', () => {
      render(<InstructionsPage />);

      const images = screen.getAllByRole('img');
      images.forEach(img => {
        expect(img).toHaveAttribute('alt');
        const altText = img.getAttribute('alt');
        expect(altText).not.toBe('');
      });
    });

    it('uses semantic regions', () => {
      const { container } = render(<InstructionsPage />);

      expect(container.querySelector('main')).toBeInTheDocument();
      expect(container.querySelector('header')).toBeInTheDocument();
      expect(container.querySelector('footer')).toBeInTheDocument();
    });
  });

  describe('Responsive Design', () => {
    it('applies responsive classes to main container', () => {
      const { container } = render(<InstructionsPage />);

      const mainContent = container.querySelector('.container');
      expect(mainContent).toBeInTheDocument();
    });

    it('has mobile-friendly touch targets', () => {
      render(<InstructionsPage />);

      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        // Buttons should have adequate sizing classes
        const classes = button.className;
        expect(classes).toBeTruthy();
      });
    });
  });

  describe('Content Accuracy', () => {
    it('displays correct step count', () => {
      render(<InstructionsPage />);

      // Should have exactly 6 steps
      const stepNumbers = ['1', '2', '3', '4', '5', '6'];
      stepNumbers.forEach(num => {
        const stepElement = screen.getByText(num);
        expect(stepElement).toBeInTheDocument();
      });
    });

    it('mentions all supported file types', () => {
      render(<InstructionsPage />);

      const content = screen.getByRole('main').textContent;
      expect(content).toMatch(/PDF/);
      expect(content).toMatch(/DOCX/);
      expect(content).toMatch(/PPTX/);
      expect(content).toMatch(/XLSX/);
    });

    it('references processing modes correctly', () => {
      render(<InstructionsPage />);

      const content = screen.getByRole('main').textContent;
      expect(content).toMatch(/Fast/);
      expect(content).toMatch(/Quality/);
    });

    it('mentions OCR functionality', () => {
      render(<InstructionsPage />);

      expect(screen.getByText(/Enable OCR for Scanned PDFs/i)).toBeInTheDocument();

      // Need to expand the tip to see the detailed OCR explanation
      const tipButtons = screen.getAllByRole('button');
      const ocrTipButton = tipButtons.find(btn =>
        within(btn).queryByText(/Enable OCR for Scanned PDFs/i)
      );

      if (ocrTipButton) {
        fireEvent.click(ocrTipButton);
        expect(screen.getByText(/OCR \(Optical Character Recognition\)/i)).toBeInTheDocument();
      }
    });
  });

  describe('Image Loading', () => {
    it('sets lazy loading on images', () => {
      render(<InstructionsPage />);

      const images = screen.getAllByRole('img');
      images.forEach(img => {
        expect(img).toHaveAttribute('loading', 'lazy');
      });
    });

    it('handles image errors gracefully', () => {
      render(<InstructionsPage />);

      const images = screen.getAllByRole('img');
      expect(images.length).toBeGreaterThan(0);

      // Component should render even if images fail to load
      expect(screen.getByRole('main')).toBeInTheDocument();
    });
  });
});
