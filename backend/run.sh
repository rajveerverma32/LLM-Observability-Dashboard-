#!/bin/bash

# LLM Observability Backend Startup Script

echo "🚀 LLM Observability Dashboard - Backend Startup"
echo "================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✓ Python version: $(python3 --version)"

# Check if requirements are installed
echo "📦 Checking dependencies..."
pip install -r requirements.txt --quiet

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Start the server
echo ""
echo "🎯 Starting FastAPI server..."
echo "📍 API will be available at: http://localhost:8000"
echo "📖 Documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py
