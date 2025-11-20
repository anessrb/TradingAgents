#!/bin/bash

echo "🚀 Starting AI Scalping Trading System (Next.js)"
echo "================================================="
echo ""

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run setup first."
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Kill any existing instances
pkill -f "python3 backend.py" 2>/dev/null
pkill -f "next dev" 2>/dev/null
sleep 1

# Start backend
echo "🔧 Starting backend..."
source .venv/bin/activate
python3 backend.py &
BACKEND_PID=$!
sleep 3

if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✅ Backend started (http://localhost:8000)"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend
echo "🎨 Starting Next.js frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ System ready!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "💡 Open http://localhost:3000 in your browser"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for interruption
wait
