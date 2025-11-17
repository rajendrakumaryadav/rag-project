#!/bin/bash
# Database migration script for LLM-PKG

set -e

echo "Running database migrations..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL environment variable is not set"
    echo "Please set it to your PostgreSQL connection string"
    exit 1
fi

# Run Alembic migrations
alembic upgrade head

echo "Database migrations completed successfully!"