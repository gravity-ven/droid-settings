#!/bin/bash
# Setup Supermemory Local with Cross-Session Memory

set -e

echo "🧠 Setting up Supermemory Local with Cross-Session Memory"
echo "=========================================================="
echo ""

# Check PostgreSQL
echo "1. Checking PostgreSQL..."
PSQL_BIN="/opt/homebrew/Cellar/postgresql@16/16.10_1/bin/psql"
if ! brew services list | grep -q "postgresql.*started"; then
    echo "   Starting PostgreSQL..."
    brew services start postgresql@16
    sleep 2
fi
echo "   ✅ PostgreSQL running"

# Create database
echo ""
echo "2. Creating supermemory_local database..."
$PSQL_BIN -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'supermemory_local'" | grep -q 1 || \
$PSQL_BIN -U postgres -c "CREATE DATABASE supermemory_local;"
echo "   ✅ Database ready"

# Install dependencies
echo ""
echo "3. Checking Node dependencies..."
cd ~/supermemory-local
if [ ! -d "node_modules" ]; then
    echo "   Installing pg module..."
    npm install pg
fi
echo "   ✅ Dependencies installed"

# Start supermemory server in background
echo ""
echo "4. Starting Supermemory servers..."
# Kill existing instances
lsof -ti :3456 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti :8788 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 1

# Start server in background
nohup node ~/supermemory-local/simple-memory-server.js > ~/.claude/logs/supermemory.log 2>&1 &
sleep 2

# Check if running
if lsof -i :3456 >/dev/null 2>&1; then
    echo "   ✅ API Server: http://localhost:3456"
else
    echo "   ❌ API Server failed to start"
    cat ~/.claude/logs/supermemory.log
    exit 1
fi

if lsof -i :8788 >/dev/null 2>&1; then
    echo "   ✅ MCP Server: http://localhost:8788"
else
    echo "   ❌ MCP Server failed to start"
    exit 1
fi

echo ""
echo "5. Testing endpoints..."
HEALTH=$(curl -s http://localhost:3456/health)
if echo "$HEALTH" | grep -q '"status":"ok"'; then
    echo "   ✅ Health check passed"
else
    echo "   ❌ Health check failed"
    exit 1
fi

echo ""
echo "✅ Supermemory Local is ready!"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code to activate hooks"
echo "  2. Memories will persist across all sessions"
echo "  3. Check logs: tail -f ~/.claude/logs/supermemory.log"
echo ""
