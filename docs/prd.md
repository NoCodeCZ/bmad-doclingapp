# Workshop Document Processor Product Requirements Document (PRD)

## Goals and Background Context

### Goals

- Successfully enable 80%+ of workshop attendees (30 people) to convert and use their own documents in Open WebUI during the October 17, 2025 workshop
- Deliver a production-ready web application that converts office documents (PDF, DOCX, PPTX, XLSX) into AI-optimized markdown format using Docling
- Achieve 95%+ successful conversion rate across all supported file types with processing times under 2 minutes
- Enable drag-and-drop simplicity requiring zero technical knowledge or manual formatting from users
- Deploy to production by October 16, 2025 (13-day development sprint with 1-day buffer)
- Dramatically improve RAG performance in Open WebUI by providing clean, well-structured markdown that enhances AI comprehension and retrieval quality

### Background Context

Employees need to leverage their own documents with Open WebUI's RAG (Retrieval-Augmented Generation) capabilities, but raw office files suffer from critical extraction problems that severely degrade AI performance. PDF files produce fragmented text with poor structure preservation, complex layouts confuse standard parsers, and scanned documents remain unreadable without OCR. This results in RAG systems retrieving irrelevant chunks and AI responses lacking accuracy, forcing users to waste time on manual reformatting or abandoning the effort entirely.

The Workshop Document Processor solves this by leveraging Docling—an open-source document parser specifically optimized for AI consumption—to transform complex office documents into clean, semantically-rich markdown that maximizes RAG retrieval accuracy. Built for an internal workshop with 30 attendees on October 17, 2025, this tool provides a simple web interface (drag-and-drop upload → automatic processing → download markdown) with zero manual work required, filling the critical gap between "raw documents" and "RAG-ready content" that no existing solution addresses.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-04 | 1.0 | Initial PRD creation from Project Brief | PM Agent |

---

## Requirements

### Functional Requirements

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

### Non-Functional Requirements

**NFR1:** The system shall handle 30 concurrent users during workshop sessions without crashes or significant performance degradation.

**NFR2:** The system shall process clean PDF documents in under 30 seconds and OCR-enabled documents in under 2 minutes at the 95th percentile.

**NFR3:** The system shall achieve a 95% or higher successful conversion rate for common document types (clean PDFs, standard DOCX/PPTX/XLSX files).

**NFR4:** The system shall be deployed and production-ready by October 16, 2025, maintaining operational stability through the October 17, 2025 workshop.

**NFR5:** The system shall operate within $10-12/month infrastructure costs using DigitalOcean App Platform with auto-scaling capabilities.

**NFR6:** The system shall store all files in private Supabase storage buckets accessible only to the application backend, with no authentication required for MVP (internal workshop use).

**NFR7:** The system shall provide 100% error coverage with actionable error messages enabling users to self-correct issues without assistance.

**NFR8:** The system shall support modern browsers (Chrome, Firefox, Safari, Edge - last 2 versions) on both desktop and mobile platforms.

---

## User Interface Design Goals

### Overall UX Vision

The Workshop Document Processor delivers a frictionless, single-purpose experience optimized for speed and clarity. Users should understand the entire workflow within 3 seconds of landing on the page: upload document → wait for processing → download markdown. Visual feedback dominates the interface—large drop zones, clear progress indicators, and prominent download buttons eliminate confusion. The design prioritizes "invisible complexity": sophisticated Docling processing and Supabase storage operate behind a deceptively simple interface that workshop attendees can use without documentation or assistance.

### Key Interaction Paradigms

- **Drag-and-Drop First:** Primary interaction is dragging files onto a large, visually prominent drop zone; click-to-browse serves as secondary option
- **Status-Driven UI:** Interface morphs based on processing state (idle → uploading → processing → complete/error), showing only relevant actions at each stage
- **One Action Per Screen:** Each view focuses on a single user decision (upload file, configure options, download result) avoiding cognitive overload
- **Instant Feedback:** Every user action produces immediate visual response (file validation, upload progress, processing status) to maintain engagement during 1-2 minute processing times
- **Mobile-First Responsiveness:** Touch-friendly targets (minimum 44px), vertical layouts, and simplified mobile flows ensure workshop attendees can use phones/tablets if needed

