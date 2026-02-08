#!/bin/bash
# Dr. Zero Evolution Framework Initialization Script

set -e

CLAUDE_DIR="$HOME/.claude"
EVOLUTION_DIR="$CLAUDE_DIR/evolution"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Dr. Zero Self-Evolution Framework - Initialization"
echo "Based on Meta/UIUC Research (arXiv:2601.07055)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Check if directory structure exists
echo "✓ Checking directory structure..."
mkdir -p "$EVOLUTION_DIR"/{state,challenges,prompts}

# Check Python availability
echo "✓ Checking Python 3..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Error: Python 3 not found in PATH"
    exit 1
fi

# Verify core engine exists
echo "✓ Verifying core evolution engine..."
if [ ! -f "$EVOLUTION_DIR/dr_zero_engine.py" ]; then
    echo "✗ Error: dr_zero_engine.py not found"
    exit 1
fi

# Test engine import
echo "✓ Testing engine import..."
if ! python3 -c "import sys; sys.path.insert(0, '$EVOLUTION_DIR'); from dr_zero_engine import get_engine" 2>/dev/null; then
    echo "✗ Error: Cannot import dr_zero_engine"
    exit 1
fi

# Initialize evolution state for all domains
echo "✓ Initializing evolution state..."
for domain in trading research coding data_analysis general; do
    echo "  • Initializing $domain domain..."
    python3 "$EVOLUTION_DIR/dr_zero_engine.py" status "$domain" > /dev/null 2>&1 || true
done

# Verify hooks are executable
echo "✓ Verifying hook permissions..."
chmod +x "$CLAUDE_DIR/hooks"/*.py 2>/dev/null || true

# Check hook integration
echo "✓ Checking hook integration..."

if grep -q "dr_zero_engine" "$CLAUDE_DIR/hooks/session-start.py" 2>/dev/null; then
    echo "  • session-start.py: ✓ Integrated"
else
    echo "  • session-start.py: ✗ Not integrated"
fi

if grep -q "DR_ZERO_AVAILABLE" "$CLAUDE_DIR/hooks/user-prompt-submit.py" 2>/dev/null; then
    echo "  • user-prompt-submit.py: ✓ Integrated"
else
    echo "  • user-prompt-submit.py: ✗ Not integrated"
fi

if grep -q "record_dr_zero_result" "$CLAUDE_DIR/hooks/post-tool-use.py" 2>/dev/null; then
    echo "  • post-tool-use.py: ✓ Integrated"
else
    echo "  • post-tool-use.py: ✗ Not integrated"
fi

# Display current status
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Evolution Status Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

for domain in trading research coding data_analysis general; do
    echo "Domain: $domain"
    python3 "$EVOLUTION_DIR/dr_zero_engine.py" status "$domain" 2>/dev/null | python3 -m json.tool | grep -E "(iteration|frontier_hop_level|solved_challenges|total_challenges)" | sed 's/^/  /'
    echo
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Initialization Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "The Dr. Zero framework is now active and will operate autonomously"
echo "through hooks. No manual invocation needed."
echo
echo "For manual control:"
echo "  • Check status: python3 $EVOLUTION_DIR/dr_zero_engine.py status <domain>"
echo "  • Force evolution: python3 $EVOLUTION_DIR/dr_zero_engine.py evolve <domain>"
echo "  • Reset domain: python3 $EVOLUTION_DIR/dr_zero_engine.py reset <domain>"
echo
echo "Documentation: $EVOLUTION_DIR/README.md"
echo "Reference prompts: $EVOLUTION_DIR/prompts/"
echo
