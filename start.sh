#!/bin/bash

echo "🤖 Starting AI Trading Agent System..."
echo ""

# Check if dependencies are installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo "Please add your Mistral API key to .env"
fi

echo ""
echo "Starting backend on http://localhost:8000"
echo "Starting dashboard on http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Start backend in background
python backend.py &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start dashboard (this will be in foreground)
streamlit run dashboard.py

# When streamlit is closed, kill backend
kill $BACKEND_PID 2>/dev/null
