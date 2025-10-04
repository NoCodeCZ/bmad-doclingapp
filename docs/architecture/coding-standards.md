# Workshop Document Processor - Coding Standards

## General Principles

### Code Quality
- Write clean, readable, and maintainable code
- Follow language-specific conventions and best practices
- Use meaningful variable and function names
- Keep functions small and focused on single responsibilities
- Add comments only when the code isn't self-explanatory

### Error Handling
- Handle errors gracefully and provide meaningful error messages
- Use structured error handling (try-catch blocks, error boundaries)
- Log errors appropriately for debugging
- Never expose sensitive information in error messages

### Security
- Validate all inputs (both client-side and server-side)
- Use parameterized queries to prevent SQL injection
- Sanitize user inputs and outputs
- Follow principle of least privilege

## Frontend Standards (Next.js/React/TypeScript)

### TypeScript Standards
```typescript
// Use explicit types for function parameters and return values
interface DocumentUpload {
  id: string;
  filename: string;
  status: 'queued' | 'processing' | 'complete' | 'failed';
}

const uploadDocument = async (file: File): Promise<DocumentUpload> => {
  // Implementation
};

// Prefer interfaces over types for object shapes
// Use union types for predefined values
type ProcessingMode = 'fast' | 'quality';
```

### React Component Standards
```typescript
// Use functional components with hooks
interface FileDropzoneProps {
  onFileSelect: (file: File) => void;
  maxSize: number;
  acceptedTypes: string[];
}

const FileDropzone: React.FC<FileDropzoneProps> = ({
  onFileSelect,
  maxSize,
  acceptedTypes
}) => {
  // Component implementation
};

// Use proper TypeScript for props
// Destructure props for clarity
// Use React hooks for state and side effects
```

### State Management
```typescript
// Use React hooks for local state
const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');

// Use Context API for global state
interface AppContextType {
  currentDocument: Document | null;
  setCurrentDocument: (doc: Document | null) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);
```

### Styling Standards
```typescript
// Use TailwindCSS classes consistently
// Prefer utility classes over custom CSS
// Use responsive prefixes (sm:, lg:, xl:)
// Use semantic color classes (text-blue-500, not text-custom-blue)

const Button = ({ variant = 'primary', children, ...props }) => (
  <button
    className={`
      px-4 py-2 rounded font-medium transition-colors
      ${variant === 'primary' ? 'bg-blue-500 text-white hover:bg-blue-600' : ''}
      ${variant === 'secondary' ? 'border border-gray-300 hover:bg-gray-50' : ''}
    `}
    {...props}
  >
    {children}
  </button>
);
```

### File Organization
```
src/
├── app/                    # Next.js App Router
│   ├── layout.tsx
│   ├── page.tsx
│   └── api/               # API routes (if any)
├── components/            # Reusable components
│   ├── ui/               # shadcn/ui components
│   ├── FileDropzone.tsx
│   ├── ProcessingCard.tsx
│   └── StatusAlert.tsx
├── hooks/                # Custom hooks
│   ├── useFileUpload.ts
│   └── useStatusPolling.ts
├── lib/                  # Utilities and configurations
│   ├── supabase.ts
│   └── types.ts
└── styles/               # Global styles
    └── globals.css
```

## Backend Standards (FastAPI/Python)

### Python Standards
```python
# Use type hints for all function parameters and return values
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class DocumentUpload(BaseModel):
    filename: str
    file_size: int
    processing_options: Dict[str, Any]

async def process_document(
    document_id: str,
    processing_options: Dict[str, Any]
) -> ProcessingResult:
    """Process a document using Docling."""
    # Implementation
    pass

# Use f-strings for string formatting
# Follow PEP 8 style guide
# Use descriptive variable names
```

### API Endpoint Standards
```python
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse

@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    ocr_enabled: bool = False,
    processing_mode: str = "fast"
) -> DocumentResponse:
    """Upload a document for processing."""
    # Validate file
    if not file.filename.endswith(('.pdf', '.docx', '.pptx', '.xlsx')):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )
    
    # Process upload
    # Return structured response
    pass

# Use proper HTTP status codes
# Provide meaningful error messages
# Use Pydantic models for request/response validation
```

