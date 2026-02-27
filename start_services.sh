#!/bin/bash

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n🛑 Stopping services..."
    # Kill all child processes in the current process group
    kill $(jobs -p) 2>/dev/null
    exit
}

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

echo "🚀 Starting Paper Servent Services..."

# 1. Start Backend (AgentOS)
echo "------------------------------------------------"
echo "📦 Starting Backend (AgentOS) on port 7777..."
uv run playground.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# 2. Start Frontend (Next.js)
echo "------------------------------------------------"
echo "🎨 Starting Frontend (Next.js) on port 3000..."
cd agent-ui-frontend
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "   Frontend PID: $FRONTEND_PID"

# 3. Wait for services to initialize
echo "------------------------------------------------"
echo "⏳ Waiting 5 seconds for services to initialize..."
sleep 5

# 4. Open in Microsoft Edge (or default fallback)
TARGET_URL="http://localhost:3000"
echo "------------------------------------------------"
echo "🌐 Opening $TARGET_URL..."

if open -a "Microsoft Edge" "$TARGET_URL" 2>/dev/null; then
    echo "   ✅ Opened in Microsoft Edge."
else
    echo "   ⚠️  Microsoft Edge not found. Opening in default browser..."
    open "$TARGET_URL"
fi

echo "------------------------------------------------"
echo "✅ Services are running!"
echo "   - Backend logs: ./backend.log"
echo "   - Frontend logs: ./agent-ui-frontend/frontend.log"
echo "   - Press Ctrl+C to stop all services."
echo "------------------------------------------------"

# Wait indefinitely to keep the script running
wait
