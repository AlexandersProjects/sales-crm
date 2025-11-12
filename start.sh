#!/bin/bash
# Sales CRM - Complete Start Script (Linux/Mac)
# Handles Docker cleanup, build, and startup

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              🚀 Sales CRM - Starting Up 🚀                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "💡 To use AI features, edit .env and add your OpenAI API key"
    echo ""
fi

# Check Docker
echo "🐳 Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker and try again."
    echo ""
    exit 1
fi
echo "✅ Docker is running"
echo ""

# Ask user what to do
echo "Choose startup mode:"
echo "  1. Quick start (restart existing containers)"
echo "  2. Clean rebuild (recommended for first time or after changes)"
echo "  3. Reset everything (removes database data)"
echo ""
read -p "Enter choice (1-3, default: 1): " choice
choice=${choice:-1}

case $choice in
    1)
        echo ""
        echo "🚀 Quick start mode..."
        echo ""
        docker-compose up -d
        ;;
    2)
        echo ""
        echo "🔨 Clean rebuild mode..."
        echo ""
        echo "Stopping containers..."
        docker-compose down

        echo "Building fresh images..."
        docker-compose build --no-cache

        echo "Starting services..."
        docker-compose up -d
        ;;
    3)
        echo ""
        echo "⚠️  RESET MODE - This will delete all data!"
        echo ""
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo "Stopping and removing everything..."
            docker-compose down -v

            echo "Rebuilding..."
            docker-compose build --no-cache

            echo "Starting fresh..."
            docker-compose up -d
        else
            echo "Cancelled."
            echo ""
            exit 0
        fi
        ;;
    *)
        echo "Invalid choice. Defaulting to quick start..."
        echo ""
        docker-compose up -d
        ;;
esac

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check if services are running
echo ""
echo "📊 Service Status:"
docker-compose ps

# Display access URLs
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  ✅ Sales CRM Ready! ✅                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

echo "🌐 Access your application:"
echo "   • Frontend:  http://localhost:5173"
echo "   • API Docs:  http://localhost:8000/docs"
echo "   • Backend:   http://localhost:8000"
echo ""

echo "📋 Useful commands:"
echo "   • View logs:     docker-compose logs -f"
echo "   • Stop services: docker-compose down"
echo "   • Restart:       docker-compose restart"
echo "   • Check DB:      python check_database.py"
echo ""

echo "🎉 Happy coding!"
echo ""

