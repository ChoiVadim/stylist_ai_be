#!/bin/bash
set -e

echo "Starting Hack Seoul API..."

# Ensure data directory exists
mkdir -p /app/data
mkdir -p /app/images
mkdir -p /app/logs

# Initialize database (allow failure to continue)
echo "Initializing database..."
uv run python -c "from src.database.user_db import init_db; init_db()" || echo "Warning: Database initialization failed, continuing anyway..."

# Check if products need to be migrated
if [ ! -f /app/data/.products_migrated ]; then
    echo "Checking if products need to be migrated..."
    if [ -f /app/data/zara_data_extended.json ]; then
        echo "Running product migration..."
        uv run python migrate_products.py || echo "Migration failed or already completed"
        touch /app/data/.products_migrated 2>/dev/null || true
    else
        echo "No product data file found, skipping migration"
    fi
fi

# Start the application
echo "Starting uvicorn server..."
exec "$@"

