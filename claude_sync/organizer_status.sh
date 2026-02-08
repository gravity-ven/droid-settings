#!/bin/bash
CLAUDE_DIR="$HOME/.claude"
STATE_FILE="$CLAUDE_DIR/state/organizer_state.json"
LOG_FILE="$CLAUDE_DIR/logs/autonomous_organizer.log"
PID_FILE="$CLAUDE_DIR/logs/organizer.pid"

echo "=== Autonomous Organizer Status ==="
echo ""

# Check if running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Status: ✅ Running (PID: $PID)"
    else
        echo "Status: ⚠️  Stopped (stale PID file)"
    fi
else
    echo "Status: ❌ Not running"
fi

echo ""

# Show stats
if [ -f "$STATE_FILE" ]; then
    echo "Lifetime Statistics:"
    python3 << PYEOF
import json
with open('$STATE_FILE', 'r') as f:
    state = json.load(f)
    print(f"  Last run: {state.get('last_run', 'Never')}")
    print(f"  Files cleaned: {state.get('files_cleaned', 0):,}")
    print(f"  Files compressed: {state.get('files_compressed', 0):,}")
    print(f"  Files consolidated: {state.get('files_consolidated', 0):,}")
    space_mb = state.get('total_space_saved', 0) / 1024 / 1024
    print(f"  Space saved: {space_mb:.2f} MB")
PYEOF
else
    echo "No statistics available yet"
fi

echo ""

# Recent activity
if [ -f "$LOG_FILE" ]; then
    echo "Recent Activity (last 10 lines):"
    tail -10 "$LOG_FILE"
fi