### Core Screens and Views

- **Upload Screen (Landing Page):** Large drag-and-drop zone, processing options (OCR toggle, Fast/Quality mode selector), file type/size guidance
- **Processing Status Screen:** Real-time progress indicator, estimated time remaining, current processing stage (queued/processing), cancel option
- **Download Screen:** Prominent download button, success confirmation, filename display, "Process Another Document" action
- **Error Screen:** Clear error message, suggested corrective action, "Try Again" button
- **Instructions Page:** Step-by-step guide for uploading markdown to Open WebUI RAG with screenshots

### Accessibility: WCAG AA

WCAG AA compliance ensures workshop attendees with disabilities can use the tool effectively. Focus on keyboard navigation (all actions accessible without mouse), screen reader compatibility (ARIA labels for drag-drop zones and status updates), sufficient color contrast (4.5:1 for text), and error identification (not relying solely on color to indicate validation errors).

### Branding

Minimal, professional styling aligned with internal tools aesthetic. Clean sans-serif typography, neutral color palette (grays, blues) with accent colors for status states (green for success, amber for processing, red for errors). No corporate branding required for MVP—prioritize clarity and functionality over visual polish. Design should feel "enterprise-lite": trustworthy but not bureaucratic.

### Target Device and Platforms: Web Responsive

Primary platform is desktop web browsers (Chrome, Firefox, Safari, Edge - last 2 versions), with full responsive support for tablets and smartphones. Workshop attendees will primarily use laptops, but mobile responsiveness ensures accessibility for users who arrive with only phones/tablets. Progressive enhancement approach: core functionality works on all devices, with enhanced features (drag-and-drop preview, advanced progress visualization) on desktop.

---

## Technical Assumptions

### Repository Structure: Monorepo

Single Git repository with `/frontend` and `/backend` directories. This structure simplifies development coordination, enables shared configuration (TypeScript types, deployment configs), and supports atomic commits spanning both services—critical for a solo developer or small team working under tight timeline. DigitalOcean App Platform natively supports monorepo deployments with multiple services.

### Service Architecture

**Monolith within Monorepo:** Two distinct services deployed as separate containers:
- **Frontend Service:** Next.js 14 application serving React UI with server components, handles file upload initiation and status polling
- **Backend Service:** FastAPI (Python async) application handling Docling document processing, file storage orchestration, and status API endpoints

Communication pattern: Frontend polls backend REST API for processing status (simple, reliable, no WebSocket complexity). Both services connect independently to Supabase (frontend for file upload URLs, backend for storage and database operations).

### Testing Requirements

**Unit + Integration Testing with Manual E2E:**
- **Backend:** Unit tests for Docling integration, API endpoints (pytest, pytest-asyncio); Integration tests for Supabase storage/database operations
- **Frontend:** Unit tests for UI components (Vitest, React Testing Library); Integration tests for API client logic
- **Manual E2E:** Human testing of complete upload→process→download workflow across different file types and browsers (workshop rehearsal serves as final E2E validation)

Rationale: 13-day timeline prohibits comprehensive automated E2E setup. Manual testing with real workshop documents provides highest confidence. Focus automated testing on business logic (Docling processing, API contracts) where bugs are most likely.

### Additional Technical Assumptions and Requests

**Frontend Stack:**
- **Framework:** Next.js 14 (App Router, React Server Components) for modern React patterns and built-in optimization
- **Styling:** TailwindCSS for rapid UI development, shadcn/ui component library for accessible, pre-built components
- **File Upload:** react-dropzone for drag-and-drop functionality with progress tracking
- **State Management:** React hooks + Context API (no Redux/Zustand needed for simple state)

**Backend Stack:**
- **Framework:** FastAPI (Python 3.11+) for async processing, automatic OpenAPI docs, and Pydantic validation
- **Document Processing:** Docling library (latest stable version) with configurable OCR and quality modes
- **Validation:** Pydantic models for request/response validation and type safety

**Database & Storage:**
- **Database:** Supabase PostgreSQL for document metadata (id, filename, status, processing_options, created_at, completed_at, error_message)
- **File Storage:** Supabase Storage with two buckets: `uploads` (original files) and `processed` (markdown outputs), both private with backend-only access
- **Client Libraries:** @supabase/supabase-js (frontend), supabase-py (backend)

