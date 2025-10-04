# Workshop Document Processor - Source Tree Structure

## Project Root Structure

```
workshop-document-processor/
├── .bmad-core/                    # BMad Method configuration and agents
├── .claude/                       # Claude Code command configurations
├── .git/                          # Git version control
├── docs/                          # Project documentation
├── frontend/                      # Next.js frontend application
├── backend/                       # FastAPI backend application
├── README.md                      # Project overview and setup
├── .gitignore                     # Git ignore patterns
├── .env.example                   # Environment variables template
└── package.json                   # Root package.json (workspace config)
```

## Frontend Directory Structure

```
frontend/
├── public/                        # Static assets
│   ├── favicon.ico
│   ├── next.svg
│   └── icons/                     # Application icons
├── src/
│   ├── app/                       # Next.js App Router
│   │   ├── layout.tsx             # Root layout component
│   │   ├── page.tsx               # Home page (upload screen)
│   │   ├── instructions/
│   │   │   └── page.tsx           # Instructions page
│   │   ├── processing/
│   │   │   └── [id]/
│   │   │       └── page.tsx       # Processing status page
│   │   ├── download/
│   │   │   └── [id]/
│   │   │       └── page.tsx       # Download page
│   │   ├── globals.css            # Global styles
│   │   └── favicon.ico
│   ├── components/                # Reusable React components
│   │   ├── ui/                    # shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── alert.tsx
│   │   │   ├── progress.tsx
│   │   │   ├── accordion.tsx
│   │   │   └── index.ts           # Barrel export
│   │   ├── FileDropzone.tsx       # File upload component
│   │   ├── ProcessingCard.tsx     # Processing status display
│   │   ├── StatusAlert.tsx        # Success/error alerts
│   │   ├── ProcessingOptions.tsx  # OCR and mode selection
│   │   ├── ActionButton.tsx       # Primary/secondary buttons
│   │   ├── InstructionsAccordion.tsx # Troubleshooting accordion
│   │   └── Header.tsx             # Application header
│   ├── hooks/                     # Custom React hooks
│   │   ├── useFileUpload.ts       # File upload logic
│   │   ├── useStatusPolling.ts    # Status polling logic
│   │   ├── useProcessingOptions.ts # Processing options state
│   │   └── useErrorHandler.ts     # Error handling logic
│   ├── lib/                       # Utilities and configurations
│   │   ├── supabase.ts            # Supabase client configuration
│   │   ├── types.ts               # TypeScript type definitions
│   │   ├── constants.ts           # Application constants
│   │   ├── utils.ts               # General utility functions
│   │   └── validations.ts         # Form validation functions
│   ├── styles/                    # Custom styles (beyond Tailwind)
│   │   └── components.css         # Component-specific styles
│   └── tests/                     # Frontend tests
│       ├── __mocks__/             # Mock files
│       ├── components/            # Component tests
│       ├── hooks/                 # Hook tests
│       ├── utils/                 # Utility tests
│       └── setup.ts               # Test configuration
├── package.json                   # Frontend dependencies
├── tsconfig.json                  # TypeScript configuration
├── tailwind.config.js             # TailwindCSS configuration
├── next.config.js                 # Next.js configuration
├── eslint.config.js               # ESLint configuration
├── prettier.config.js             # Prettier configuration
├── vitest.config.ts               # Vitest configuration
└── .env.local                     # Local environment variables
```

