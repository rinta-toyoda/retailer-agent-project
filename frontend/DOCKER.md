# Docker Setup for Frontend

This document explains how to run the Next.js frontend using Docker in both development and production modes.

## Development Mode

### Using Docker Compose (Recommended)

From the project root directory:

```bash
# Start all services (database, backend, frontend)
task dev

# Or manually:
docker-compose up --build
```

The frontend will be available at http://localhost:3000

### Using Docker Only

```bash
# Build the development image
docker build -t retailer-frontend:dev -f Dockerfile .

# Run the container
docker run -p 3000:3000 \
  -v $(pwd):/app \
  -v /app/node_modules \
  -e NEXT_PUBLIC_API_URL=http://localhost:8100 \
  retailer-frontend:dev
```

### Development Features

- **Hot Reload**: Code changes automatically reload
- **Volume Mounting**: Local files sync with container
- **Node Modules**: Isolated in container for consistency
- **Environment Variables**: Set via docker-compose or -e flag

## Production Mode

### Build Production Image

```bash
docker build -t retailer-frontend:prod \
  -f Dockerfile.prod \
  --build-arg NEXT_PUBLIC_API_URL=https://api.yourdomain.com \
  .
```

### Run Production Container

```bash
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://api.yourdomain.com \
  retailer-frontend:prod
```

### Production Features

- **Multi-stage Build**: Optimized image size (~150MB vs ~1GB)
- **Standalone Output**: Self-contained server bundle
- **Non-root User**: Runs as 'nextjs' user for security
- **Static Asset Optimization**: Pre-built static files
- **No Dev Dependencies**: Only production modules included

## Docker Files Explained

### `Dockerfile` (Development)

Simple development setup:
- Base: `node:20-alpine` (~150MB)
- Installs all dependencies including devDependencies
- Copies source code
- Runs `npm run dev` with hot reload

### `Dockerfile.prod` (Production)

Multi-stage optimized build:
1. **deps**: Install dependencies only
2. **builder**: Build Next.js application
3. **runner**: Minimal runtime image
   - Only includes built artifacts
   - Runs as non-root user
   - Uses standalone output

### `.dockerignore`

Excludes from Docker builds:
- `node_modules` (rebuilt in container)
- `.next` (rebuilt in container)
- Development files (*.md, .env.local)
- Git metadata

## Environment Variables

### Required

- `NEXT_PUBLIC_API_URL`: Backend API URL
  - Development: `http://localhost:8100`
  - Production: `https://api.yourdomain.com`

### Optional

- `PORT`: Server port (default: 3000)
- `NODE_ENV`: Environment (development/production)
- `NEXT_TELEMETRY_DISABLED`: Disable Next.js telemetry (1/0)

## Docker Compose Configuration

Located in project root `docker-compose.yml`:

```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
  ports:
    - "3000:3000"
  volumes:
    - ./frontend:/app
    - /app/node_modules
    - /app/.next
  environment:
    - NEXT_PUBLIC_API_URL=http://localhost:8100
  depends_on:
    - backend
```

### Volume Mounts

- `./frontend:/app`: Sync local code with container
- `/app/node_modules`: Persist node_modules in container
- `/app/.next`: Persist build cache for faster rebuilds

## Troubleshooting

### Port Already in Use

```bash
# Change port mapping
docker run -p 3001:3000 retailer-frontend:dev
```

Or update docker-compose.yml:
```yaml
ports:
  - "3001:3000"
```

### Build Fails

```bash
# Clear Docker cache
docker builder prune -a

# Rebuild without cache
docker-compose build --no-cache frontend
```

### Container Won't Start

```bash
# Check logs
docker logs retailer_frontend

# Interactive shell
docker exec -it retailer_frontend sh
```

### Hot Reload Not Working

Ensure volume mounts are correct in docker-compose.yml:
```yaml
volumes:
  - ./frontend:/app
  - /app/node_modules
```

### Environment Variables Not Working

