# Requirements

## Functional Requirements

**FR1:** The system shall accept file uploads via drag-and-drop or click-to-browse interface supporting PDF, DOCX, PPTX, and XLSX file types with maximum file size of 10MB.

**FR2:** The system shall validate uploaded files client-side for supported formats and size limits before transmission, providing immediate visual feedback.

**FR3:** The system shall process uploaded documents using the Docling library to convert them into AI-optimized markdown format.

**FR4:** The system shall provide user-selectable processing options including OCR toggle (on/off) and processing mode selection (Fast/Quality).

**FR5:** The system shall display real-time processing status updates showing states: queued, processing, complete, or failed with progress indication.

**FR6:** The system shall enable one-click download of processed markdown files preserving the original filename with .md extension.

**FR7:** The system shall store uploaded files and processed markdown files in Supabase Storage with metadata tracking in PostgreSQL (filename, status, timestamps, processing options).

**FR8:** The system shall display clear, actionable error messages for common failures including unsupported format, file too large, processing timeout, and corrupted file scenarios.

**FR9:** The system shall provide an instructions page explaining how to upload processed markdown files to Open WebUI's RAG feature.

**FR10:** The system shall function on mobile devices (phones/tablets) with responsive UI adapting to different screen sizes.

## Non-Functional Requirements

**NFR1:** The system shall handle 30 concurrent users during workshop sessions without crashes or significant performance degradation.

**NFR2:** The system shall process clean PDF documents in under 30 seconds and OCR-enabled documents in under 2 minutes at the 95th percentile.

**NFR3:** The system shall achieve a 95% or higher successful conversion rate for common document types (clean PDFs, standard DOCX/PPTX/XLSX files).

**NFR4:** The system shall be deployed and production-ready by October 16, 2025, maintaining operational stability through the October 17, 2025 workshop.

**NFR5:** The system shall operate within $10-12/month infrastructure costs using DigitalOcean App Platform with auto-scaling capabilities.

**NFR6:** The system shall store all files in private Supabase storage buckets accessible only to the application backend, with no authentication required for MVP (internal workshop use).

**NFR7:** The system shall provide 100% error coverage with actionable error messages enabling users to self-correct issues without assistance.

**NFR8:** The system shall support modern browsers (Chrome, Firefox, Safari, Edge - last 2 versions) on both desktop and mobile platforms.