#!/bin/bash

# Seed the local Qdrant database
echo "Seeding Qdrant Vector Database..."
python seed_lore.py

# Start Celery worker in the background
echo "Starting Celery worker..."
celery -A app.worker.celery_app worker --loglevel=info &

# Start Uvicorn in the foreground
echo "Starting Uvicorn web server..."
# Render provides the port in the $PORT environment variable
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
