#!/bin/bash
# Install Chrome Integration for Claude Code (Beta)
# Released: February 2026

echo "=== Claude Code Chrome Integration Setup ==="
echo ""

# Check prerequisites
echo "1. Checking prerequisites..."

# Check if Chrome is installed
if ! command -v /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome &> /dev/null; then
    echo "   ❌ Google Chrome not found"
    echo "   → Install from: https://www.google.com/chrome/"
    exit 1
else
    echo "   ✅ Google Chrome installed"
fi

# Check Claude Code version
CLAUDE_VERSION=$(claude --version 2>/dev/null | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' | head -1)
if [ -z "$CLAUDE_VERSION" ]; then
    echo "   ⚠️  Could not detect Claude Code version"
else
    echo "   ✅ Claude Code version: $CLAUDE_VERSION"
fi

echo ""
echo "2. Installing Chrome Extension..."
echo "   → Visit: https://chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn"
echo "   → Click 'Add to Chrome'"
echo "   → Minimum version required: 1.0.36"
echo ""
read -p "   Press Enter after installing the extension..."

echo ""
echo "3. Setting up native messaging host..."

# Create native messaging host directory
NATIVE_DIR="$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts"
mkdir -p "$NATIVE_DIR"

# Check if config exists (Claude Code should create this)
CONFIG_FILE="$NATIVE_DIR/com.anthropic.claude_code_browser_extension.json"
if [ -f "$CONFIG_FILE" ]; then
    echo "   ✅ Native messaging host config found"
    echo "      $CONFIG_FILE"
else
    echo "   ⚠️  Native messaging host config not found"
    echo "   → Run: claude --chrome"
    echo "   → This will create the config on first use"
fi

echo ""
echo "4. Testing connection..."
echo "   → Start Claude Code with: claude --chrome"
echo "   → Or enable in session: /chrome"
echo ""

# Create quick start script
cat > ~/.claude/chrome-start.sh << 'EOF'
#!/bin/bash
# Quick start Claude Code with Chrome integration
claude --chrome
EOF
chmod +x ~/.claude/chrome-start.sh

echo "5. Created quick start script:"
echo "   → ~/.claude/chrome-start.sh"
echo ""

echo "=== Setup Complete ==="
echo ""
echo "📋 Next Steps:"
echo "   1. Start Claude Code with Chrome:"
echo "      claude --chrome"
echo ""
echo "   2. Or use quick start:"
echo "      ~/.claude/chrome-start.sh"
echo ""
echo "   3. Test connection:"
echo "      /chrome"
echo ""
echo "   4. Try it:"
echo '      > Go to google.com and search for "Claude AI"'
echo ""
echo "📚 Documentation:"
echo "   https://code.claude.com/docs/en/chrome"
echo ""
echo "💡 Enable by default:"
echo "   Run: /chrome → Select 'Enabled by default'"
echo ""
