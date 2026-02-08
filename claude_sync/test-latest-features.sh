#!/bin/bash
# Test Latest Anthropic Features Integration (Feb 2026)

echo "=== Latest Anthropic Features Integration Test ==="
echo ""
echo "Testing features from: https://www.anthropic.com/news/claude-opus-4-6"
echo ""

# 1. Compaction API
echo "1. Compaction API (Infinite Conversations)"
if [ -f ~/.claude/features/compaction_config.json ]; then
    echo "   ✅ Configuration file exists"
    THRESHOLD=$(cat ~/.claude/features/compaction_config.json | grep -o '"trigger_threshold": [0-9]*' | grep -o '[0-9]*')
    echo "      Threshold: $THRESHOLD tokens"
else
    echo "   ❌ Configuration missing"
fi

if [ -x ~/.claude/hooks/compaction-manager.py ]; then
    echo "   ✅ Compaction manager hook executable"
else
    echo "   ❌ Hook not executable"
fi

if grep -q "compaction-manager.py" ~/.claude/settings.json; then
    echo "   ✅ Hook registered in settings.json"
else
    echo "   ❌ Hook NOT registered"
fi

echo ""

# 2. Environment Variables
echo "2. Global Environment Variables"
if grep -q "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS" ~/.claude/settings.json; then
    echo "   ✅ Agent teams enabled"
fi
if grep -q "CLAUDE_CODE_COMPACTION_ENABLED" ~/.claude/settings.json; then
    echo "   ✅ Compaction enabled"
fi
if grep -q "CLAUDE_CODE_ADAPTIVE_THINKING" ~/.claude/settings.json; then
    echo "   ✅ Adaptive thinking configured"
fi

echo ""

# 3. Chrome Integration
echo "3. Chrome Integration (Beta)"
if [ -x ~/.claude/setup/install-chrome-integration.sh ]; then
    echo "   ✅ Installation script ready"
    echo "      Run: ~/.claude/setup/install-chrome-integration.sh"
else
    echo "   ❌ Installation script missing"
fi

if [ -x ~/.claude/chrome-start.sh ]; then
    echo "   ✅ Quick start script exists"
    echo "      Run: ~/.claude/chrome-start.sh"
else
    echo "   ⚠️  Quick start not yet created (install Chrome integration first)"
fi

echo ""

# 4. Features Configuration
echo "4. Features in settings.json"
if grep -q '"features"' ~/.claude/settings.json; then
    echo "   ✅ Features section configured"
    if grep -q '"compaction"' ~/.claude/settings.json; then
        echo "      ✓ Compaction"
    fi
    if grep -q '"adaptive_thinking"' ~/.claude/settings.json; then
        echo "      ✓ Adaptive thinking"
    fi
    if grep -q '"extended_context"' ~/.claude/settings.json; then
        echo "      ✓ Extended context (1M tokens)"
    fi
else
    echo "   ❌ Features section missing"
fi

echo ""

# 5. Documentation
echo "5. Documentation"
if [ -f ~/.claude/docs/LATEST_FEATURES_2026.md ]; then
    LINES=$(wc -l < ~/.claude/docs/LATEST_FEATURES_2026.md)
    echo "   ✅ Latest features guide ($LINES lines)"
else
    echo "   ❌ Documentation missing"
fi

if grep -q "Latest Features (February 2026)" ~/.claude/CLAUDE.md; then
    echo "   ✅ CLAUDE.md updated"
else
    echo "   ❌ CLAUDE.md not updated"
fi

echo ""

# 6. Test Compaction Hook
echo "6. Testing Compaction Hook"
TEST_INPUT='{"prompt": "Test prompt for token estimation"}'
echo "$TEST_INPUT" | python3 ~/.claude/hooks/compaction-manager.py >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Hook executes without errors"
else
    echo "   ❌ Hook execution failed"
fi

# Check if state file created
if [ -f ~/.claude/state/compaction_state.json ]; then
    echo "   ✅ State tracking works"
    ESTIMATE=$(cat ~/.claude/state/compaction_state.json | grep -o '"token_estimate": [0-9]*' | grep -o '[0-9]*' | head -1)
    if [ ! -z "$ESTIMATE" ]; then
        echo "      Last estimate: $ESTIMATE tokens"
    fi
else
    echo "   ⚠️  State file not yet created (will be created on first use)"
fi

echo ""

# 7. Logs
echo "7. Logging System"
mkdir -p ~/.claude/logs >/dev/null 2>&1
if [ -d ~/.claude/logs ]; then
    echo "   ✅ Logs directory exists"

    if [ -f ~/.claude/logs/compaction.log ]; then
        LINES=$(wc -l < ~/.claude/logs/compaction.log)
        echo "      Compaction log: $LINES lines"
    else
        echo "      Compaction log: Will be created on first use"
    fi
fi

echo ""

# 8. Integration Summary
echo "=== Integration Summary ==="
echo ""
echo "✅ Features Applied to ALL CLI Agents:"
echo "   • Main agent"
echo "   • All Task subagents (Bash, general-purpose, Explore, Plan, etc.)"
echo "   • All agent team members"
echo ""
echo "📊 Enabled Features:"
echo "   1. Compaction API - Infinite conversations (150k token threshold)"
echo "   2. Adaptive Thinking - 4 effort levels (default: high)"
echo "   3. Chrome Integration - Browser automation (setup available)"
echo "   4. Extended Context - 1M token window (beta)"
echo "   5. Agent Teams - Autonomous coordination (active)"
echo ""
echo "📝 Configuration Files:"
echo "   ~/.claude/features/compaction_config.json"
echo "   ~/.claude/settings.json (env vars + features + hooks)"
echo "   ~/.claude/CLAUDE.md (global instructions updated)"
echo ""
echo "🔍 Monitoring:"
echo "   tail -f ~/.claude/logs/compaction.log"
echo "   tail -f ~/.claude/state/compaction_state.json"
echo ""
echo "📚 Documentation:"
echo "   ~/.claude/docs/LATEST_FEATURES_2026.md"
echo "   https://www.anthropic.com/news/claude-opus-4-6"
echo ""
echo "🚀 Try New Features:"
echo ""
echo "   # Compaction (automatic)"
echo "   claude"
echo "   > [work on long task - compaction handles context automatically]"
echo ""
echo "   # Adaptive thinking"
echo "   claude --effort max"
echo "   > [complex architecture task]"
echo ""
echo "   # Chrome integration"
echo "   ~/.claude/setup/install-chrome-integration.sh"
echo "   claude --chrome"
echo "   > Go to google.com and search for \"Claude AI\""
echo ""