## Backend Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Application configuration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                # FastAPI dependencies
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── upload.py          # File upload endpoint
│   │       ├── status.py          # Status checking endpoint
│   │       ├── download.py        # File download endpoint
│   │       └── health.py          # Health check endpoint
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py            # Security utilities
│   │   ├── config.py              # Core configuration
│   │   └── exceptions.py          # Custom exceptions
│   ├── services/
│   │   ├── __init__.py
│   │   ├── docling_service.py     # Document processing service
│   │   ├── supabase_service.py    # Supabase integration service
│   │   ├── file_service.py        # File management service
│   │   └── processing_service.py  # Processing orchestration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py             # Pydantic models
│   │   ├── database.py            # Database models
│   │   └── enums.py               # Enum definitions
│   └── utils/
│       ├── __init__.py
│       ├── logger.py              # Logging configuration
│       ├── validators.py          # Input validators
│       └── helpers.py             # Helper functions
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration
│   ├── test_api/
│   │   ├── __init__.py
│   │   ├── test_upload.py         # Upload endpoint tests
│   │   ├── test_status.py         # Status endpoint tests
│   │   ├── test_download.py       # Download endpoint tests
│   │   └── test_health.py         # Health check tests
│   ├── test_services/
│   │   ├── __init__.py
│   │   ├── test_docling_service.py # Docling service tests
│   │   ├── test_supabase_service.py # Supabase service tests
│   │   └── test_file_service.py   # File service tests
│   └── fixtures/                  # Test data fixtures
│       ├── sample_files/          # Sample documents for testing
│       └── test_data.py           # Test data generators
├── requirements.txt               # Python dependencies
├── requirements-dev.txt           # Development dependencies
├── pyproject.toml                 # Python project configuration
├── .env.example                   # Environment variables template
├── .env                           # Local environment variables
├── alembic.ini                    # Database migration config (if needed)
├── migrations/                    # Database migrations (if needed)
└── Dockerfile                     # Docker configuration (optional)
```

## Documentation Directory Structure

```
docs/
├── brief.md                       # Project brief
├── prd.md                         # Product Requirements Document
├── front-end-spec.md              # UI/UX specifications
├── architecture.md                # System architecture document
├── architecture/                  # Architecture details
│   ├── coding-standards.md        # Development standards
│   ├── tech-stack.md              # Technology stack details
│   └── source-tree.md             # Project structure guide
├── prd/                           # Sharded PRD documents
│   ├── epic-1-foundation.md
│   ├── epic-2-user-experience.md
│   └── epic-3-production-readiness.md
├── stories/                       # User stories for development
│   ├── 1.1.project-setup.md
│   ├── 1.2.supabase-integration.md
│   └── ...
└── qa/                            # Quality assurance documents
    ├── assessments/               # QA assessments and reports
    └── gates/                     # Quality gate decisions
```

## BMad Core Directory Structure

```
.bmad-core/
├── core-config.yaml               # BMad configuration
├── install-manifest.yaml          # Installation manifest
├── user-guide.md                  # User documentation
├── enhanced-ide-development-workflow.md # Development workflow
├── working-in-the-brownfield.md   # Brownfield project guide
├── agents/                        # BMad agents
│   ├── pm.md                      # Product Manager agent
│   ├── architect.md               # Architect agent
│   ├── dev.md                     # Developer agent
│   ├── qa.md                      # Test Architect agent
│   ├── sm.md                      # Scrum Master agent
│   ├── po.md                      # Product Owner agent
│   ├── ux-expert.md               # UX Expert agent
│   ├── analyst.md                 # Analyst agent
│   ├── bmad-master.md             # Master agent
│   └── bmad-orchestrator.md       # Orchestrator agent
├── tasks/                         # BMad tasks
│   ├── create-doc.md
│   ├── shard-doc.md
│   ├── create-next-story.md
│   ├── review-story.md
│   └── ...
├── templates/                     # Document templates
│   ├── prd-tmpl.yaml
│   ├── story-tmpl.yaml
│   ├── architecture-tmpl.yaml
│   └── ...
├── checklists/                    # Quality checklists
│   ├── architect-checklist.md
│   ├── story-dod-checklist.md
│   └── ...
├── workflows/                     # Workflow definitions
│   ├── greenfield-fullstack.yaml
│   ├── brownfield-fullstack.yaml
│   └── ...
├── agent-teams/                   # Agent team configurations
│   ├── team-fullstack.yaml
│   ├── team-ide-minimal.yaml
│   └── ...
├── data/                          # Knowledge base data
│   ├── bmad-kb.md
│   ├── technical-preferences.md
│   └── ...
└── utils/                         # Utility files
    ├── bmad-doc-template.md
    └── workflow-management.md
