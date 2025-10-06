# Coolify Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Docling Document Processor using Coolify with Docker Compose. This deployment method offers cost savings ($24/month compared to DigitalOcean) while maintaining full control over your infrastructure.

## Prerequisites

- Coolify instance with Docker Compose support
- Git repository access
- Self-hosted Supabase (already configured)
- Domain name for SSL certificates

## Deployment Architecture

### Container Architecture

```mermaid
graph TB
    subgraph "Coolify Host"
        subgraph "Docker Compose"
            A[Frontend Container<br/>Next.js 14<br/>Port 3000]
            B[Backend Container<br/>FastAPI<br/>Port 8080]
            C[Upload Volume<br/>/app/uploads]
        end
        D[Coolify Dashboard<br/>Auto SSL & Monitoring]
    end
    
    subgraph "External Services"
        E[Supabase PostgreSQL<br/>Document Metadata]
        F[Supabase Storage<br/>File Buckets]
    end
    
    G[Users] -->|HTTPS| A
    A -->|API Calls| B
    B -->|Metadata| E
    B -->|Files| F
    B -->|Upload Volume| C
    D -->|Manages| A
    D -->|Manages| B
    
    style A fill:#c8e6c9
    style B fill:#fff9c4
    style C fill:#ffccbc
    style D fill:#e1f5fe
```

### Resource Requirements

**Backend Container:**
- Memory: 2GB
- CPU: 1 core
- Storage: 10GB for uploads
- Processing: Docling document conversion

**Frontend Container:**
- Memory: 1GB
- CPU: 1 core
- Storage: 500MB (static assets)

**Total Infrastructure:**
- RAM: +3GB total
- Disk: +10GB for file uploads
- Bandwidth: Monitor based on usage

## Deployment Steps

### 1. Configure Application in Coolify

#### 1.1 Create New Application
1. **Login to Coolify Dashboard**
2. **Create New Application**
   - Click "New Application"
   - Select "Docker Compose"
   - Name: `docling-processor`

#### 1.2 Connect Git Repository
1. **Repository Settings**
   - Repository: Your Git repository URL
   - Branch: `main`
   - Auto-deploy: Enable
   - Build context: Project root

#### 1.3 Set Environment Variables
Navigate to Environment Variables and add:

```bash
# Supabase Configuration
SUPABASE_URL=https://supabasekong-pgg8kss0oc08oo0gokgossog.app.thit.io/
SUPABASE_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoic2VydmljZV9yb2xlIn0.EnOpR72H05QVdHsjZPsw2IC3vSnOUcwOWd8MreYffR4
SUPABASE_ANON_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc1OTMyNjAwMCwiZXhwIjo0OTE0OTk5NjAwLCJyb2xlIjoiYW5vbiJ9.9N2FNNrBisKwF-AIj-jdeB4pGRNNBol-kXTNL3RCBFY

# Application URLs
BACKEND_URL=http://backend:8080
FRONTEND_URL=https://your-docling-domain.com

# File Upload Configuration
MAX_FILE_SIZE=52428800
PROCESSING_TIMEOUT=600

# Environment
ENVIRONMENT=production
```

#### 1.4 Configure Domain
1. **Domain Settings**
   - Frontend: `docling.your-company.com`
   - Coolify will auto-generate SSL certificates
   - Configure DNS A record to point to Coolify server

#### 1.5 Deploy Application
1. **Initial Deployment**
   - Click "Deploy"
   - Monitor build logs for successful completion
   - Verify both containers start successfully

### 2. File Structure Requirements

Ensure your repository contains these files:

```
project-root/
├── docker-compose.yml          # Main orchestration
├── backend/
│   ├── Dockerfile             # Backend container
│   └── app/
│       └── core/
│           └── config.py      # Updated for 50MB
├── frontend/
│   ├── Dockerfile             # Frontend container
│   ├── next.config.js         # Standalone output
│   └── src/
│       └── lib/
│           └── validation.ts  # 50MB validation
├── .env.coolify              # Environment template
└── .gitignore                # Docker exclusions
```

### 3. Configuration Updates

#### 3.1 Backend Configuration
Update [`backend/app/core/config.py`](backend/app/core/config.py:24):
```python
# Change from 10MB to 50MB
MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
```

#### 3.2 Frontend Validation
Update [`frontend/src/lib/validation.ts`](frontend/src/lib/validation.ts):
```typescript
// Change from 10MB to 50MB
export const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
```

