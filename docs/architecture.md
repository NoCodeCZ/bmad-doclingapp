# Workshop Document Processor System Architecture

## Overview

The Workshop Document Processor is a web application designed to convert office documents (PDF, DOCX, PPTX, XLSX) into AI-optimized markdown format using Docling. The system is built as a monorepo with two main services: a Next.js frontend and a FastAPI backend, deployed on DigitalOcean App Platform with Supabase for data storage and file management.

## Service Architecture

### Frontend Service (Next.js 14)
- **Framework**: Next.js 14 with App Router and React Server Components
- **Styling**: TailwindCSS with shadcn/ui component library
- **File Upload**: react-dropzone for drag-and-drop functionality
- **State Management**: React hooks + Context API
- **Deployment**: DigitalOcean App Platform

### Backend Service (FastAPI)
- **Framework**: FastAPI (Python 3.11+) with async processing
- **Document Processing**: Docling library with OCR and quality modes
- **Validation**: Pydantic models for request/response validation
- **API Documentation**: Automatic OpenAPI docs generation
- **Deployment**: DigitalOcean App Platform

### Database & Storage (Supabase)
- **Database**: PostgreSQL for document metadata
- **File Storage**: Two private buckets (uploads, processed)
- **Client Libraries**: @supabase/supabase-js (frontend), supabase-py (backend)

## Data Architecture

### Database Schema
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('queued', 'processing', 'complete', 'failed')),
    processing_options JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT
);
```

### File Storage Structure
- **uploads/**: Original uploaded files
- **processed/**: Converted markdown files
- Both buckets configured as private with backend-only access

## API Contracts

### Upload Endpoint
```
POST /api/upload
Content-Type: multipart/form-data
Response: {
  "id": "uuid",
  "filename": "document.pdf",
  "status": "queued"
}
```

### Status Endpoint
```
GET /api/status/{document_id}
Response: {
  "id": "uuid",
  "filename": "document.pdf",
  "status": "processing",
  "progress_stage": "processing",
  "elapsed_time": 45
}
```

### Download Endpoint
```
GET /api/download/{document_id}
Response: Streaming markdown file with content-disposition header
```

## Infrastructure Architecture

### Deployment Structure
- **Monorepo**: Single Git repository with `/frontend` and `/backend` directories
- **Services**: Two separate containers on DigitalOcean App Platform
- **Environments**: Staging and production with separate Supabase instances
- **Auto-scaling**: Enabled for both services to handle 30 concurrent users

### Monitoring & Logging
- **Health Checks**: `/api/health` (backend), `/_health` (frontend)
- **Metrics**: DigitalOcean built-in monitoring (CPU, memory, request rate, error rate)
- **Log Aggregation**: Centralized logs with 7-day retention
- **Alerts**: Health check failures and error rate thresholds

## Security Architecture

### File Security
- **File Size Limits**: 10MB maximum enforced client and server-side
- **File Type Validation**: Only PDF, DOCX, PPTX, XLSX allowed
- **Processing Timeout**: 5-minute hard timeout on Docling operations
- **Private Storage**: All files stored in private Supabase buckets

### API Security
- **CORS**: Frontend and backend on same domain (no CORS complexity)
- **Input Validation**: Pydantic models for all API endpoints
- **Error Handling**: User-friendly error messages without technical details

## Development Architecture

### Monorepo Structure
```
/
├── frontend/                 # Next.js application
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── next.config.js
├── backend/                  # FastAPI application
│   ├── app/
│   ├── tests/
│   ├── requirements.txt
│   └── main.py
├── docs/                     # Documentation
├── .bmad-core/              # BMad Method configuration
└── README.md
```

### Testing Strategy
- **Backend**: Unit tests (pytest) + integration tests for Supabase operations
- **Frontend**: Unit tests (Vitest, React Testing Library) for UI components
- **E2E**: Manual testing for complete upload→process→download workflow

## Performance Architecture

### Processing Pipeline
- **Async Processing**: FastAPI async endpoints for non-blocking operations
- **Status Polling**: 2-second intervals for status updates
- **File Streaming**: Direct streaming from Supabase storage for downloads
- **Connection Pooling**: Optimized database connections for concurrent users

### Performance Targets
- **Upload Response**: < 1 second
- **Processing Time**: < 30 seconds (clean PDF), < 2 minutes (OCR)
- **Download Start**: < 2 seconds
- **Concurrent Users**: 30 simultaneous users

## Quality Assurance Architecture

### Test Architect Integration
- **Risk Assessment**: Pre-development risk profiling for complex stories
- **Test Design**: Comprehensive test strategy creation
- **Requirements Tracing**: Coverage verification during development
- **Quality Gates**: PASS/CONCERNS/FAIL decisions with documented criteria

### Error Handling Strategy
- **Client-side Validation**: Immediate feedback on file selection
- **Server-side Validation**: Double-check all inputs
- **Graceful Degradation**: Clear error messages with actionable guidance
- **Recovery Patterns**: Retry mechanisms and alternative approaches

## Future Scalability

### Horizontal Scaling
- **Load Balancing**: DigitalOcean App Platform auto-scaling
- **Database Scaling**: Supabase connection pooling and read replicas
- **File Storage**: CDN integration for static assets
- **Processing Queue**: Background job processing for high volume

### Feature Expansion
- **Batch Processing**: Multiple file upload capability
- **User Authentication**: Individual user accounts and file management
- **Advanced Processing**: Custom processing configurations
- **API Access**: Programmatic document processing capabilities

## Technology Stack Summary

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS + shadcn/ui
- **File Upload**: react-dropzone
- **HTTP Client**: Native fetch API

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Document Processing**: Docling library
- **Validation**: Pydantic
- **Database**: Supabase PostgreSQL
- **File Storage**: Supabase Storage

### Infrastructure
- **Hosting**: DigitalOcean App Platform
- **Database**: Supabase (PostgreSQL)
- **File Storage**: Supabase Storage
- **Monitoring**: DigitalOcean built-in tools
- **Deployment**: Git-based automatic deployments

## Development Standards

### Code Quality
- **Frontend**: ESLint + Prettier, TypeScript strict mode
- **Backend**: Black + Ruff formatting, type hints
- **Git**: Conventional commits, feature branch workflow
- **Testing**: Minimum 80% coverage for business logic

### Documentation Standards
- **API Documentation**: Automatic OpenAPI generation
- **Code Comments**: JSDoc (frontend), docstrings (backend)
- **Architecture Documentation**: Living documents updated with changes
- **User Documentation**: Clear instructions for workshop attendees

This architecture provides a solid foundation for the Workshop Document Processor, ensuring reliability, scalability, and maintainability while meeting the tight 13-day development timeline.