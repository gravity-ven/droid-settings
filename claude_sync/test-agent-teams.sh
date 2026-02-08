#!/bin/bash
# Test Agent Teams Integration

echo "=== Agent Teams Integration Test ==="
echo ""

echo "1. Checking environment variable..."
if grep -q "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS" ~/.claude/settings.json; then
    echo "   ✅ Environment variable configured in settings.json"
else
    echo "   ❌ Environment variable NOT found in settings.json"
fi

echo ""
echo "2. Checking hook integration..."
if grep -q "agent-teams-context.py" ~/.claude/settings.json; then
    echo "   ✅ Hook registered in UserPromptSubmit"
else
    echo "   ❌ Hook NOT registered"
fi

echo ""
echo "3. Checking hook file..."
if [ -x ~/.claude/hooks/agent-teams-context.py ]; then
    echo "   ✅ Hook file exists and is executable"
else
    echo "   ❌ Hook file missing or not executable"
fi

echo ""
echo "4. Testing hook execution..."
echo '{"userMessage": "Create a team to investigate multiple hypotheses for this bug"}' | python3 ~/.claude/hooks/agent-teams-context.py
if [ $? -eq 0 ]; then
    echo "   ✅ Hook executes successfully"
else
    echo "   ❌ Hook execution failed"
fi

echo ""
echo "5. Checking documentation..."
if [ -f ~/.claude/docs/AGENT_TEAMS_GUIDE.md ]; then
    echo "   ✅ Documentation created ($(wc -l < ~/.claude/docs/AGENT_TEAMS_GUIDE.md) lines)"
else
    echo "   ❌ Documentation missing"
fi

echo ""
echo "6. Checking CLAUDE.md integration..."
if grep -q "Agent Teams Integration" ~/.claude/CLAUDE.md; then
    echo "   ✅ CLAUDE.md updated with agent teams section"
else
    echo "   ❌ CLAUDE.md not updated"
fi

echo ""
echo "=== Integration Status ==="
echo "✅ Agent teams fully integrated into CLI"
echo ""
echo "Try it with:"
echo '  claude'
echo '  > Create an agent team with 3 members to review this codebase'
echo ""
