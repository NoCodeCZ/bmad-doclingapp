'use client';

import Link from 'next/link';
import { Step } from '@/components/instructions/Step';
import { Tips } from '@/components/instructions/Tips';
import { Troubleshooting } from '@/components/instructions/Troubleshooting';

export default function InstructionsPage() {
  return (
    <main role="main" className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b sticky top-0 bg-background z-10">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 id="instructions-title" className="text-3xl font-bold">
                How to Use Processed Documents in Open WebUI
              </h1>
              <p className="text-muted-foreground mt-1">
                Complete step-by-step guide for workshop attendees
              </p>
            </div>
            <Link
              href="/"
              className="text-primary hover:underline text-sm font-medium"
            >
              ← Back to Upload
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-12">
          {/* Introduction */}
          <section className="prose prose-sm max-w-none">
            <p className="text-lg text-muted-foreground">
              This guide will walk you through the complete workflow from processing your document
              to using it in Open WebUI&apos;s RAG (Retrieval Augmented Generation) system.
            </p>
          </section>

          {/* Step-by-Step Instructions */}
          <section aria-labelledby="steps-heading">
            <h2 id="steps-heading" className="text-2xl font-bold mb-6">
              Step-by-Step Instructions
            </h2>
            <ol className="space-y-8">
              <Step
                number={1}
                title="Process Your Document"
                description="Upload your PDF, DOCX, PPTX, or XLSX file using this tool. Choose the processing mode (Fast for simple documents, Quality for complex ones) and enable OCR if needed for scanned documents."
                imagePath="/images/instructions/step1-upload.png"
                imageAlt="Screenshot showing the document upload interface with processing options"
              />
              <Step
                number={2}
                title="Download the Markdown File"
                description="Once processing is complete, click the 'Download Markdown' button. The file will be saved to your Downloads folder with a .md extension."
                imagePath="/images/instructions/step2-download.png"
                imageAlt="Screenshot showing the download button after successful processing"
              />
              <Step
                number={3}
                title="Open Open WebUI"
                description="Navigate to Open WebUI in your browser. Make sure you're logged in and in the correct workspace for your project."
                imagePath="/images/instructions/step3-openwebui.png"
                imageAlt="Screenshot of Open WebUI main interface"
              />
              <Step
                number={4}
                title="Navigate to Documents Section"
                description="Click on the workspace menu, then select 'Documents' or 'Knowledge Base' from the navigation. This is where you manage RAG documents."
                imagePath="/images/instructions/step4-navigation.png"
                imageAlt="Screenshot showing Open WebUI navigation to Documents/RAG section"
              />
              <Step
                number={5}
                title="Upload Your Markdown File"
                description="Click the 'Upload' or '+' button in the Documents section. Select the markdown file you downloaded in Step 2. Wait for the upload confirmation."
                imagePath="/images/instructions/step5-upload-rag.png"
                imageAlt="Screenshot showing the file upload dialog in Open WebUI Documents section"
              />
              <Step
                number={6}
                title="Verify Document in Knowledge Base"
                description="Check that your document appears in the knowledge base list. You should see the filename and file size. The document is now ready to use for AI-powered queries."
                imagePath="/images/instructions/step6-verify.png"
                imageAlt="Screenshot showing uploaded document appearing in the knowledge base"
              />
            </ol>
          </section>

          {/* Tips Section */}
          <Tips />

          {/* Troubleshooting Section */}
          <Troubleshooting />

          {/* Back to Upload Link */}
          <div className="text-center pt-8">
            <Link
              href="/"
              className="inline-flex items-center px-6 py-3 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
            >
              ← Back to Upload
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t mt-16">
        <div className="container mx-auto px-4 py-6">
          <p className="text-center text-sm text-muted-foreground">
            Built for the October 17, 2025 Workshop • Internal Use Only
          </p>
        </div>
      </footer>
    </main>
  );
}
