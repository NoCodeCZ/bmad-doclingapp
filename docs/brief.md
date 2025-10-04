# Project Brief: Workshop Document Processor

## Executive Summary

The **Workshop Document Processor** is a web application that converts office documents (PDF, DOCX, PPTX, XLSX) into AI-optimized markdown format using Docling, specifically designed to improve RAG performance in Open WebUI. The application targets internal employees attending a workshop on October 17, 2025, providing a simple drag-and-drop interface that processes documents into clean, well-structured markdown that dramatically improves AI comprehension and retrieval quality. This 13-day development sprint delivers a production-ready tool that solves the critical problem of poor document parsing in AI systems, enabling workshop attendees to immediately leverage their own documents with Open WebUI's RAG capabilities.

## Problem Statement

Employees need to leverage their own documents with Open WebUI's RAG (Retrieval-Augmented Generation) capabilities, but raw office files suffer from critical extraction problems that severely degrade AI performance:

**Current State & Pain Points:**
- PDF files produce fragmented text with poor structure preservation
- Complex layouts (tables, multi-column formats, embedded images) confuse standard parsers
- Scanned documents remain unreadable without OCR processing
- DOCX, PPTX, and XLSX files lose formatting context during conversion
- Inconsistent extraction quality leads to incomplete or inaccurate AI responses

**Impact:**
- RAG systems retrieve irrelevant chunks due to poor document structure
- AI responses lack accuracy when working with poorly-parsed source material
- Users waste time reformatting documents manually or get frustrated with poor results
- Workshop attendees (30 people) need a working solution by October 17, 2025

**Why Existing Solutions Fall Short:**
- Generic converters don't optimize for AI/RAG consumption
- Manual markdown conversion is time-consuming and inconsistent
- Open WebUI's built-in parsing doesn't handle complex document layouts well
- No current tool specifically targets "AI-ready" markdown output

**Urgency:**
- Workshop deadline creates hard timeline (13 days)
- Early adoption of Open WebUI internally depends on document quality
- Employees are eager to use RAG with their domain-specific documents

## Proposed Solution

The Workshop Document Processor leverages **Docling**, an open-source document parser specifically optimized for AI consumption, to transform complex office documents into clean, semantically-rich markdown that maximizes RAG retrieval accuracy.

**Core Concept:**
- Simple web interface: drag-and-drop upload → automatic processing → download markdown
- Backend processing pipeline using Docling's AI-optimized extraction algorithms
- Intelligent handling of complex layouts (tables, multi-column text, embedded content)
- Configurable processing modes (Fast mode vs. Quality mode with OCR)
- Real-time status updates during processing

**Key Differentiators:**
- **AI-First Design:** Output specifically structured for RAG chunking and retrieval (unlike generic converters)
- **Docling Engine:** Open-source, actively developed, designed for LLM consumption
- **Zero Manual Work:** Fully automated pipeline requiring no user reformatting
- **Privacy-Focused:** Local document processing (no third-party APIs), data stored in private Supabase instance
- **Workshop-Ready:** Optimized for 30 concurrent users with auto-scaling infrastructure

**Why This Will Succeed:**
- Addresses the specific gap between "raw documents" and "RAG-ready content"
- Docling has proven superior markdown output quality for AI applications
- Simple UX removes friction (no learning curve for workshop attendees)
- Focused scope (document conversion only) ensures delivery within 13-day timeline
- Built for internal use first, reducing external pressure and compliance requirements

**High-Level Vision:**
A production-quality tool that becomes the standard internal solution for document preparation before RAG ingestion, with potential to expand to external use cases post-workshop.

## Target Users

### Primary User Segment: Internal Workshop Attendees

**Demographic/Firmographic Profile:**
- Internal employees across various departments (engineering, product, marketing, operations)
- 30 attendees for the October 17, 2025 workshop
- Technical literacy: Mixed (from basic computer users to advanced developers)
- Organizational role: Individual contributors and managers seeking to leverage AI tools

**Current Behaviors and Workflows:**
- Currently use Open WebUI for AI-assisted tasks (research, analysis, content generation)
- Have domain-specific documents (reports, presentations, spreadsheets, technical docs)
- Manually upload documents to Open WebUI's RAG feature with inconsistent results
- Experience frustration when AI responses don't accurately reflect document content
- Some users attempt manual markdown conversion (time-consuming, inconsistent)

**Specific Needs and Pain Points:**
- Need reliable way to prepare documents for RAG ingestion
- Want zero-effort solution (no manual formatting or technical setup)
- Require fast processing (workshop setting has time constraints)
- Need confidence that converted documents will work properly in Open WebUI
- Desire to use their own organizational knowledge (not just public information)

**Goals They're Trying to Achieve:**
- Build custom AI assistants using their own organizational documents
- Get accurate, context-aware responses from Open WebUI based on their specific files
- Demonstrate value of RAG to their teams/stakeholders
- Leave the workshop with working examples using their real documents

### Secondary User Segment: Post-Workshop Internal Users

**Demographic/Firmographic Profile:**
- Employees who didn't attend the workshop but hear about the tool
- Teams looking to build departmental knowledge bases with RAG
- Technical literacy: Varied (tool must remain accessible to non-technical users)