**Infrastructure & Deployment:**
- **Hosting:** DigitalOcean App Platform with two services (Next.js frontend, FastAPI backend) and auto-scaling enabled
- **Environment:** Separate staging and production environments (staging for pre-workshop testing)
- **Configuration:** Environment variables for Supabase credentials, Docling options, file size limits
- **Monitoring:** DigitalOcean built-in metrics (no external APM tools for MVP)

**Development & Tooling:**
- **Language Versions:** Node.js 20 LTS (frontend), Python 3.11+ (backend)
- **Package Management:** npm (frontend), pip with requirements.txt (backend)
- **Code Quality:** ESLint + Prettier (frontend), Black + Ruff (backend), pre-commit hooks for formatting
- **Version Control:** Git with conventional commits, feature branch workflow

**Security & Constraints:**
- **File Size Limit:** 10MB maximum (enforced client and server-side) to prevent resource exhaustion
- **Processing Timeout:** 5-minute hard timeout on Docling operations to prevent hanging requests
- **Rate Limiting:** None for MVP (internal use, 30 known users) but log request patterns for post-workshop evaluation
- **Data Retention:** Files stored indefinitely for MVP (add cleanup policy post-workshop if needed)
- **CORS:** Frontend and backend on same DigitalOcean domain (no CORS complexity)

**Docling Configuration:**
- **Processing Modes:** Fast mode (basic extraction, no OCR), Quality mode (full layout analysis + OCR)
- **OCR Engine:** EasyOCR or Tesseract (whatever Docling defaults to, no custom training)
- **Output Format:** Markdown with preserved table structure, heading hierarchy, and image placeholders

---

## Epic List

### Epic 1: Foundation & Core Processing Pipeline
Establish project infrastructure (Next.js frontend, FastAPI backend, Supabase integration, DigitalOcean deployment) while delivering the core document conversion capability—users can upload a file, process it with Docling, and receive markdown output.

### Epic 2: User Experience & Status Management
Enhance the basic pipeline with real-time status updates, processing options (OCR toggle, Fast/Quality modes), error handling with actionable messages, and responsive UI refinements to create the polished workshop-ready experience.

### Epic 3: Production Readiness & Workshop Preparation
Implement mobile responsiveness, create the instructions page for Open WebUI integration, conduct comprehensive testing with diverse document types, perform load testing for 30 concurrent users, and finalize deployment with monitoring for workshop day stability.

---

## Epic 1: Foundation & Core Processing Pipeline

**Epic Goal:** Establish the complete technical foundation and deliver the core document conversion workflow, enabling users to upload documents, process them with Docling, and download markdown output. This epic creates a fully deployable end-to-end system with basic functionality, providing the foundation for all subsequent enhancements.

### Story 1.1: Project Initialization & Repository Setup

As a **developer**,
I want **monorepo project structure with Next.js frontend and FastAPI backend configured**,
so that **the team has a clean foundation for parallel frontend/backend development**.

#### Acceptance Criteria

1. Monorepo created with `/frontend` (Next.js 14 App Router) and `/backend` (FastAPI Python 3.11+) directories
2. Frontend configured with TailwindCSS, shadcn/ui, TypeScript, ESLint, and Prettier
3. Backend configured with FastAPI, Pydantic, pytest, Black, and Ruff formatting
4. Git repository initialized with `.gitignore` for Node and Python, conventional commit setup, and pre-commit hooks for code formatting
5. Both services run locally with health check endpoints (`GET /` returns 200 OK with basic JSON response)
6. README documents local development setup for both frontend and backend services

### Story 1.2: Supabase Integration & Database Schema

As a **developer**,
I want **Supabase PostgreSQL database schema and storage buckets configured**,
so that **the application can persist document metadata and store uploaded/processed files**.

#### Acceptance Criteria

1. Supabase client libraries integrated (supabase-js for frontend, supabase-py for backend) with environment variable configuration
2. Database table `documents` created with fields: `id` (UUID, PK), `filename` (text), `status` (enum: queued/processing/complete/failed), `processing_options` (JSON), `created_at` (timestamp), `completed_at` (timestamp), `error_message` (text, nullable)
3. Two storage buckets created: `uploads` (original files) and `processed` (markdown files), both configured as private with backend-only access
4. Backend service successfully connects to Supabase and can create test records in `documents` table
5. Backend service can upload/download test files to/from both storage buckets with proper error handling
6. Database migration script or schema documentation provided for reproducible setup