### Database Standards
```python
# Use Supabase client for database operations
from supabase import Client

async def create_document_record(
    supabase: Client,
    filename: str,
    processing_options: Dict[str, Any]
) -> str:
    """Create a new document record."""
    result = supabase.table('documents').insert({
        'filename': filename,
        'status': 'queued',
        'processing_options': processing_options
    }).execute()
    
    return result.data[0]['id']

# Use parameterized queries (handled by Supabase client)
# Handle database errors gracefully
# Use transactions for multi-step operations
```

### Error Handling Standards
```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class DocumentProcessingError(Exception):
    """Custom exception for document processing errors."""
    pass

async def process_with_docling(file_path: str) -> str:
    """Process document using Docling."""
    try:
        # Docling processing
        result = docling_process(file_path)
        return result
    except DoclingError as e:
        logger.error(f"Docling processing failed: {e}")
        raise DocumentProcessingError(f"Processing failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during processing: {e}")
        raise DocumentProcessingError("Unexpected processing error")

# Use custom exceptions for domain-specific errors
# Log errors with appropriate context
# Never expose stack traces to clients
```

### File Organization
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   ├── upload.py
│   │   │   ├── status.py
│   │   │   └── download.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── docling_service.py
│   │   └── supabase_service.py
│   └── models/
│       ├── __init__.py
│       └── schemas.py
├── tests/
│   ├── test_api/
│   ├── test_services/
│   └── conftest.py
└── requirements.txt
```

## Testing Standards

### Frontend Testing
```typescript
// Use React Testing Library for component testing
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { FileDropzone } from './FileDropzone';

describe('FileDropzone', () => {
  it('should accept valid file types', async () => {
    const onFileSelect = jest.fn();
    render(<FileDropzone onFileSelect={onFileSelect} maxSize={10} acceptedTypes={['.pdf']} />);
    
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByRole('button');
    
    fireEvent.change(input, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(onFileSelect).toHaveBeenCalledWith(file);
    });
  });
});

// Test user behavior, not implementation details
// Use meaningful test descriptions
// Mock external dependencies
```

### Backend Testing
```python
# Use pytest for backend testing
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_valid_document():
    """Test uploading a valid document."""
    with open("test_files/sample.pdf", "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("sample.pdf", f, "application/pdf")},
            data={"ocr_enabled": "false", "processing_mode": "fast"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "sample.pdf"
    assert data["status"] == "queued"

# Use descriptive test names
# Test both success and failure scenarios
# Use fixtures for common test data
```

## Git Standards

### Commit Messages
```
# Use conventional commits
feat: add file upload functionality
fix: resolve status polling issue
docs: update API documentation
test: add integration tests for document processing
refactor: improve error handling in docling service

# Format: <type>(<scope>): <description>
# Types: feat, fix, docs, style, refactor, test, chore
```

### Branch Strategy
```
main                    # Production branch
develop                 # Development branch
feature/file-upload     # Feature branches
bugfix/status-polling   # Bugfix branches
hotfix/critical-issue   # Hotfix branches
```

## Performance Standards

### Frontend Performance
- Use React.memo() for expensive components
- Implement lazy loading for large components
- Optimize images and assets
- Use code splitting for better initial load times
- Monitor Core Web Vitals (LCP, FID, CLS)

### Backend Performance
- Use async/await for I/O operations
- Implement connection pooling for database
- Use streaming for large file downloads
- Cache frequently accessed data
- Monitor response times and error rates

## Security Standards

### Input Validation
- Validate all inputs on both client and server
- Use whitelist approach for file types
- Implement file size limits
- Sanitize user inputs before processing

### Data Protection
- Never log sensitive information
- Use environment variables for secrets
- Implement proper error handling without information leakage
- Use HTTPS for all communications

These coding standards ensure consistency, maintainability, and quality across the Workshop Document Processor codebase. All team members should follow these standards and update them as the project evolves.