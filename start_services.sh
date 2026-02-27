# ... 前面部分 ...
echo "🚀 Starting Paper Servant Services..."

# 0. Initialization
echo "------------------------------------------------"
echo "🔍 Initializing environment..."

# Sync Backend Dependencies
echo "📦 Syncing backend dependencies (uv sync)..."
uv sync

# Install Frontend Dependencies if node_modules missing
if [ ! -d "agent-ui-frontend/node_modules" ]; then
    echo "🎨 Installing frontend dependencies (npm install)..."
    cd agent-ui-frontend && npm install && cd ..
fi

# 1. Start Backend (AgentOS)
# ... 后面部分 ...