### Story 1.3: File Upload UI & Client-Side Validation

As a **workshop attendee**,
I want **drag-and-drop file upload interface with immediate validation feedback**,
so that **I can easily upload my documents and know if they're acceptable before processing**.

#### Acceptance Criteria

1. Upload screen displays large drag-and-drop zone using react-dropzone with visual hover states
2. Click-to-browse fallback option available for users preferring traditional file selection
3. Client-side validation enforces: file type (PDF, DOCX, PPTX, XLSX only), file size (max 10MB) with immediate visual feedback on validation failure
4. Accepted files display filename and file size before upload confirmation
5. Upload button triggers file transmission to backend with visual loading state (spinner/progress indicator)
6. Responsive layout works on mobile devices with touch-friendly drop zone (minimum 44px touch targets)
7. Clear error messages displayed for rejected files: "Unsupported file type - only PDF, DOCX, PPTX, XLSX allowed" or "File too large - maximum 10MB"

### Story 1.4: Backend File Upload & Storage

As a **backend service**,
I want **file upload endpoint that validates and stores documents in Supabase**,
so that **uploaded files are securely stored and tracked for processing**.

#### Acceptance Criteria

1. `POST /api/upload` endpoint accepts multipart/form-data file uploads with server-side validation (file type, size limits)
2. Uploaded file stored in Supabase `uploads` bucket with unique filename (UUID-based to prevent collisions)
3. Document metadata record created in `documents` table with status='queued', original filename, and processing options placeholder
4. Endpoint returns JSON response with document `id`, `filename`, and `status`
5. Server-side validation errors return 400 status with actionable error messages matching client-side validation messages
6. File upload errors (storage failures) return 500 status with error logged and user-friendly message returned
7. Unit tests verify validation logic, integration tests verify Supabase storage operations

### Story 1.5: Docling Processing Pipeline

As a **backend service**,
I want **document processing workflow using Docling to convert files to markdown**,
so that **uploaded documents are transformed into AI-optimized format**.

#### Acceptance Criteria

1. Docling library integrated with basic configuration (Fast mode, no OCR for initial implementation)
2. `POST /api/process/{document_id}` endpoint triggers processing: updates status to 'processing', retrieves file from `uploads` bucket, invokes Docling conversion
3. Docling output (markdown text) stored in Supabase `processed` bucket with matching filename pattern (`{original-name}.md`)
4. On successful processing: status updated to 'complete', `completed_at` timestamp set, processed file path stored in metadata
5. On processing failure: status updated to 'failed', `error_message` populated with Docling error details, original file remains in uploads bucket
6. Processing timeout enforced at 5 minutes, triggering failure status if exceeded
7. Unit tests mock Docling operations, integration tests verify full pipeline with sample PDF file

### Story 1.6: Markdown Download & Basic Frontend Flow

As a **workshop attendee**,
I want **to download processed markdown files after upload completes**,
so that **I can use the converted document in Open WebUI**.

#### Acceptance Criteria

1. Frontend polls `GET /api/status/{document_id}` endpoint every 2 seconds after upload to check processing status
2. `GET /api/status/{document_id}` returns current status, filename, and download URL (if complete) or error message (if failed)
3. UI transitions from "Uploading..." → "Processing..." → "Complete" based on status updates
4. Download button appears when status='complete', triggering `GET /api/download/{document_id}` which streams markdown file from `processed` bucket
5. Downloaded file preserves original filename with `.md` extension (e.g., `report.pdf` → `report.md`)
6. "Process Another Document" button resets UI to upload screen after successful download
7. Error state displays error message from backend with "Try Again" button returning to upload screen

### Story 1.7: DigitalOcean Deployment & CI/CD

As a **developer**,
I want **automated deployment to DigitalOcean App Platform with staging and production environments**,
so that **the application is accessible for testing and ready for workshop use**.

#### Acceptance Criteria