**Current Behaviors and Workflows:**
- May not yet be using Open WebUI but interested after hearing about it
- Have accumulated document repositories they want to make searchable/queryable
- Currently rely on manual search through folders or traditional search tools

**Specific Needs and Pain Points:**
- Need simple onboarding (no workshop training available)
- Require batch processing for multiple documents
- Want document management features (re-download, history)

**Goals They're Trying to Achieve:**
- Quickly convert document libraries for RAG use
- Enable team-wide access to organizational knowledge
- Reduce time spent searching for information in documents

## Goals & Success Metrics

### Business Objectives

- **Workshop Success:** 80%+ of attendees successfully convert and use their own documents in Open WebUI during the workshop session
- **Adoption Rate:** Achieve 50+ documents processed within first week post-workshop (organic adoption indicator)
- **Reliability:** Maintain 95%+ successful conversion rate across all supported file types
- **Performance:** Process documents within acceptable timeframes (< 2 minutes including OCR, < 30 seconds for clean PDFs)
- **Launch Timeline:** Deploy production-ready application by October 16, 2025 (1 day buffer before workshop)

### User Success Metrics

- **Task Completion:** Users successfully upload, process, and download markdown files without assistance
- **Quality Perception:** Users report improved RAG response quality when using processed documents (post-workshop survey)
- **Time Savings:** Average document preparation time reduced from 15-30 minutes (manual) to < 2 minutes (automated)
- **Return Usage:** 40%+ of workshop attendees return to process additional documents within 2 weeks

### Key Performance Indicators (KPIs)

- **Conversion Success Rate:** Percentage of uploads that complete successfully without errors - Target: 95%+
- **Processing Time (p95):** 95th percentile processing time for standard documents - Target: < 2 minutes
- **Concurrent User Handling:** System stability under workshop load (30 users) - Target: No crashes or timeouts
- **Error Recovery:** Percentage of failures with clear, actionable error messages - Target: 100%
- **Document Quality Score:** User-reported quality of markdown output (1-5 scale, post-workshop survey) - Target: 4.0+ average

## MVP Scope

### Core Features (Must Have)

- **File Upload Interface:** Drag-and-drop or click-to-browse upload supporting PDF, DOCX, PPTX, XLSX file types with client-side validation and visual feedback
- **Document Processing Pipeline:** Backend integration with Docling to convert uploaded documents into AI-optimized markdown format
- **Real-time Status Display:** Live processing status updates (queued → processing → complete/failed) with progress indication
- **Markdown Download:** One-click download of processed markdown files with original filename preservation
- **Processing Options:** User-selectable toggles for OCR (on/off) and processing mode (Fast/Quality) to balance speed vs. accuracy
- **Error Handling:** Clear, actionable error messages for common failures (unsupported format, file too large, processing timeout, corrupted file)
- **File Storage:** Supabase Storage integration for uploaded and processed files with metadata tracking in PostgreSQL
- **Mobile Responsiveness:** Functional UI on mobile devices (workshop attendees may use phones/tablets)
- **Instructions Page:** Simple guide explaining how to upload processed markdown to Open WebUI's RAG feature

### Out of Scope for MVP

- User authentication (keep it open for workshop simplicity)
- Batch file upload (process one at a time initially)
- File management UI (delete, re-download previous files)
- Document preview (show markdown before download)
- Processing history view
- Custom processing configurations beyond OCR/mode toggles
- Team sharing or collaboration features
- Admin dashboard or usage analytics
- Custom domain (use DigitalOcean subdomain)
- API for programmatic access

### MVP Success Criteria

**The MVP is successful if:**
- Any workshop attendee can upload a document, wait for processing, download markdown, and use it in Open WebUI—all without assistance or documentation
- The system handles 10 concurrent uploads without crashes or significant performance degradation
- 90%+ of common document types (clean PDFs, standard DOCX/PPTX/XLSX) convert successfully
- Processing completes within timeframes users find acceptable (visual feedback makes waiting tolerable)
- Error messages enable users to self-correct issues (e.g., "File too large - max 10MB" vs. generic "Error")

## Post-MVP Vision

### Phase 2 Features

Based on workshop feedback, potential improvements include:

- Processing history view
- Batch upload capability
- Content preview before download
- Better error messages for edge cases

### Long-term Vision

This tool solves a specific problem for the workshop. If it proves useful, it may become a standard internal utility for document preparation. Future direction will be driven entirely by actual user needs post-workshop.

### Expansion Opportunities

No planned expansion beyond internal use at this time.

## Technical Considerations

### Platform Requirements

- **Target Platforms:** Web application (browser-based, no native apps)
- **Browser/OS Support:** Modern browsers (Chrome, Firefox, Safari, Edge - last 2 versions), works on desktop and mobile devices
- **Performance Requirements:** Handle 30 concurrent users during workshop, process standard documents in < 2 minutes, support files up to 10MB

### Technology Preferences

