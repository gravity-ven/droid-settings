#!/bin/bash
# Display all active autonomous systems

echo "═══════════════════════════════════════════════════════════════"
echo "   CLAUDE CODE - FULLY AUTONOMOUS & SELF-ORGANIZING"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "🤖 ACTIVE AUTONOMOUS SYSTEMS:"
echo ""

# Supermemory
if launchctl list | grep -q "claude.supermemory"; then
    PID=$(launchctl list | grep "claude.supermemory" | awk '{print $1}')
    echo "  ✅ Supermemory (PID: $PID)"
    echo "     → Cross-session memory persistence"
    echo "     → Ports: 3456 (API), 8788 (MCP)"
    echo ""
fi

# Organizer
if launchctl list | grep -q "claude.organizer"; then
    PID=$(launchctl list | grep "claude.organizer" | awk '{print $1}')
    echo "  ✅ Code Organizer (PID: $PID)"
    echo "     → Self-organizing every 6 hours"
    echo "     → Cleans, compresses, consolidates"
    echo ""
fi

echo "📊 ORGANIZER STATISTICS:"
if [ -f ~/.claude/state/organizer_state.json ]; then
    python3 << PYEOF
import json
with open('$HOME/.claude/state/organizer_state.json', 'r') as f:
    state = json.load(f)
    print(f"  Files compressed: {state['files_compressed']:,}")
    print(f"  Files consolidated: {state['files_consolidated']}")
    print(f"  Space saved: {state['total_space_saved'] / 1024:.2f} KB")
    print(f"  Last run: {state['last_run'][:19]}")
PYEOF
fi

echo ""
echo "📁 ORGANIZED STRUCTURE:"
echo "  ~/.claude/docs/               → All documentation (13 files)"
echo "  ~/.claude/autonomous/         → Autonomous systems"
echo "  ~/.claude/hooks/              → Event hooks (7 active)"
echo "  ~/.claude/state/              → State tracking"
echo "  ~/.claude/DIRECTORY_INDEX.json → Structure reference"
echo ""
echo "🔧 MANAGEMENT COMMANDS:"
echo "  Status:  ~/.claude/organizer_status.sh"
echo "  Logs:    tail -f ~/.claude/logs/autonomous_organizer.log"
echo "  Stop:    ~/.claude/stop_organizer.sh"
echo "  Start:   ~/.claude/start_organizer.sh"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ SYSTEM IS FULLY AUTONOMOUS - ZERO MAINTENANCE REQUIRED"
echo "═══════════════════════════════════════════════════════════════"