#### 3.3 Next.js Configuration
Update [`frontend/next.config.js`](frontend/next.config.js):
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Add for Docker deployment
  output: 'standalone',
  
  // Increase body size limit
  experimental: {
    serverActions: {
      bodySizeLimit: '50mb'
    }
  }
}
```

### 4. Verification Steps

#### 4.1 Health Check
```bash
curl https://your-domain.com/api/health
```
Expected response:
```json
{
  "status": "ok",
  "timestamp": "2025-10-06T00:47:00Z"
}
```

#### 4.2 File Upload Test
1. Navigate to `https://your-domain.com`
2. Upload a 50MB test file
3. Verify processing completes successfully
4. Download markdown output
5. Check file size and content accuracy

#### 4.3 Container Monitoring
In Coolify dashboard:
- Check container resource usage
- Verify health checks passing
- Monitor logs for errors
- Confirm automatic restarts working

## Cost Analysis

### Coolify Deployment (Recommended)
- **Monthly Cost**: $0 (uses your infrastructure)
- **One-time Setup**: ~1.5 hours
- **Infrastructure Requirements**:
  - Disk: +10GB for file uploads
  - RAM: +3GB total (2GB backend + 1GB frontend)
  - Bandwidth: Monitor based on usage

### DigitalOcean Comparison
- **Monthly Cost**: $24
- **Setup Time**: ~2 hours
- **Managed Service**: Yes

**Monthly Savings**: $24
**ROI**: Setup time pays for itself in 1 month

## Monitoring and Maintenance

### Coolify Monitoring Features
- Real-time resource monitoring
- Log aggregation and search
- Health check status dashboard
- Automatic restarts on failure
- SSL certificate management

### Backup Strategy
- **Database**: Already handled by Supabase
- **Uploaded Files**: Mount volume `/app/uploads` to persistent storage
- **Configuration**: Version controlled in Git repository

### Maintenance Tasks
1. **Weekly**: Monitor resource usage and logs
2. **Monthly**: Review and update container images
3. **Quarterly**: Backup strategy verification
4. **As Needed**: Scale resources based on usage

## Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check logs in Coolify dashboard
# Verify environment variables
# Confirm Docker Compose syntax
```

#### File Upload Fails
```bash
# Check MAX_FILE_SIZE environment variable
# Verify backend configuration updated
# Confirm frontend validation matches
```

#### Health Check Failing
```bash
# Verify backend port 8080 accessible
# Check curl installed in container
# Confirm API health endpoint working
```

#### SSL Certificate Issues
```bash
# Verify DNS A record points to Coolify server
# Check domain configuration in Coolify
# Monitor certificate renewal logs
```

### Performance Optimization

#### Backend Optimization
- Monitor Docling processing times
- Scale CPU if processing slow
- Consider Redis cache for frequent documents

#### Frontend Optimization
- Enable CDN caching in Coolify
- Monitor bundle size
- Optimize image assets

## Migration Path from DigitalOcean

### Pre-Migration Checklist
- [ ] Backup current DigitalOcean deployment
- [ ] Export any custom configurations
- [ ] Document current environment variables
- [ ] Test local Docker Compose setup

### Migration Steps
1. **Create all new files** listed in this guide
2. **Update existing files** with 50MB limits
3. **Test locally** with `docker-compose up`
4. **Push to Git repository**
5. **Deploy via Coolify dashboard**
6. **Test deployment** with 50MB files
7. **Update DNS** to point to Coolify
8. **Decommission DigitalOcean** (save $24/month)

### Post-Migration Verification
- [ ] All file sizes upload successfully
- [ ] Processing completes within timeout
- [ ] SSL certificates working
- [ ] Monitoring and alerts configured
- [ ] Backup strategy verified

**Total migration time**: ~2-3 hours
**Monthly savings**: $24/month

## Security Considerations

### Container Security
- Use non-root users in containers
- Regular security updates
- Network isolation between containers
- Resource limits to prevent abuse

### Application Security
- Environment variables for secrets
- CORS configuration for frontend domain
- File type validation server-side
- Rate limiting on upload endpoints

### Infrastructure Security
- Regular Coolify updates
- Firewall configuration
- SSL/TLS enforcement
- Access logging and monitoring

## Support and Resources

### Documentation
- [Coolify Official Documentation](https://coolify.io/docs)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Next.js Deployment Guide](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

### Community Support
- Coolify Discord Community
- Docker Forums
- Supabase Community
- GitHub Issues for project-specific problems

---

**Deployment Guide Complete** ✅

For additional support or questions, refer to the project documentation or create an issue in the repository.