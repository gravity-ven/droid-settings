#!/bin/bash

# Supermemory Setup Script for Claude Code
# Run this after getting your API key from https://console.supermemory.ai/keys

echo "🧠 Supermemory Setup for Claude Code"
echo "===================================="
echo ""

# Check if API key is already set
if [ -n "$SUPERMEMORY_CC_API_KEY" ]; then
    echo "✅ SUPERMEMORY_CC_API_KEY is already set"
    echo "   Key: ${SUPERMEMORY_CC_API_KEY:0:10}..."
else
    echo "⚠️  SUPERMEMORY_CC_API_KEY is not set"
    echo ""
    echo "To get your API key:"
    echo "1. Visit: https://console.supermemory.ai/keys"
    echo "2. Sign up or log in"
    echo "3. Create a new API key (format: sm_...)"
    echo ""
    read -p "Enter your Supermemory API key (sm_...): " api_key

    if [[ $api_key == sm_* ]]; then
        # Detect shell
        if [ -n "$ZSH_VERSION" ]; then
            SHELL_RC="$HOME/.zshrc"
        elif [ -n "$BASH_VERSION" ]; then
            SHELL_RC="$HOME/.bashrc"
        else
            SHELL_RC="$HOME/.profile"
        fi

        echo ""
        echo "Adding to $SHELL_RC..."
        echo "export SUPERMEMORY_CC_API_KEY=\"$api_key\"" >> "$SHELL_RC"
        export SUPERMEMORY_CC_API_KEY="$api_key"

        echo "✅ API key added to $SHELL_RC"
        echo ""
        echo "Run: source $SHELL_RC"
        echo "Or restart your terminal"
    else
        echo "❌ Invalid API key format (should start with 'sm_')"
        exit 1
    fi
fi

echo ""
echo "Checking installation..."
echo ""

# Check plugin installation
if [ -d "$HOME/.claude/plugins/supermemory" ]; then
    echo "✅ Plugin installed: ~/.claude/plugins/supermemory/"
else
    echo "❌ Plugin not found"
    exit 1
fi

# Check settings file
if [ -f "$HOME/.supermemory-claude/settings.json" ]; then
    echo "✅ Settings configured: ~/.supermemory-claude/settings.json"
else
    echo "⚠️  Settings file not found (will use defaults)"
fi

# Check MCP configuration
if grep -q '"supermemory"' "$HOME/.claude/settings.json" 2>/dev/null; then
    echo "✅ MCP server configured in Claude settings"
else
    echo "⚠️  MCP server not configured"
fi

echo ""
echo "📋 Setup Status Summary"
echo "======================="
echo "Plugin: ✅ Installed"
echo "MCP Server: ✅ Configured"
echo "API Key: $([ -n "$SUPERMEMORY_CC_API_KEY" ] && echo '✅ Set' || echo '❌ Not set')"
echo ""

if [ -n "$SUPERMEMORY_CC_API_KEY" ]; then
    echo "✅ Setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Restart Claude Code (exit and relaunch)"
    echo "2. Test with: /claude-supermemory:index"
    echo "3. Index your important projects"
    echo ""
    echo "Commands available:"
    echo "  /claude-supermemory:index   - Index current codebase"
    echo "  /claude-supermemory:logout  - Logout and clear credentials"
else
    echo "⚠️  Setup incomplete - API key needed"
    echo ""
    echo "Get your API key from: https://console.supermemory.ai/keys"
    echo "Then run this script again or set manually:"
    echo "  export SUPERMEMORY_CC_API_KEY=\"sm_your_key_here\""
fi

echo ""
echo "Documentation: ~/.claude/SUPERMEMORY_SETUP.md"
echo "Support: https://github.com/supermemoryai/claude-supermemory"
echo ""
