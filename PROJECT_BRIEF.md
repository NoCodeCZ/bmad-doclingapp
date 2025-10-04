# Workshop Document Processor - Project Brief

## Executive Summary

A web application that enables employees to convert documents (PDF, DOCX, PPTX, XLSX) into AI-ready markdown format using Docling, optimized for use with Open WebUI's RAG capabilities.

**Launch Date:** October 17, 2025
**Timeline:** 13 days
**Target Users:** Internal employees (workshop attendees)

---

## Problem Statement

Employees need to use Open WebUI with their own documents, but raw files often have:
- Poor text extraction
- Formatting issues
- Complex layouts that AI struggles to parse

Open WebUI's RAG performs significantly better with clean, well-structured markdown.

---

## Solution

A simple web application powered by **Docling** (open-source document parser) that:
1. Accepts document uploads
2. Processes files into clean markdown
3. Provides downloads ready for Open WebUI

---

## Technical Architecture

### Stack

**Frontend:**
- Next.js 14 (React)
- TailwindCSS
- shadcn/ui components
- react-dropzone

**Backend:**
- FastAPI (Python)
- Docling for document processing
- Async processing

**Storage:**
- Supabase Storage (file storage)
- Supabase PostgreSQL (metadata, history)

**Hosting:**
- DigitalOcean App Platform (all-in-one)
- Cost: $10-12/month

### Architecture Diagram

```
┌─────────────────────────────────────────┐
│    DigitalOcean App Platform            │
│  ┌───────────────────────────────┐      │
│  │  Frontend (Next.js)           │      │
│  │  - Upload UI                  │      │
│  │  - Status display             │      │
│  │  - Download interface         │      │
│  └───────────────────────────────┘      │
│                                          │
│  ┌───────────────────────────────┐      │
│  │  Backend (FastAPI + Docling)  │      │
│  │  - File processing            │      │
│  │  - Document conversion        │      │
│  │  - API endpoints              │      │
│  └───────────────────────────────┘      │
└──────────────┬───────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│      Supabase (Hosted)                  │
│  - Uploaded files storage               │
│  - Processed files storage              │
│  - Processing metadata                  │
└─────────────────────────────────────────┘
```

---

## Features

### Phase 1: MVP (Core Features)

**Frontend:**
- Drag & drop file upload
- File type validation (PDF, DOCX, PPTX, XLSX)
- Upload progress indicator
- Real-time processing status
- Download button for processed files
- Basic error handling

**Backend:**
- File upload endpoint
- Docling integration
- Markdown generation
- Supabase Storage integration
- Processing status API

**Processing Options:**
- OCR toggle (for scanned documents)
- Table extraction toggle
- Fast vs. Quality mode

### Phase 2: Enhanced Features (Workshop-Ready)

- Processing history view
- Content preview
- Batch upload capability
- Improved error messages
- Instructions page (Open WebUI integration guide)
- Mobile-responsive design

### Phase 3: Post-Workshop (Optional)

- User authentication
- File management (delete, re-download)
- Usage analytics
- Team sharing
- Admin panel

---

## User Flow

```
1. User visits app
2. Drags/uploads document file
3. (Optional) Selects processing options
4. Clicks "Process" button
5. Backend processes via Docling
6. User sees real-time progress
7. Download button appears when complete
8. User downloads markdown file
9. Uploads to Open WebUI Documents
```

---

## Database Schema

```sql
-- Documents table
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  original_filename TEXT NOT NULL,
  file_type TEXT NOT NULL,
  file_size INTEGER,
  status TEXT DEFAULT 'pending',
  original_file_path TEXT,
  processed_file_path TEXT,
  processing_options JSONB,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP
);
```

---

## Development Timeline

### Week 1: Core Development (Oct 5-11)

**Day 1-2 (Oct 5-6):**
- Setup DigitalOcean App Platform
- Create Next.js frontend project
- Create FastAPI backend project
- Setup Supabase storage buckets

**Day 3-4 (Oct 7-8):**
- Build upload UI
- Implement file upload to Supabase
- Integrate Docling in backend
- Create processing endpoint

**Day 5-6 (Oct 9-10):**
- Connect frontend to backend
- Add status polling
- Implement download functionality
- Basic error handling

**Day 7 (Oct 11):**
- First deployment to DigitalOcean
- Testing with sample documents
- Bug fixes

### Week 2: Polish & Launch (Oct 12-17)

**Day 8-9 (Oct 12-13):**
- UI polish
- Add instructions page
- Processing options (OCR toggle)
- Preview functionality

**Day 10-11 (Oct 14-15):**
- Final testing
- Performance optimization
- Create user guide
- Test with various file types

**Day 12-13 (Oct 16):**
- Final deployment
- Smoke testing
- Prepare workshop demo

**Day 14 (Oct 17): WORKSHOP DAY! 🎉**

---

## Performance Optimization

### Docling Configuration

**Fast Mode (Default):**
```python
PdfPipelineOptions(
    do_ocr=False,           # Skip OCR
    do_table_structure=True  # Keep tables
)
```

**Quality Mode (User selectable):**
```python
PdfPipelineOptions(
    do_ocr=True,            # Enable OCR
    do_table_structure=True
)
```

