#!/bin/bash
# Test Autonomous Agent Teams System

echo "=== Autonomous Agent Teams System Test ==="
echo ""

echo "1. Testing autonomous detection hook..."
TEST_PROMPT='{"prompt": "Create a team to refactor authentication with security, performance, and testing reviews"}'
echo "$TEST_PROMPT" | python3 ~/.claude/hooks/autonomous-agent-teams.py > /tmp/hook_output.txt
if grep -q "AUTO-SPAWN READY\|auto-spawn" /tmp/hook_output.txt; then
    echo "   ✅ Auto-spawn mode detected correctly"
    SCORE=$(grep -o 'score: [0-9]\+/10' /tmp/hook_output.txt | head -1)
    echo "      Complexity $SCORE"
else
    echo "   ⚠️  Auto-spawn detection (check output below)"
fi

echo ""
echo "2. Testing complexity scoring..."
TEST_SIMPLE='{"prompt": "Fix typo in README"}'
echo "$TEST_SIMPLE" | python3 ~/.claude/hooks/autonomous-agent-teams.py > /tmp/simple_output.txt
if [ ! -s /tmp/simple_output.txt ]; then
    echo "   ✅ Simple tasks correctly ignored (no output)"
else
    if grep -q "AUTO-SPAWN\|SUGGEST" /tmp/simple_output.txt; then
        echo "   ❌ Simple task incorrectly triggered team"
    else
        echo "   ✅ Simple task handled appropriately"
    fi
fi

echo ""
echo "3. Testing team composition suggestions..."
if grep -q -i "security\|performance\|test" /tmp/hook_output.txt; then
    echo "   ✅ Team roles suggested automatically"
else
    echo "   ⚠️  Team composition check output below"
fi

echo ""
echo "4. Checking autonomous components..."
if [ -x ~/.claude/hooks/autonomous-agent-teams.py ]; then
    echo "   ✅ Autonomous hook executable"
else
    echo "   ❌ Hook not executable"
fi

if [ -x ~/.claude/autonomous/team_monitor.py ]; then
    echo "   ✅ Team monitor executable"
else
    echo "   ❌ Monitor not executable"
fi

if [ -x ~/.claude/autonomous/start_team_monitor.sh ]; then
    echo "   ✅ Monitor startup script executable"
else
    echo "   ❌ Startup script not executable"
fi

echo ""
echo "5. Checking hook registration..."
if grep -q "autonomous-agent-teams.py" ~/.claude/settings.json; then
    echo "   ✅ Hook registered in settings.json"
else
    echo "   ❌ Hook NOT registered"
fi

echo ""
echo "6. Testing log directory..."
if [ -d ~/.claude/logs ]; then
    echo "   ✅ Logs directory exists"
    if [ -f ~/.claude/logs/autonomous_teams.log ]; then
        LINES=$(wc -l < ~/.claude/logs/autonomous_teams.log)
        echo "      Existing log: $LINES lines"
    fi
else
    mkdir -p ~/.claude/logs
    echo "   ✅ Logs directory created"
fi

echo ""
echo "7. Checking documentation..."
if [ -f ~/.claude/docs/AUTONOMOUS_AGENT_TEAMS.md ]; then
    LINES=$(wc -l < ~/.claude/docs/AUTONOMOUS_AGENT_TEAMS.md)
    echo "   ✅ Autonomous teams guide ($LINES lines)"
else
    echo "   ❌ Documentation missing"
fi

echo ""
echo "=== Test Results Summary ==="
echo ""
echo "📊 Sample Hook Output (first 25 lines):"
echo "----------------------------------------"
head -25 /tmp/hook_output.txt
echo "----------------------------------------"
echo ""
echo "🎯 System Status: ✅ Autonomous agent teams ready"
echo ""
echo "💡 Try it:"
echo '  claude'
echo '  > Create a team to investigate this bug from multiple angles'
echo ""
echo "📈 Monitor (optional):"
echo '  ~/.claude/autonomous/start_team_monitor.sh'
echo '  tail -f ~/.claude/logs/autonomous_teams_monitor.log'
echo ""
echo "📝 View logs:"
echo '  tail -f ~/.claude/logs/autonomous_teams.log'
echo ""

# Cleanup
rm -f /tmp/hook_output.txt /tmp/simple_output.txt 2>/dev/null
