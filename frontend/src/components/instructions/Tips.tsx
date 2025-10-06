'use client';

import { useState } from 'react';

interface Tip {
  icon: string;
  title: string;
  description: string;
  details?: string;
}

const tips: Tip[] = [
  {
    icon: '⚡',
    title: 'Use Quality Mode for Complex Documents',
    description: 'For documents with tables, charts, or complex formatting, select Quality mode during processing.',
    details: 'Quality mode uses advanced AI models that better preserve document structure, table layouts, and formatting nuances. While it takes longer (up to 2 minutes), the result is more accurate markdown that works better with RAG systems.',
  },
  {
    icon: '🔍',
    title: 'Enable OCR for Scanned PDFs',
    description: 'If your PDF is a scanned image or contains image-based text, enable the OCR option.',
    details: 'OCR (Optical Character Recognition) extracts text from images within PDFs. This is essential for scanned documents, photos of documents, or PDFs created from images. Without OCR, these documents will appear empty in the markdown output.',
  },
  {
    icon: '📄',
    title: 'Break Large Documents into Sections',
    description: 'For very large documents (100+ pages), consider splitting them into logical sections before processing.',
    details: 'Large documents can be slower to process and harder for AI systems to work with effectively. Breaking them into chapters, sections, or topics improves processing speed and RAG accuracy. Each section can be uploaded as a separate document in Open WebUI.',
  },
  {
    icon: '✅',
    title: 'Verify File Format',
    description: 'Ensure your downloaded markdown file has a .md extension before uploading to Open WebUI.',
    details: 'Open WebUI\'s RAG system expects markdown files with .md extensions. If your browser changed the extension during download, rename the file to add .md at the end. The file should be plain text format.',
  },
  {
    icon: '🎯',
    title: 'Use Descriptive Filenames',
    description: 'Rename your files with clear, descriptive names before processing to make them easier to find in Open WebUI.',
    details: 'Good filenames help you identify documents in the knowledge base. Use names like "Q4-Sales-Report-2024.md" instead of "document-1.md". This is especially important when managing multiple documents.',
  },
];

export function Tips() {
  const [expandedTip, setExpandedTip] = useState<number | null>(null);

  const toggleTip = (index: number) => {
    setExpandedTip(expandedTip === index ? null : index);
  };

  return (
    <section aria-labelledby="tips-heading" className="bg-muted/50 rounded-lg p-6 md:p-8">
      <h2 id="tips-heading" className="text-2xl font-bold mb-6">
        Tips for Optimal Results
      </h2>
      <div className="space-y-4">
        {tips.map((tip, index) => (
          <div
            key={index}
            className="bg-background border border-border rounded-lg overflow-hidden"
          >
            <button
              onClick={() => toggleTip(index)}
              className="w-full text-left p-4 hover:bg-muted/50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-inset"
              aria-expanded={expandedTip === index}
              aria-controls={`tip-details-${index}`}
            >
              <div className="flex items-start gap-3">
                <span className="text-2xl flex-shrink-0" aria-hidden="true">
                  {tip.icon}
                </span>
                <div className="flex-1">
                  <h3 className="font-semibold text-base md:text-lg">{tip.title}</h3>
                  <p className="text-sm text-muted-foreground mt-1">{tip.description}</p>
                </div>
                <span
                  className="text-muted-foreground transition-transform"
                  style={{
                    transform: expandedTip === index ? 'rotate(180deg)' : 'rotate(0deg)',
                  }}
                  aria-hidden="true"
                >
                  ▼
                </span>
              </div>
            </button>
            {expandedTip === index && tip.details && (
              <div
                id={`tip-details-${index}`}
                className="px-4 pb-4 pt-0"
                role="region"
                aria-label={`Details for ${tip.title}`}
              >
                <div className="pl-11 text-sm text-muted-foreground leading-relaxed border-t border-border pt-3">
                  {tip.details}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