```

## Claude Code Directory Structure

```
.claude/
├── commands/
│   ├── BMad/                      # BMad Core commands
│   │   ├── agents/                 # Agent configurations
│   │   └── tasks/                  # Task configurations
│   └── bmad-cw/                   # Creative Writing commands
│       ├── agents/
│       └── tasks/
└── settings.json                  # Claude Code settings
```

## File Naming Conventions

### Frontend Files
- **Components**: PascalCase (FileDropzone.tsx, ProcessingCard.tsx)
- **Hooks**: camelCase with 'use' prefix (useFileUpload.ts, useStatusPolling.ts)
- **Utilities**: camelCase (utils.ts, validations.ts)
- **Types**: camelCase (types.ts, constants.ts)
- **Pages**: lowercase with dashes (instructions/page.tsx)

### Backend Files
- **Modules**: lowercase with underscores (docling_service.py, supabase_service.py)
- **Classes**: PascalCase (DocumentProcessor, FileManager)
- **Functions**: snake_case (process_document, upload_file)
- **Constants**: UPPER_CASE (MAX_FILE_SIZE, DEFAULT_TIMEOUT)

### Documentation Files
- **Main docs**: lowercase with dashes (architecture.md, coding-standards.md)
- **Stories**: numbered with dots (1.1.project-setup.md, 2.1.processing-options.md)
- **Epics**: numbered with prefix (epic-1-foundation.md)

## Import/Export Patterns

### Frontend Imports
```typescript
// Component imports
import { FileDropzone } from '@/components/FileDropzone';
import { Button, Card, Alert } from '@/components/ui';

// Hook imports
import { useFileUpload } from '@/hooks/useFileUpload';
import { useStatusPolling } from '@/hooks/useStatusPolling';

// Utility imports
import { validateFileType } from '@/lib/validations';
import { API_ENDPOINTS } from '@/lib/constants';
import type { DocumentStatus } from '@/lib/types';
```

### Backend Imports
```python
# Standard library imports
from typing import List, Optional, Dict, Any
from pathlib import Path

# Third-party imports
from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel
import supabase

# Local imports
from app.core.config import settings
from app.services.docling_service import DoclingService
from app.models.schemas import DocumentUpload, ProcessingResult
```

## Configuration Files

### Root Configuration
- **package.json**: Workspace configuration and scripts
- **.gitignore**: Git ignore patterns for Node.js, Python, and IDEs
- **README.md**: Project overview and setup instructions

### Frontend Configuration
- **next.config.js**: Next.js configuration
- **tsconfig.json**: TypeScript configuration
- **tailwind.config.js**: TailwindCSS configuration
- **eslint.config.js**: ESLint configuration
- **prettier.config.js**: Prettier configuration

### Backend Configuration
- **requirements.txt**: Python dependencies
- **pyproject.toml**: Python project configuration
- **.env**: Environment variables

## Testing Structure

### Frontend Tests
- **Unit Tests**: Component and hook testing
- **Integration Tests**: API client testing
- **Mock Files**: External dependency mocking
- **Test Utils**: Custom testing utilities

### Backend Tests
- **Unit Tests**: Service and utility testing
- **Integration Tests**: API endpoint testing
- **Fixtures**: Test data and sample files
- **Test Configuration**: Pytest setup and fixtures

## Deployment Structure

### Build Outputs
- **Frontend**: `.next/` directory (Next.js build output)
- **Backend**: No build step required (Python interpreted)

### Environment Files
- **.env.example**: Template for environment variables
- **.env.local**: Local development variables
- **Production**: Environment variables set in DigitalOcean

This source tree structure provides a clean, organized foundation for the Workshop Document Processor project, supporting rapid development while maintaining code quality and scalability.