1. DigitalOcean App Platform configured with two services: `frontend` (Next.js) and `backend` (FastAPI) both deploying from monorepo
2. Staging environment deployed with separate Supabase instance/buckets for testing
3. Environment variables configured for both services (Supabase credentials, API URLs, file size limits)
4. Health check endpoints (`/api/health` for backend, `/_health` for frontend) configured in DigitalOcean for monitoring
5. Deployment succeeds for both services with publicly accessible URLs (e.g., `https://frontend.ondigitalocean.app`, `https://backend.ondigitalocean.app`)
6. Basic smoke test passes: upload sample PDF → process → download markdown in staging environment
7. Deployment documentation includes rollback procedure and environment variable management

---

## Epic 2: User Experience & Status Management

**Epic Goal:** Transform the basic processing pipeline into a polished, workshop-ready experience with real-time status visibility, configurable processing options (OCR toggle, Fast/Quality modes), comprehensive error handling with actionable messages, and UI refinements that enable workshop attendees to use the tool independently without assistance.

### Story 2.1: Processing Options UI & Backend Integration

As a **workshop attendee**,
I want **to select OCR and processing mode options before uploading**,
so that **I can optimize processing speed vs. quality based on my document type**.

#### Acceptance Criteria

1. Upload screen displays two toggle controls: "Enable OCR" (checkbox, default off) and "Processing Mode" (radio buttons: Fast/Quality, default Fast)
2. Help text explains each option: OCR ("Enable for scanned documents or images"), Fast mode ("Quick processing, best for clean digital documents"), Quality mode ("Thorough analysis, best for complex layouts")
3. Selected options included in upload request payload (`processing_options` JSON field)
4. Backend `/api/upload` endpoint stores processing options in `documents.processing_options` field
5. Backend `/api/process/{document_id}` retrieves processing options and configures Docling accordingly (OCR on/off, Fast/Quality mode)
6. Docling processing respects configuration: OCR mode uses optical character recognition, Quality mode performs full layout analysis
7. Unit tests verify options are correctly passed through upload → storage → processing pipeline

### Story 2.2: Enhanced Status Display & Progress Indicators

As a **workshop attendee**,
I want **clear visual feedback showing processing progress and estimated time**,
so that **I understand what's happening and how long to wait**.

#### Acceptance Criteria

1. Processing screen displays animated progress indicator (spinner or progress bar) with current status text: "Uploading file...", "Queued for processing...", "Processing document...", "Finalizing..."
2. Status updates polled every 2 seconds from backend with visual state transitions (no jarring UI jumps)
3. Estimated time remaining displayed based on processing mode: Fast mode ("~30 seconds"), Quality mode with OCR ("~2 minutes"), adjusts if processing exceeds estimates
4. Backend `/api/status/{document_id}` returns enriched response: status, progress_stage (uploading/queued/processing/finalizing), elapsed_time, filename
5. Visual differentiation between stages: uploading (blue pulse), processing (amber spinner), complete (green checkmark), failed (red error icon)
6. Processing screen remains responsive on mobile devices with appropriately sized progress indicators
7. Status polling stops automatically when status reaches 'complete' or 'failed' terminal states

### Story 2.3: Comprehensive Error Handling & Actionable Messages

As a **workshop attendee**,
I want **clear error messages that tell me what went wrong and how to fix it**,
so that **I can resolve issues without asking for help**.

#### Acceptance Criteria

1. Error messages displayed in prominent error UI component (red banner or modal) with error icon
2. File validation errors show specific guidance: "File too large (15MB) - maximum size is 10MB. Try compressing your PDF or splitting into multiple files"
3. Unsupported format errors include allowed formats: "Cannot process .txt files - supported formats: PDF, DOCX, PPTX, XLSX"
4. Processing timeout errors (5+ minutes) display: "Processing took too long - try enabling Fast mode or reducing document complexity"
5. Corrupted file errors suggest: "Unable to process file - ensure the document isn't password-protected or corrupted"
6. Backend service errors (Supabase failures, Docling crashes) show user-friendly message: "Processing failed due to server error - please try again" (technical details logged server-side only)
7. All error states include "Try Again" button that resets to upload screen, clearing previous error state
8. Error logging on backend captures full error details (stack trace, document ID, file metadata) for debugging

### Story 2.4: Download Experience & File Management

