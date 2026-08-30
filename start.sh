#!/bin/bash

# Optimize memory usage for Render's 512MB limit by restricting PyTorch threads
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export MALLOC_ARENA_MAX=2

# Seed the local Qdrant database
echo "Seeding Qdrant Vector Database..."
python seed_lore.py

# Start Celery worker in the background
echo "Starting Celery worker..."
celery -A app.worker.celery_app worker --loglevel=info --pool=solo &

# Start Uvicorn in the foreground
echo "Starting Uvicorn web server..."
# Render provides the port in the $PORT environment variable
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
