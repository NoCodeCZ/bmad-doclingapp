# Workshop Document Processor

A web application that converts office documents (PDF, DOCX, PPTX, XLSX) into AI-optimized markdown format using Docling. Built for the October 17, 2025 workshop.

## Project Overview

This application enables workshop attendees to convert their own documents for use in Open WebUI with RAG capabilities. The system processes documents in under 2 minutes with a simple drag-and-drop interface.

## Technology Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **TailwindCSS** - Utility-first CSS framework
- **shadcn/ui** - Component library built on Radix UI

### Backend
- **FastAPI** - Modern Python web framework
- **Python 3.11+** - Modern Python with async support
- **Docling** - AI-optimized document parsing
- **Pydantic** - Data validation

### Database & Storage
- **Supabase PostgreSQL** - Managed database
- **Supabase Storage** - Object storage for files

### Deployment
- **DigitalOcean App Platform** - PaaS hosting

## Project Structure

```
workshop-document-processor/
├── frontend/                      # Next.js frontend application
│   ├── src/
│   │   ├── app/                   # Next.js App Router
│   │   ├── components/            # Reusable React components
│   │   ├── hooks/                 # Custom React hooks
│   │   ├── lib/                   # Utilities and configurations
│   │   └── tests/                 # Frontend tests
│   ├── public/                    # Static assets
│   └── package.json               # Frontend dependencies
├── backend/                       # FastAPI backend application
│   ├── app/
│   │   ├── api/endpoints/         # API endpoints
│   │   ├── core/                  # Core configuration
│   │   ├── services/              # Business logic
│   │   ├── models/                # Data models
│   │   └── utils/                 # Helper functions
│   ├── tests/                     # Backend tests
│   └── requirements.txt           # Python dependencies
├── docs/                          # Project documentation
├── package.json                   # Root package.json (workspace config)
└── README.md                      # This file
```

## Getting Started

### Prerequisites

- Node.js 20+ 
- Python 3.11+
- Supabase account

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd workshop-document-processor
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   cd ..
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase credentials
   ```

### Development

1. **Start both services**
   ```bash
   npm run dev
   ```
   This will start:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

2. **Start services individually**
   ```bash
   # Frontend only
   npm run dev:frontend
   
   # Backend only
   npm run dev:backend
   ```

### Testing

```bash
# Run all tests
npm test

# Frontend tests only
npm run test:frontend

# Backend tests only
npm run test:backend
```

### Code Quality

```bash
# Lint all code
npm run lint

# Format all code
npm run format

# Type checking
npm run type-check
```

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

- `GET /api/health` - Health check
- `POST /api/upload` - Upload document for processing
- `GET /api/status/{document_id}` - Check processing status
- `GET /api/download/{document_id}` - Download processed document

## Configuration

### Environment Variables

#### Frontend
- `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anonymous key
- `NEXT_PUBLIC_API_URL` - Backend API URL

#### Backend
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase service key
- `DEBUG` - Enable debug mode
- `MAX_FILE_SIZE` - Maximum file size in bytes (default: 10MB)
- `PROCESSING_TIMEOUT` - Processing timeout in seconds (default: 300)

## Deployment

### DigitalOcean App Platform

1. Connect your repository to DigitalOcean App Platform
2. Configure two services:
   - **Frontend**: Build command `npm run build`, Run command `npm start`
   - **Backend**: Build command `pip install -r requirements.txt`, Run command `uvicorn app.main:app --host 0.0.0.0 --port 8080`
3. Set environment variables in DigitalOcean dashboard
4. Deploy!

## Contributing

1. Follow the coding standards in `docs/architecture/coding-standards.md`
2. Use conventional commits
3. Write tests for new features
4. Ensure all tests pass before submitting

## License

MIT License - see LICENSE file for details.

## Support

For workshop support, please contact the workshop facilitators.