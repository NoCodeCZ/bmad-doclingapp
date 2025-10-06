'use client';

import { useState } from 'react';

interface Issue {
  problem: string;
  solution: string;
  severity: 'critical' | 'warning' | 'info';
}

const issues: Issue[] = [
  {
    problem: 'Markdown file not appearing in Open WebUI RAG',
    solution: 'Verify the file has a .md extension and is under 10MB. Ensure you\'re uploading to the Documents/Knowledge Base section, not the chat interface. Check that you\'re in the correct workspace. Try refreshing the page after upload.',
    severity: 'critical',
  },
  {
    problem: 'AI responses are still inaccurate after uploading document',
    solution: 'Confirm the document was uploaded to the correct workspace. Verify the markdown content is readable by opening it in a text editor. Try re-processing the document with Quality mode enabled. Make sure OCR was enabled if the source was a scanned PDF.',
    severity: 'warning',
  },
  {
    problem: 'Downloaded file won\'t open or shows strange characters',
    solution: 'The markdown file is plain text and should open in any text editor (Notepad, TextEdit, VS Code). If you see strange characters, try opening with a different editor. Ensure the file wasn\'t corrupted during download - try downloading again.',
    severity: 'info',
  },
  {
    problem: 'Processing takes longer than expected',
    solution: 'Quality mode can take up to 2 minutes for complex documents. Large files (50+ pages) will take longer. If processing exceeds 5 minutes, refresh the page and try again. Consider breaking very large documents into smaller sections.',
    severity: 'info',
  },
  {
    problem: 'Upload fails with "Backend service not available" error',
    solution: 'The backend server may not be running. Contact the workshop facilitator or check the backend service status. If you\'re running locally, ensure the backend server is started on port 8000.',
    severity: 'critical',
  },
  {
    problem: 'Tables and charts are not formatted correctly in markdown',
    solution: 'Use Quality mode instead of Fast mode for documents with complex layouts. Quality mode has better table detection and formatting. For charts and images, note that visual content is converted to text descriptions - review the markdown to ensure accuracy.',
    severity: 'warning',
  },
];

const severityConfig = {
  critical: {
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-200',
    icon: '🚨',
    label: 'Critical',
  },
  warning: {
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-200',
    icon: '⚠️',
    label: 'Warning',
  },
  info: {
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    icon: 'ℹ️',
    label: 'Info',
  },
};

export function Troubleshooting() {
  const [expandedIssue, setExpandedIssue] = useState<number | null>(null);

  const toggleIssue = (index: number) => {
    setExpandedIssue(expandedIssue === index ? null : index);
  };

  return (
    <section aria-labelledby="troubleshooting-heading" className="bg-muted/50 rounded-lg p-6 md:p-8">
      <h2 id="troubleshooting-heading" className="text-2xl font-bold mb-6">
        Troubleshooting Common Issues
      </h2>
      <div className="space-y-3">
        {issues.map((issue, index) => {
          const config = severityConfig[issue.severity];
          return (
            <div
              key={index}
              className={`bg-background border ${config.borderColor} rounded-lg overflow-hidden`}
            >
              <button
                onClick={() => toggleIssue(index)}
                className="w-full text-left p-4 hover:bg-muted/50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-inset"
                aria-expanded={expandedIssue === index}
                aria-controls={`issue-solution-${index}`}
              >
                <div className="flex items-start gap-3">
                  <span className="text-xl flex-shrink-0" aria-hidden="true">
                    {config.icon}
                  </span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`text-xs font-medium ${config.color} uppercase tracking-wide`}>
                        {config.label}
                      </span>
                    </div>
                    <h3 className="font-semibold text-base md:text-lg">{issue.problem}</h3>
                  </div>
                  <span
                    className="text-muted-foreground transition-transform"
                    style={{
                      transform: expandedIssue === index ? 'rotate(180deg)' : 'rotate(0deg)',
                    }}
                    aria-hidden="true"
                  >
                    ▼
                  </span>
                </div>
              </button>
              {expandedIssue === index && (
                <div
                  id={`issue-solution-${index}`}
                  className={`px-4 pb-4 pt-0 ${config.bgColor}`}
                  role="region"
                  aria-label={`Solution for ${issue.problem}`}
                >
                  <div className="pl-11 text-sm leading-relaxed border-t border-border pt-3">
                    <strong className="block mb-2">Solution:</strong>
                    {issue.solution}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Additional Help */}
      <div className="mt-6 p-4 bg-background border border-border rounded-lg">
        <p className="text-sm text-muted-foreground">
          <strong className="text-foreground">Still having issues?</strong> Contact the workshop facilitator or check the{' '}
          <a href="/" className="text-primary hover:underline">
            main upload page
          </a>{' '}
          for system status updates.
        </p>
      </div>
    </section>
  );
}