As a **workshop attendee**,
I want **a streamlined download experience with clear success confirmation**,
so that **I know my markdown file is ready and correctly named**.

#### Acceptance Criteria

1. Success screen displays: green checkmark, "Processing Complete!" heading, original filename with `.md` extension preview
2. Large, prominent "Download Markdown" button triggers download with proper content-disposition header (forces download vs. browser display)
3. Downloaded file uses cleaned filename: preserves original name, replaces `.pdf`/`.docx`/`.pptx`/`.xlsx` with `.md`, removes special characters
4. Success message includes file size of processed markdown (e.g., "report.md (45 KB) ready for download")
5. "Process Another Document" button visible below download button, resets entire UI state to upload screen
6. Backend `/api/download/{document_id}` endpoint streams file from Supabase `processed` bucket with proper MIME type (`text/markdown`)
7. Download errors (file not found, storage access failed) display actionable message: "Download failed - file may have been moved or deleted. Please process document again"

### Story 2.5: Mobile Responsive UI Refinements

As a **workshop attendee using a mobile device**,
I want **the interface to work seamlessly on my phone or tablet**,
so that **I can process documents even if I don't have a laptop**.

#### Acceptance Criteria

1. Upload screen responsive breakpoints: full-width drop zone on mobile (<768px), centered layout on desktop
2. Processing options (OCR toggle, mode selection) stack vertically on mobile with touch-friendly spacing (minimum 44px tap targets)
3. Status screen adapts: progress indicator scaled appropriately, status text readable without horizontal scrolling
4. Download button full-width on mobile, fixed width centered on desktop
5. Error messages wrap properly on narrow screens without text overflow
6. Mobile Safari and Chrome tested: drag-and-drop works (if supported) or gracefully falls back to click-to-browse
7. Responsive typography: base font 16px on mobile (prevents zoom on iOS input focus), scales up to 18px on desktop

### Story 2.6: Integration Testing & Error Scenario Validation

As a **developer**,
I want **comprehensive integration tests covering success and failure paths**,
so that **we have confidence the system handles real-world scenarios reliably**.

#### Acceptance Criteria

1. Integration test suite created covering: successful upload → process → download for each file type (PDF, DOCX, PPTX, XLSX)
2. Processing options validated: Fast mode completes faster than Quality mode, OCR mode handles scanned PDF successfully
3. Error scenarios tested: oversized file rejection (11MB file), unsupported format rejection (.txt file), corrupted file handling (intentionally corrupted PDF)
4. Timeout scenario tested: mock Docling processing exceeding 5 minutes triggers failure status with correct error message
5. Storage failure scenarios: Supabase connection error handled gracefully with user-friendly error message
6. End-to-end test on staging environment: upload real workshop sample documents (complex PDF with tables, multi-slide PPTX, large Excel spreadsheet)
7. Test results documented: success rate, processing times (p50, p95), identified edge cases requiring handling in Epic 3

---

## Epic 3: Production Readiness & Workshop Preparation

**Epic Goal:** Finalize production deployment with comprehensive testing across diverse document types, validate system performance under workshop load conditions (30 concurrent users), create supporting documentation for Open WebUI integration, and ensure monitoring/stability for workshop day success.

### Story 3.1: Instructions Page for Open WebUI Integration

As a **workshop attendee**,
I want **clear step-by-step instructions for using processed markdown in Open WebUI**,
so that **I can successfully complete the end-to-end workflow from document upload to RAG usage**.

#### Acceptance Criteria

1. Instructions page accessible from main navigation (link visible on upload screen and success screen)
2. Step-by-step guide with numbered instructions: (1) Process document using this tool, (2) Download markdown file, (3) Open Open WebUI, (4) Navigate to RAG/Documents section, (5) Upload markdown file, (6) Verify document appears in knowledge base
3. Screenshots or annotated images showing Open WebUI interface for each step (RAG navigation, upload button, confirmation screen)
4. Troubleshooting section addresses common issues: "Markdown not appearing in RAG" → check file format, "AI responses still inaccurate" → verify document uploaded to correct workspace
5. Tips for optimal results: "Use Quality mode for complex documents", "Enable OCR for scanned PDFs", "Break very large documents into sections"
6. Responsive layout: instructions readable on mobile devices, images scale appropriately without horizontal scrolling
7. "Back to Upload" navigation link returns users to main application flow

