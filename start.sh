#!/bin/bash

echo "🤖 AI Trading Agent System"
echo "=========================="
echo ""

# Check if dependencies are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  Dependencies not installed. Installing..."
    pip3 install -r requirements.txt
    echo "✅ Dependencies installed!"
else
    echo "✅ Dependencies OK"
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  Please add your Mistral API key to .env"
else
    echo "✅ .env file found"
fi

echo ""
echo "🚀 Starting servers..."
echo "   Backend:   http://localhost:8000"
echo "   Dashboard: http://localhost:8501"
echo ""
echo "💡 Tip: Watch this terminal to see AI thinking!"
echo "📊 Note: Click 'Load Chart' button in Charts tab"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    pkill -P $$ 2>/dev/null
    echo "✅ Stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Kill any existing instances
pkill -f "python3 backend.py" 2>/dev/null
pkill -f "streamlit run dashboard.py" 2>/dev/null
sleep 1

# Start backend in background
python3 backend.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Check if backend started successfully
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✅ Backend started (PID: $BACKEND_PID)"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start dashboard (this will be in foreground)
streamlit run dashboard.py

# When streamlit is closed, cleanup
cleanup