Restart container after changing variables:
```bash
docker-compose down
docker-compose up --build
```

## Performance Optimization

### Development

1. **Use BuildKit**:
   ```bash
   export DOCKER_BUILDKIT=1
   docker-compose build
   ```

2. **Persistent Node Modules**:
   Already configured in docker-compose.yml

3. **Use .dockerignore**:
   Reduces build context size

### Production

1. **Multi-stage Build**:
   Reduces final image size to ~150MB

2. **Standalone Output**:
   Self-contained, no external dependencies

3. **Alpine Base**:
   Smaller base image than full Node

## Security Best Practices

### Implemented

- Non-root user (nextjs:1001)
- Minimal base image (alpine)
- No dev dependencies in production
- Environment variable validation
- .dockerignore to prevent leaks

### Recommended Additions

- [ ] Use secrets for sensitive data
- [ ] Scan images with `docker scan`
- [ ] Pin specific Node version
- [ ] Use distroless base for production

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Frontend

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: |
          docker build -t retailer-frontend:latest \
            -f frontend/Dockerfile.prod \
            --build-arg NEXT_PUBLIC_API_URL=${{ secrets.API_URL }} \
            frontend/

      - name: Push to registry
        run: docker push retailer-frontend:latest
```

## Container Registry

### Tag and Push

```bash
# Tag for registry
docker tag retailer-frontend:prod your-registry.com/retailer-frontend:v1.0.0

# Push to registry
docker push your-registry.com/retailer-frontend:v1.0.0
```

### Pull and Run

```bash
# Pull from registry
docker pull your-registry.com/retailer-frontend:v1.0.0

# Run
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://api.yourdomain.com \
  your-registry.com/retailer-frontend:v1.0.0
```

## Monitoring in Docker

### Health Check

Add to Dockerfile:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD node -e "require('http').get('http://localhost:3000', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"
```

### Resource Limits

```bash
docker run -p 3000:3000 \
  --memory=512m \
  --cpus=1 \
  retailer-frontend:prod
```

### Logs

```bash
# View logs
docker logs retailer_frontend

# Follow logs
docker logs -f retailer_frontend

# Last 100 lines
docker logs --tail 100 retailer_frontend
```

## Cleanup

### Remove Containers

```bash
# Stop and remove
docker-compose down

# Remove with volumes
docker-compose down -v
```

### Remove Images

```bash
# List images
docker images | grep retailer-frontend

# Remove specific image
docker rmi retailer-frontend:dev

# Remove all unused images
docker image prune -a
```

## Quick Reference

### Common Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f frontend

# Restart frontend
docker-compose restart frontend

# Rebuild frontend
docker-compose build frontend

# Shell access
docker-compose exec frontend sh

# Stop all
docker-compose down
```

### Image Sizes

- Development: ~1.2GB (includes dev dependencies)
- Production: ~150MB (standalone optimized)
- Base Alpine: ~50MB

### Build Times

- First build: ~2-5 minutes
- Cached rebuild: ~30 seconds
- Production build: ~3-7 minutes

## Production Deployment

### AWS ECS Example

```bash
# Build for ECS
docker build -t retailer-frontend:prod \
  -f Dockerfile.prod \
  --build-arg NEXT_PUBLIC_API_URL=https://api.yourdomain.com \
  .

# Tag for ECR
docker tag retailer-frontend:prod \
  123456789.dkr.ecr.us-east-1.amazonaws.com/retailer-frontend:latest

# Push to ECR
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/retailer-frontend:latest
```

### Kubernetes Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: retailer-frontend
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: frontend
        image: retailer-frontend:prod
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "https://api.yourdomain.com"
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## Support

For Docker-related issues:
1. Check container logs: `docker logs retailer_frontend`
2. Verify environment variables: `docker exec retailer_frontend env`
3. Check running processes: `docker exec retailer_frontend ps aux`
4. Test connectivity: `docker exec retailer_frontend wget -O- http://localhost:3000`
