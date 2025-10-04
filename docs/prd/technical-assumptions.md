# Technical Assumptions

## Repository Structure: Monorepo

Single Git repository with `/frontend` and `/backend` directories. This structure simplifies development coordination, enables shared configuration (TypeScript types, deployment configs), and supports atomic commits spanning both services—critical for a solo developer or small team working under tight timeline. DigitalOcean App Platform natively supports monorepo deployments with multiple services.

## Service Architecture

**Monolith within Monorepo:** Two distinct services deployed as separate containers:
- **Frontend Service:** Next.js 14 application serving React UI with server components, handles file upload initiation and status polling
- **Backend Service:** FastAPI (Python async) application handling Docling document processing, file storage orchestration, and status API endpoints

Communication pattern: Frontend polls backend REST API for processing status (simple, reliable, no WebSocket complexity). Both services connect independently to Supabase (frontend for file upload URLs, backend for storage and database operations).

## Testing Requirements

**Unit + Integration Testing with Manual E2E:**
- **Backend:** Unit tests for Docling integration, API endpoints (pytest, pytest-asyncio); Integration tests for Supabase storage/database operations
- **Frontend:** Unit tests for UI components (Vitest, React Testing Library); Integration tests for API client logic
- **Manual E2E:** Human testing of complete upload→process→download workflow across different file types and browsers (workshop rehearsal serves as final E2E validation)

Rationale: 13-day timeline prohibits comprehensive automated E2E setup. Manual testing with real workshop documents provides highest confidence. Focus automated testing on business logic (Docling processing, API contracts) where bugs are most likely.

## Additional Technical Assumptions and Requests

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