#!/bin/bash
# Install Autonomous Claude Code Organizer
# Auto-start on login, runs every 6 hours

set -e

CLAUDE_DIR="$HOME/.claude"
ORGANIZER_SCRIPT="$CLAUDE_DIR/autonomous_organizer.py"
PLIST_FILE="$HOME/Library/LaunchAgents/com.claude.organizer.plist"
LOG_DIR="$CLAUDE_DIR/logs"

echo "=== Installing Autonomous Claude Code Organizer ==="
echo ""

# 1. Make organizer executable
echo "1. Making organizer executable..."
chmod +x "$ORGANIZER_SCRIPT"
echo "   ✅ Executable: $ORGANIZER_SCRIPT"

# 2. Create logs directory
mkdir -p "$LOG_DIR"
echo "   ✅ Log directory: $LOG_DIR"

# 3. Create LaunchAgent plist
echo ""
echo "2. Creating LaunchAgent for auto-start..."

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.claude.organizer</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$ORGANIZER_SCRIPT</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>$LOG_DIR/organizer_stdout.log</string>

    <key>StandardErrorPath</key>
    <string>$LOG_DIR/organizer_stderr.log</string>

    <key>WorkingDirectory</key>
    <string>$CLAUDE_DIR</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>

    <key>ThrottleInterval</key>
    <integer>300</integer>
</dict>
</plist>
EOF

echo "   ✅ LaunchAgent created: $PLIST_FILE"

# 4. Load LaunchAgent
echo ""
echo "3. Loading LaunchAgent..."
launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl load "$PLIST_FILE"
echo "   ✅ LaunchAgent loaded and active"

# 5. Run initial organization
echo ""
echo "4. Running initial organization cycle..."
python3 "$ORGANIZER_SCRIPT" --once

# 6. Create management scripts
echo ""
echo "5. Creating management scripts..."

# Start script
cat > "$CLAUDE_DIR/start_organizer.sh" << 'STARTEOF'
#!/bin/bash
PLIST="$HOME/Library/LaunchAgents/com.claude.organizer.plist"
launchctl load "$PLIST"
echo "✅ Autonomous organizer started"
STARTEOF
chmod +x "$CLAUDE_DIR/start_organizer.sh"

# Stop script
cat > "$CLAUDE_DIR/stop_organizer.sh" << 'STOPEOF'
#!/bin/bash
PLIST="$HOME/Library/LaunchAgents/com.claude.organizer.plist"
launchctl unload "$PLIST"
echo "✅ Autonomous organizer stopped"
STOPEOF
chmod +x "$CLAUDE_DIR/stop_organizer.sh"

# Status script
cat > "$CLAUDE_DIR/organizer_status.sh" << 'STATUSEOF'
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
    python3 -c "
import json
with open('$STATE_FILE', 'r') as f:
    state = json.load(f)
    print(f\"  Last run: {state.get('last_run', 'Never')}\")
    print(f\"  Files cleaned: {state.get('files_cleaned', 0):,}\")
    print(f\"  Files compressed: {state.get('files_compressed', 0):,}\")
    print(f\"  Files consolidated: {state.get('files_consolidated', 0):,}\")
    space_mb = state.get('total_space_saved', 0) / 1024 / 1024
    print(f\"  Space saved: {space_mb:.2f} MB\")
"
else
    echo "No statistics available yet"
fi

echo ""

# Recent activity
if [ -f "$LOG_FILE" ]; then
    echo "Recent Activity (last 10 lines):"
    tail -10 "$LOG_FILE"
fi
STATUSEOF
chmod +x "$CLAUDE_DIR/organizer_status.sh"

echo "   ✅ Management scripts created"

# 7. Success summary
echo ""
echo "=== Installation Complete! ==="
echo ""
echo "📁 Autonomous Organizer Features:"
echo "   • Auto-cleans debug files older than 30 days"
echo "   • Compresses session history older than 7 days"
echo "   • Consolidates duplicate backups"
echo "   • Organizes documentation to docs/"
echo "   • Maintains directory index"
echo "   • Runs every 6 hours automatically"
echo ""
echo "🔧 Management Commands:"
echo "   Status:  ~/.claude/organizer_status.sh"
echo "   Stop:    ~/.claude/stop_organizer.sh"
echo "   Start:   ~/.claude/start_organizer.sh"
echo "   Logs:    tail -f ~/.claude/logs/autonomous_organizer.log"
echo ""
echo "📊 Current State:"
python3 "$CLAUDE_DIR/organizer_status.sh"
echo ""
echo "✅ System is now self-organizing!"
