#!/bin/bash
# Start Autonomous Team Monitor
# Similar to autonomous_monitor.py for services

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$HOME/.claude/logs/team_monitor.pid"
LOG_FILE="$HOME/.claude/logs/autonomous_teams_monitor.log"

# Create logs directory
mkdir -p "$HOME/.claude/logs"

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "Team monitor already running (PID: $OLD_PID)"
        exit 0
    else
        echo "Removing stale PID file"
        rm "$PID_FILE"
    fi
fi

# Start monitor in background
echo "Starting Autonomous Team Monitor..."
nohup python3 "$SCRIPT_DIR/team_monitor.py" >> "$LOG_FILE" 2>&1 &
MONITOR_PID=$!

# Save PID
echo "$MONITOR_PID" > "$PID_FILE"

echo "✅ Team monitor started (PID: $MONITOR_PID)"
echo "📋 View logs: tail -f $LOG_FILE"
echo "🛑 Stop: kill $MONITOR_PID"
