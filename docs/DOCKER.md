# Docker Setup Guide

This guide explains how to build and run the Hack Seoul API using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, but recommended)
- Environment variables set up (see below)

## Quick Start

### 1. Create Environment File

Create a `.env` file in the project root:

```bash
cat > .env << EOF
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SECRET_KEY=your_jwt_secret_key_here
EOF
```

### 2. Build and Run with Docker Compose

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The API will be available at `http://localhost:8000`

### 3. Development Mode

For development with hot reload:

```bash
docker-compose -f docker-compose.dev.yml up
```

## Manual Docker Commands

### Build the Image

```bash
docker build -t hackseoul-api .
```

### Run the Container

```bash
docker run -d \
  --name hackseoul-api \
  -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e OPENAI_API_KEY=your_key \
  -e ANTHROPIC_API_KEY=your_key \
  -e SECRET_KEY=your_secret \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/images:/app/images \
  hackseoul-api
```

## Running Migrations

The entrypoint script automatically:
1. Initializes the database on startup
2. Runs product migration if `zara_data_extended.json` exists and hasn't been migrated yet

To manually run migrations:

```bash
# Run database initialization
docker exec hackseoul-api python -c "from src.database.user_db import init_db; init_db()"

# Run product migration
docker exec hackseoul-api python migrate_products.py
```

## Data Persistence

The following directories are mounted as volumes to persist data:
- `./data` - Database and JSON files
- `./images` - Image files

Make sure these directories exist and have proper permissions.

## API Documentation

Once the container is running, access:
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## Troubleshooting

### Container won't start
- Check logs: `docker-compose logs`
- Verify environment variables are set correctly
- Ensure ports 8000 is not already in use

### Database issues
- Check that `./data` directory exists and is writable
- Verify database file permissions

### Migration issues
- Ensure `zara_data_extended.json` exists in `./data` directory
- Check container logs for migration errors

## Production Considerations

For production deployment:

1. **Security**:
   - Use Docker secrets or environment variable management
   - Change `SECRET_KEY` to a strong random value
   - Restrict CORS origins in `app.py`

2. **Performance**:
   - Use a production ASGI server like Gunicorn with Uvicorn workers
   - Consider using a PostgreSQL database instead of SQLite
   - Set up proper logging and monitoring

3. **Scaling**:
   - Use Docker Swarm or Kubernetes for orchestration
   - Set up a reverse proxy (nginx/traefik)
   - Use a shared database for multiple instances