### Story 3.2: Diverse Document Type Testing & Edge Case Handling

As a **QA engineer**,
I want **the system validated against diverse real-world documents and edge cases**,
so that **workshop attendees experience high success rates regardless of document complexity**.

#### Acceptance Criteria

1. Test suite includes diverse document types: clean digital PDF, scanned PDF (low and high quality), DOCX with tables/images, PPTX with complex layouts, XLSX with multiple sheets and formulas
2. Edge cases tested: password-protected files (should fail with clear message), corrupted files, files at size limits (9.9MB, 10.1MB), files with special characters in filenames, non-English language documents
3. Docling output quality validated: tables preserved in markdown format, heading hierarchy maintained, image placeholders inserted correctly, multi-column layouts handled gracefully
4. Processing time benchmarks documented per file type: PDF (p50, p95), DOCX (p50, p95), PPTX (p50, p95), XLSX (p50, p95)
5. Known limitations documented: file types that consistently fail, document features that don't convert well (embedded videos, complex charts), acceptable quality degradation scenarios
6. Bug fixes implemented for critical failures discovered during testing
7. Test report includes: success rate by file type, processing time distribution, error rate breakdown, recommendations for workshop messaging (set expectations on limitations)

### Story 3.3: Load Testing & Performance Optimization

As a **workshop facilitator**,
I want **the system validated for 30 concurrent users with acceptable performance**,
so that **all attendees can use the tool simultaneously without failures or slowdowns**.

#### Acceptance Criteria

1. Load test executed simulating 30 concurrent users each uploading and processing documents (mix of file types, processing options)
2. System handles 30 concurrent uploads without crashes, 500 errors, or request timeouts (5-minute processing limit not exceeded)
3. DigitalOcean auto-scaling triggers appropriately: frontend and backend services scale up when load increases, scale down when load decreases
4. Performance metrics captured: response time p95 for upload endpoint, processing completion time p95, concurrent processing capacity (how many Docling processes run simultaneously)
5. Database query performance validated: status polling by 30 users doesn't degrade response times, connection pooling configured appropriately
6. Storage bandwidth sufficient: 30 simultaneous downloads don't exceed Supabase limits or cause throttling
7. Optimization implemented if performance issues found: increase worker processes, optimize database queries, adjust auto-scaling thresholds, implement request queuing if needed
8. Load test report documents: max concurrent capacity, performance at 30 users vs. baseline, identified bottlenecks and mitigations

### Story 3.4: Production Deployment & Monitoring Setup

As a **DevOps engineer**,
I want **production environment deployed with monitoring and alerting configured**,
so that **we can detect and respond to issues during the workshop**.

#### Acceptance Criteria

1. Production environment deployed to DigitalOcean with separate Supabase production instance (isolated from staging)
2. Environment variables configured for production: Supabase production credentials, CORS settings (if frontend/backend on different subdomains), file size limits, processing timeouts
3. DigitalOcean monitoring dashboards configured tracking: CPU/memory usage per service, request rate, error rate (4xx, 5xx), response time p95
4. Log aggregation enabled: application logs from frontend and backend centralized in DigitalOcean logs with retention policy (7 days minimum)
5. Health check alerts configured: notify if health endpoints fail 3 consecutive times, alert if error rate exceeds 10% over 5-minute window
6. Backup strategy documented: database backup schedule (daily), storage bucket backup (manual pre-workshop snapshot), rollback procedure
7. Production smoke test passes: upload → process → download workflow for each file type succeeds in production environment

### Story 3.5: Workshop Rehearsal & Final Validation

As a **workshop facilitator**,
I want **a full rehearsal of workshop scenarios with real users**,
so that **we identify any remaining issues before October 17**.

#### Acceptance Criteria

1. Rehearsal session conducted with 5-10 internal testers simulating workshop conditions: each tester uploads their own real documents, uses mobile and desktop devices
2. Testers follow complete workflow: access production URL → upload document → configure options → wait for processing → download markdown → upload to Open WebUI
3. Observed pain points documented: confusing UI elements, unclear error messages, unexpected failures, accessibility issues (keyboard navigation, screen reader compatibility)
4. Success metrics measured: task completion rate (% who successfully download markdown), time to completion, error rate, user satisfaction score (1-5 scale)
5. Critical issues fixed immediately: blocking errors, major UX confusion, accessibility failures preventing task completion
6. Nice-to-have improvements deferred: minor polish, edge case handling, features beyond MVP scope
7. Workshop day runbook created: troubleshooting guide for facilitators, escalation path for technical issues, contact information for on-call developer, known limitations to communicate to attendees

