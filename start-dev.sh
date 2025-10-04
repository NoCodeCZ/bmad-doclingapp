#!/bin/bash

echo "🚀 Starting Workshop Document Processor..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 20+ first."
    exit 1
fi

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'.' -f1 | cut -d'v' -f2)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo "❌ Node.js version 20+ required. Current version: $(node -v)"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo "❌ Python 3.11+ required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Node.js $(node -v) detected"
echo "✅ Python $PYTHON_VERSION detected"

# Install root dependencies
echo "📦 Installing root dependencies..."
npm install

# Install backend dependencies
echo "🐍 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "⚛️ Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo ""
echo "🎉 All dependencies installed!"
echo ""
echo "To start the application:"
echo "1. Terminal 1 - Start backend:"
echo "   cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2. Terminal 2 - Start frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "📖 API Documentation: http://localhost:8000/docs"