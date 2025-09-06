#!/bin/bash

echo "Testing development setup..."

# Stop any existing containers
echo "Stopping existing containers..."
docker compose down

# Start development environment
echo "Starting development environment..."
make dev

# Wait a bit for services to start
echo "Waiting for services to start..."
sleep 10

# Test server health
echo "Testing server health..."
curl -f http://localhost:8000/health || echo "Server health check failed"

# Test webapp
echo "Testing webapp..."
curl -f http://localhost:3000 || echo "Webapp check failed"

echo "Development setup test complete!"