### Story 3.6: Documentation & Handoff Materials

As a **workshop facilitator and future maintainer**,
I want **comprehensive documentation covering operation, troubleshooting, and future enhancements**,
so that **the tool can be supported beyond the initial workshop**.

#### Acceptance Criteria

1. User documentation finalized: Instructions page (Story 3.1) reviewed for clarity, FAQ section added covering common questions (processing time expectations, file type support, Open WebUI integration)
2. Operational runbook created: how to access DigitalOcean dashboards, how to check logs for errors, how to manually restart services, how to scale resources if needed
3. Troubleshooting guide for facilitators: common error messages and resolutions, how to verify Supabase connectivity, how to check Docling processing logs, emergency contact procedures
4. Technical documentation updated: architecture diagram (frontend ↔ backend ↔ Supabase flow), API endpoint documentation, environment variable reference, deployment procedures
5. Post-workshop enhancement backlog documented: features mentioned in brief as "out of scope" (batch upload, processing history, user auth), performance optimizations identified during testing
6. Maintenance plan outlined: who owns the tool post-workshop, how to handle user requests, process for deploying updates, data retention/cleanup policy
7. Handoff meeting scheduled with workshop facilitators and future maintainers covering all documentation

---

## Checklist Results Report

### Executive Summary

**Overall PRD Completeness:** 92%
**MVP Scope Appropriateness:** Just Right
**Readiness for Architecture Phase:** Ready

### Final Decision

**✅ READY FOR ARCHITECT**

The PRD and epics are comprehensive, properly structured, and ready for architectural design. All critical criteria met with only minor non-blocking gaps (data retention policy formalization can be addressed in Story 3.6).

---

## Next Steps

### UX Expert Prompt

**Note:** UX Expert work is optional for this project given the tight 13-day timeline and simple UI requirements. If you choose to engage the UX Expert, use this prompt:

```
/BMad:ux *create

I need a front-end specification for the Workshop Document Processor based on the PRD at docs/prd.md and Project Brief at docs/brief.md.

Focus areas:
1. Detailed UI component specifications for the 5 core screens (Upload, Processing Status, Download, Error, Instructions)
2. Responsive layout specifications (mobile breakpoints, touch targets, typography scales)
3. Component library usage guide (shadcn/ui components mapped to screens)
4. Interaction patterns for drag-and-drop, status polling, and error states
5. Accessibility implementation details (WCAG AA compliance checklist, ARIA labels, keyboard navigation)

Keep it lean and actionable - we have 13 days to build this. Prioritize implementation-ready specs over conceptual design exploration.
```

### Architect Prompt

```
/BMad:architect *create

Please create the system architecture document for the Workshop Document Processor based on:
- PRD: docs/prd.md
- Project Brief: docs/brief.md

Key focus areas:
1. **Service Architecture:** Two-service monorepo (Next.js frontend + FastAPI backend) with Supabase integration - detail the communication patterns, API contracts, and deployment structure
2. **Docling Integration:** Document processing pipeline architecture with OCR/Quality mode configuration, timeout handling, and error recovery
3. **Data Architecture:** PostgreSQL schema (documents table), Supabase Storage bucket structure (uploads/processed), file lifecycle management
4. **Infrastructure:** DigitalOcean App Platform deployment (staging + production), auto-scaling configuration for 30 concurrent users, monitoring setup
5. **Development Standards:** Monorepo structure (/frontend, /backend), testing strategy (unit + integration, manual E2E), code quality tooling

Critical constraints:
- 13-day development timeline (deploy by Oct 16, 2025)
- Budget: $10-12/month infrastructure
- No authentication required (internal workshop use)
- Must handle 30 concurrent users on Oct 17 workshop day

Deliverable: Complete architecture.md following the architecture template, ready for developer implementation starting with Epic 1, Story 1.1.
```
