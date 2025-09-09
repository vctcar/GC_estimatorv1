# GC Estimator - Optimization & Monitoring Guide

## 🚀 Deployed Applications
- **Frontend**: https://frontend-green-flower-3817.fly.dev/
- **Backend API**: https://api-dark-flower-4953.fly.dev/

## 📊 1. Monitoring Resource Usage

### Check Application Status
```bash
# Check frontend status
flyctl status -a frontend-green-flower-3817

# Check backend API status  
flyctl status -a api-dark-flower-4953
```

### Monitor Logs
```bash
# Frontend logs (real-time)
flyctl logs -a frontend-green-flower-3817

# Backend API logs (real-time)
flyctl logs -a api-dark-flower-4953

# Get specific number of log lines
flyctl logs -a frontend-green-flower-3817 --lines 100
```

### Resource Monitoring
```bash
# Check machine details and resource usage
flyctl machine list -a frontend-green-flower-3817
flyctl machine list -a api-dark-flower-4953

# Get detailed machine info
flyctl machine status <machine-id> -a <app-name>
```

## ⚡ 2. Performance Optimizations

### Current Build Configuration
- ✅ **Next.js 14.2.5** with stable Webpack (no Turbopack issues)
- ✅ **Standalone output** for minimal Docker images
- ✅ **Multi-stage builds** for optimal performance

### Alternative Build Options (if needed)
```json
// package.json - Alternative scripts if you need them
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "build:webpack": "next build --no-turbo",
    "build:turbo": "next build --turbo",
    "start": "next start"
  }
}
```

### Memory Scaling (if needed)
```bash
# Scale frontend memory if needed
flyctl scale memory 512 -a frontend-green-flower-3817

# Scale backend memory if needed  
flyctl scale memory 512 -a api-dark-flower-4953

# Check current scaling
flyctl scale show -a frontend-green-flower-3817
```

## 🐳 3. Local Docker Development (Optional)

### Optimized docker-compose.yml for Local Development
```yaml
# docker-compose.local.yml
services:
  api:
    build:
      context: ./api
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
    depends_on:
      - api
    volumes:
      - ./frontend:/app
      - /app/node_modules
```

### Run Local Development
```bash
# Run locally with hot reload
docker-compose -f docker-compose.local.yml up

# Build without cache if needed
docker-compose -f docker-compose.local.yml build --no-cache
```

## 🌐 4. Fly.io Private Networking

### Current Setup
- ✅ **Both apps in same region**: `lax` (Los Angeles)
- ✅ **Private networking**: Automatic 6PN IPv6 network
- ✅ **Internal DNS**: Frontend connects to backend via Fly's internal DNS
- ✅ **Environment variable**: `NEXT_PUBLIC_API_URL="https://api-dark-flower-4953.fly.dev"`

### Networking Commands
```bash
# Check app networking
flyctl ips list -a frontend-green-flower-3817
flyctl ips list -a api-dark-flower-4953

# Test internal connectivity (from frontend machine)
flyctl ssh console -a frontend-green-flower-3817
# Then inside the machine:
# curl https://api-dark-flower-4953.fly.dev/health
```

## 💾 5. Data Persistence

### Current State
- ⚠️ **In-memory storage**: Data resets on deployment/restart
- ✅ **Suitable for MVP**: Perfect for testing and demos

### Future Persistence Options
```bash
# Create volume for data persistence (future enhancement)
flyctl volumes create data --region lax --size 1 -a api-dark-flower-4953

# Update fly.toml to mount volume
[mounts]
  source = "data"
  destination = "/app/data"
```

## 💰 6. Cost Optimization

### Check Usage and Costs
```bash
# Check current usage
flyctl dashboard billing

# Check app resource usage
flyctl machine list -a frontend-green-flower-3817 --json
flyctl machine list -a api-dark-flower-4953 --json
```

### Auto-scaling Configuration
```toml
# Both apps configured for cost efficiency:
[http_service]
  auto_stop_machines = 'stop'    # Stop when idle
  auto_start_machines = true     # Start on request
  min_machines_running = 0       # No always-on machines
```

### Suspend Apps When Not Needed
```bash
# Suspend apps to save costs (stops all machines)
flyctl scale count 0 -a frontend-green-flower-3817
flyctl scale count 0 -a api-dark-flower-4953

# Resume apps
flyctl scale count 1 -a frontend-green-flower-3817
flyctl scale count 1 -a api-dark-flower-4953
```

### Destroy Apps (if completely done)
```bash
# ⚠️ CAUTION: This permanently deletes the apps
flyctl apps destroy frontend-green-flower-3817
flyctl apps destroy api-dark-flower-4953
```

## 🔧 7. Troubleshooting Commands

### Health Checks
```bash
# Test endpoints directly
curl https://frontend-green-flower-3817.fly.dev/
curl https://api-dark-flower-4953.fly.dev/health

# Check if machines are running
flyctl machine list -a frontend-green-flower-3817
flyctl machine list -a api-dark-flower-4953
```

### Restart Applications
```bash
# Restart frontend
flyctl machine restart -a frontend-green-flower-3817

# Restart backend
flyctl machine restart -a api-dark-flower-4953
```

### Debug Build Issues
```bash
# Check build logs
flyctl logs -a frontend-green-flower-3817 --lines 200

# SSH into machine for debugging
flyctl ssh console -a frontend-green-flower-3817
```

## 📈 8. Performance Monitoring

### Key Metrics to Watch
- **Response times**: Should be < 2s for cold starts
- **Memory usage**: Should stay under allocated limits
- **Build times**: Frontend ~60s, Backend ~60s
- **Auto-scaling**: Machines should stop/start properly

### Alerts and Monitoring
```bash
# Set up alerts (future enhancement)
# Fly.io supports webhook notifications for machine events
```

## 🎯 Best Practices

1. **Monitor regularly** but don't over-optimize prematurely
2. **Use auto-scaling** to minimize costs
3. **Keep builds efficient** with proper .dockerignore
4. **Test connectivity** between services periodically
5. **Scale up only when needed** based on actual usage
6. **Use logs** for debugging rather than local development

## 🚀 Quick Commands Reference

```bash
# Daily monitoring
flyctl status -a frontend-green-flower-3817
flyctl status -a api-dark-flower-4953

# Check logs if issues
flyctl logs -a frontend-green-flower-3817 --lines 50

# Test functionality
curl https://frontend-green-flower-3817.fly.dev/api/estimates

# Scale if needed
flyctl scale memory 512 -a frontend-green-flower-3817
```
