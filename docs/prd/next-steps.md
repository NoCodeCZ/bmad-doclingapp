# Next Steps

## UX Expert Prompt

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

## Architect Prompt

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