- **Frontend:** Next.js 14 (React framework with server components), TailwindCSS for styling, shadcn/ui component library, react-dropzone for file uploads
- **Backend:** FastAPI (Python async framework), Docling library for document processing, Pydantic for request/response validation
- **Database:** Supabase PostgreSQL for document metadata (filename, status, timestamps), Supabase Storage for file storage (uploaded and processed files)
- **Hosting/Infrastructure:** DigitalOcean App Platform (hosts both frontend and backend services with auto-scaling)

### Architecture Considerations

- **Repository Structure:** Monorepo with `/frontend` and `/backend` directories
- **Service Architecture:** Two services - Next.js frontend (serves UI), FastAPI backend (handles processing), frontend polls backend for status updates
- **Integration Requirements:** Supabase client libraries (frontend for file upload, backend for storage/database), Docling Python SDK for document conversion
- **Security/Compliance:** Internal use only (no public exposure), file size limits to prevent abuse, no authentication required for MVP (acceptable for workshop), files stored in private Supabase buckets

## Constraints & Assumptions

### Constraints

- **Budget:** $10-12/month infrastructure costs (DigitalOcean App Platform only)
- **Timeline:** 13 days total development time (October 5 - October 17, 2025), hard deadline for workshop on October 17
- **Resources:** Solo developer or small team, limited QA resources (self-testing required)
- **Technical:** CPU-based processing only (no GPU acceleration), DigitalOcean container size limits

### Key Assumptions

- Workshop attendees have basic computer literacy and access to modern web browsers
- Open WebUI is already deployed and accessible to all workshop attendees
- Self-hosted Supabase instance has sufficient capacity for workshop volume
- DigitalOcean App Platform auto-scaling handles 30 concurrent users without manual configuration
- Docling library processes common document formats reliably without extensive customization
- Workshop attendees will tolerate 1-2 minute processing times if given clear status feedback
- Internal network/tools allow access to externally hosted applications (no firewall blocks)
- No formal security review required for internal workshop tools
- Sample documents for testing are available before workshop day

## Risks & Open Questions

### Key Risks

- **Docling Processing Failures:** Complex or corrupted documents may fail to convert, impacting user confidence during workshop - Mitigation: Test with diverse document samples beforehand, provide clear error messages
- **Workshop Day Load:** 30 simultaneous users could overwhelm infrastructure despite auto-scaling claims - Mitigation: Load test with 10-15 concurrent uploads before Oct 17, have manual scaling plan ready
- **Processing Time Perception:** Even 1-2 minute waits may frustrate users if expectations aren't set properly - Mitigation: Clear progress indicators, set expectations on instructions page
- **OCR Quality Issues:** Scanned documents may produce poor-quality markdown despite OCR processing - Mitigation: Test OCR mode extensively, document known limitations for users
- **Timeline Risk:** 13 days is tight; any blocker could jeopardize workshop deadline - Mitigation: Deploy MVP core features by Day 10 (Oct 14), reserve final days for polish and testing

### Open Questions

- What types of documents will workshop attendees actually bring? (Need sample set for testing)
- Is there network/firewall access to DigitalOcean-hosted apps from employee devices?
- What is acceptable processing time for workshop context? (30 seconds? 2 minutes? 5 minutes?)
- Should we provide sample documents if attendees arrive without their own files?
- Who handles support during the workshop if issues arise?
- What happens to the tool post-workshop? (Ongoing maintenance owner?)

### Areas Needing Further Research

- Docling performance benchmarks with representative document types (PDF with tables, scanned images, complex PPTX)
- DigitalOcean App Platform actual auto-scaling behavior under load
- Open WebUI's preferred markdown format/structure for optimal RAG performance

## Appendices

### A. Research Summary

Based on the original PROJECT_BRIEF.md, key research findings include:

**Docling Technology Assessment:**
- Open-source document parser specifically designed for AI/LLM consumption
- Supports PDF, DOCX, PPTX, XLSX formats with intelligent layout handling
- Configurable processing modes (Fast vs. Quality with OCR)
- Active development and proven output quality for RAG applications

**Infrastructure Evaluation:**
- DigitalOcean App Platform selected for simplicity (all-in-one deployment)
- Self-hosted Supabase already available (storage + database)
- Monorepo structure with Next.js frontend + FastAPI backend
- Expected processing times: Clean PDFs (10-30s), OCR PDFs (1-2min), Office docs (5-15s)

### C. References

- Original project specification: PROJECT_BRIEF.md
- Docling documentation and GitHub repository
- Open WebUI RAG documentation
- DigitalOcean App Platform documentation

## Next Steps

### Immediate Actions

1. Setup development environment (Next.js + FastAPI projects)
2. Create Supabase storage buckets and database schema
3. Integrate Docling in backend and test with sample documents
4. Build core upload/processing/download workflow
5. Deploy to DigitalOcean App Platform
6. Load test with 10-15 concurrent users
7. Final testing and workshop preparation (Oct 16)

### PM Handoff

This Project Brief provides the full context for **Workshop Document Processor**. Please start in 'PRD Generation Mode', review the brief thoroughly to work with the user to create the PRD section by section as the template indicates, asking for any necessary clarification or suggesting improvements.