### Expected Processing Times

- Clean PDF: 10-30 seconds
- Scanned PDF (OCR): 1-2 minutes
- DOCX/PPTX: 5-15 seconds
- XLSX: 5-10 seconds

### Scalability

- DigitalOcean App Platform auto-scales
- Can handle 5-10 concurrent processes
- Sufficient for 30 workshop attendees

---

## Deployment Configuration

### DigitalOcean App Spec

```yaml
name: docling-workshop-app
region: nyc

services:
  - name: frontend
    source_dir: /frontend
    build_command: npm run build
    run_command: npm start
    environment_slug: node-js
    instance_size_slug: basic-xxs
    routes:
      - path: /

  - name: backend
    source_dir: /backend
    build_command: pip install -r requirements.txt
    run_command: uvicorn main:app --host 0.0.0.0 --port 8080
    environment_slug: python
    instance_size_slug: basic-xs
    routes:
      - path: /api
    envs:
      - key: SUPABASE_URL
      - key: SUPABASE_KEY
```

---

## Project Structure

```
docling-workshop-app/
├── frontend/              # Next.js app
│   ├── app/
│   │   ├── page.tsx      # Upload page
│   │   └── layout.tsx
│   ├── components/
│   │   ├── FileUpload.tsx
│   │   ├── ProcessingStatus.tsx
│   │   └── DownloadButton.tsx
│   └── lib/
│       └── supabase.ts
│
├── backend/               # FastAPI app
│   ├── main.py           # Main API
│   ├── docling_processor.py
│   ├── supabase_client.py
│   └── requirements.txt
│
└── .do/                  # DigitalOcean config
    └── app.yaml
```

---

## Testing Checklist

**Before Workshop:**
- [ ] Test PDF upload (clean text)
- [ ] Test PDF with OCR (scanned)
- [ ] Test DOCX upload
- [ ] Test PPTX upload
- [ ] Test XLSX upload
- [ ] Test large file (10MB+)
- [ ] Test error cases (corrupted files)
- [ ] Test concurrent uploads (5+ users)
- [ ] Verify markdown quality in Open WebUI
- [ ] Mobile responsiveness

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Slow processing during workshop | High | Disable OCR by default, optimize Docling config |
| Too many concurrent users | Medium | DigitalOcean auto-scales, test beforehand |
| Service downtime | High | Thorough testing Oct 16, have backup plan |
| Poor output quality | High | Test with actual workshop document types |
| Large file uploads | Low | Set file size limits, provide guidance |

---

## Success Criteria

### Must Have (Launch Blockers)
- [ ] Users can upload files
- [ ] Files process successfully
- [ ] Users can download markdown
- [ ] Works on mobile and desktop
- [ ] No crashes under normal use

### Should Have (Important)
- [ ] Processing takes < 2 minutes
- [ ] Clear error messages
- [ ] Instructions provided
- [ ] Preview functionality
- [ ] Professional UI

### Nice to Have (Post-Workshop)
- [ ] Processing history
- [ ] Batch processing
- [ ] Custom domain
- [ ] Analytics

---

## Cost Estimate

| Service | Plan | Monthly Cost |
|---------|------|--------------|
| Vercel/DigitalOcean Frontend | Basic | $5 |
| DigitalOcean Backend | Basic | $5-7 |
| Supabase | Free tier | $0 |
| **Total** | | **$10-12/month** |

---

## Workshop Day Preparation

**Provide Attendees:**
1. App URL (*.ondigitalocean.app)
2. Quick start guide (1-page PDF)
3. Sample document to test
4. Open WebUI integration instructions

**Have Ready:**
- [ ] App running smoothly
- [ ] Backup plan (local version if needed)
- [ ] Sample processed files
- [ ] Troubleshooting guide
- [ ] Support contact info

---

## Key Decisions

✅ **Workshop Date:** October 17, 2025
✅ **No Authentication:** Keep it simple for workshop
✅ **Hosting:** DigitalOcean App Platform (all-in-one)
✅ **Domain:** Use DigitalOcean subdomain initially
✅ **Processing:** CPU-based (sufficient for workshop)
✅ **Timeline:** 13 days - Achievable with focused development

---

## Next Steps

1. Setup Supabase project
2. Create repository structure
3. Setup development environment
4. Build Phase 1 features
5. Deploy to DigitalOcean
6. Test and iterate
7. Launch workshop!

---

## Appendix: Technology Decisions Rationale

**Why Docling?**
- Open-source, no vendor lock-in
- Excellent AI-optimized output
- Supports multiple formats
- Local processing (data privacy)
- Active development

**Why Next.js?**
- Modern, production-ready
- Great developer experience
- Server components for performance
- Easy Vercel deployment

**Why FastAPI?**
- Fast, async Python framework
- Easy Docling integration
- Auto-generated API docs
- Type safety with Pydantic

**Why Supabase?**
- Already hosted
- Storage + Database in one
- Easy to use
- Generous free tier

**Why DigitalOcean?**
- Simple deployment
- Affordable pricing
- Good Python support
- Auto-scaling built-in
