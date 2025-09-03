# GC Estimator API - Docker Setup

This directory contains the containerized FastAPI application for the GC Estimator.

## 🐳 Docker Configuration

### Files
- `Dockerfile` - Production-optimized container
- `Dockerfile.dev` - Development container with hot reload
- `docker-compose.yml` - Production compose configuration
- `docker-compose.dev.yml` - Development compose with volume mounting
- `.dockerignore` - Build optimization exclusions

### Build & Run Commands

#### Production Mode
```bash
# Build from project root
docker build -f api/Dockerfile -t gc-estimator-api .

# Run standalone
docker run -p 8000:8000 gc-estimator-api

# Run with docker-compose (from api/ directory)
cd api && docker-compose up
```

#### Development Mode (with hot reload)
```bash
# Run with docker-compose dev config
cd api && docker-compose -f docker-compose.dev.yml up
```

### API Endpoints

- `GET /` - Root endpoint with version info
- `GET /health` - Health check endpoint
- `GET /api/estimates` - List all estimates
- `POST /api/estimates` - Create new estimate
- `POST /api/estimates/import` - Import QTO Excel/CSV files
- `GET /api/estimates/{id}` - Get specific estimate
- `PUT /api/estimates/{id}` - Update estimate
- `DELETE /api/estimates/{id}` - Delete estimate
- `GET /api/estimates/{id}/rollup` - Get cost rollup calculations

### Environment Variables

- `CORS_ORIGINS` - Comma-separated list of allowed origins (default: `http://localhost:3000,http://127.0.0.1:3000`)
- `PYTHONPATH` - Set to `/app` for proper module imports

### Features

- **Python 3.10** - Matches project requirements
- **Production Ready** - No reload flag, optimized copying
- **Security** - Non-root user execution
- **Health Monitoring** - Built-in health checks
- **Excel Support** - Includes openpyxl for XLSX files
- **CORS Configured** - Ready for frontend integration

### Deployment

The container is optimized for deployment platforms like Fly.io, Railway, or any Docker-compatible hosting service.
