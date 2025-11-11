#!/bin/bash
# Quick start script

echo "🚀 Starting Sales CRM..."
echo ""
echo "Make sure Docker Desktop is running!"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

echo "Starting services with Docker Compose..."
docker-compose up --build

