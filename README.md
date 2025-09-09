# GC Estimator - Frontend/Backend Architecture

This project follows Docker best practices with a clear separation between frontend (Next.js) and backend (FastAPI) services.

## Project Structure

```
GC_estimator_version1/
├── frontend/                 # Next.js application
│   ├── src/                 # Source code
│   ├── public/              # Static assets
│   ├── package.json         # Node.js dependencies
│   ├── Dockerfile           # Frontend container
│   └── .dockerignore        # Docker ignore rules
├── backend/                 # FastAPI application
│   ├── main.py             # FastAPI entry point
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Backend container
│   └── .dockerignore       # Docker ignore rules
├── docker-compose.yml       # Multi-service orchestration
└── README.md               # This file
```

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- Git

### Running the Application

1. **Clone and navigate to the project:**
   ```bash
   cd GC_estimator_version1
   ```

2. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development Mode

For development with hot reloading:

```bash
# Start services in development mode (uses override file automatically)
make dev
# or
docker-compose up --build
```

**Hot Reloading Features:**
- **Frontend**: Next.js dev server with live code changes
- **Backend**: FastAPI auto-reload on Python file changes
- **Volume Mounts**: Source code mounted for immediate updates
- **Efficient Dev Loop**: Changes appear instantly without rebuilding

### Stopping the Application

```bash
docker-compose down
```

## Individual Service Management

### Backend Service
```bash
# Build backend only
docker-compose build backend

# Run backend only
docker-compose up backend

# View backend logs
docker-compose logs backend
```

### Frontend Service
```bash
# Build frontend only
docker-compose build frontend

# Run frontend only
docker-compose up frontend

# View frontend logs
docker-compose logs frontend
```

## Development Without Docker

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## Docker Best Practices Implemented

1. **Single Responsibility**: Each container does one thing well
   - Frontend container serves the Next.js application
   - Backend container runs the FastAPI API

2. **Multi-stage Builds**: Frontend uses multi-stage build for optimization
   - Reduces final image size
   - Separates build dependencies from runtime

3. **Security**: 
   - Non-root users in both containers
   - Minimal base images (alpine for frontend, slim for backend)

4. **Health Checks**: Backend includes health check endpoint
   - Frontend waits for backend to be healthy before starting

5. **Environment Configuration**: 
   - Environment variables for service communication
   - CORS configuration for cross-origin requests

6. **Volume Management**: 
   - Development volumes for hot reloading
   - Named volumes for persistent data

## API Endpoints

The backend provides the following main endpoints:
- `GET /health` - Health check
- `POST /estimates` - Create new estimate
- `GET /estimates/{id}` - Get estimate by ID
- `PUT /estimates/{id}` - Update estimate
- `DELETE /estimates/{id}` - Delete estimate

## Environment Variables

### Backend
- `ENVIRONMENT`: Set to 'production' or 'development'
- `CORS_ORIGINS`: Comma-separated list of allowed origins

### Frontend
- `NODE_ENV`: Set to 'production' or 'development'
- `NEXT_PUBLIC_API_URL`: Backend API URL

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000 and 8000 are available
2. **Build failures**: Check Docker logs with `docker-compose logs`
3. **CORS errors**: Verify CORS_ORIGINS environment variable
4. **Health check failures**: Ensure backend is properly starting

### Useful Commands

```bash
# View all logs
docker-compose logs

# Rebuild without cache
docker-compose build --no-cache

# Remove all containers and volumes
docker-compose down -v

# Check container status
docker-compose ps
```

## Contributing

1. Make changes in the appropriate service directory
2. Test locally with Docker Compose
3. Ensure both services start correctly
4. Update documentation as needed

## License

[Add your license information here]
