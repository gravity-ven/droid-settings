#!/usr/bin/env bash

##############################################################################
# MCP Status Checker
# Quickly verify all MCP servers are configured correctly
##############################################################################

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
   __  __  ____ ____    ____  _        _
  |  \/  |/ ___|  _ \  / ___|| |_ __ _| |_ _   _ ___
  | |\/| | |   | |_) | \___ \| __/ _` | __| | | / __|
  | |  | | |___|  __/   ___) | || (_| | |_| |_| \__ \
  |_|  |_|\____|_|     |____/ \__\__,_|\__|\__,_|___/

EOF
echo -e "${NC}"

echo -e "${GREEN}MCP Server Status Check${NC}"
echo ""

# Check configuration files
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE} Configuration Files${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [ -f ~/.claude/settings.json ]; then
    echo -e "✅ ${GREEN}settings.json found${NC}"

    # Check if mcpServers section exists
    if grep -q "mcpServers" ~/.claude/settings.json; then
        echo -e "✅ ${GREEN}mcpServers section present${NC}"

        # List configured servers
        echo -e "\n${YELLOW}Configured MCP Servers:${NC}"
        grep -A 1 '"[a-z]*":' ~/.claude/settings.json | grep -E 'memory|github|slack|filesystem' | sed 's/[",:]//g' | sed 's/^/  - /'
    else
        echo -e "❌ ${RED}mcpServers section missing${NC}"
    fi
else
    echo -e "❌ ${RED}settings.json not found${NC}"
fi

echo ""

if [ -f ~/.claude/settings.local.json ]; then
    echo -e "✅ ${GREEN}settings.local.json found${NC}"

    # List enabled servers
    if grep -q "enabledMcpjsonServers" ~/.claude/settings.local.json; then
        echo -e "\n${YELLOW}Enabled MCP Servers:${NC}"
        grep -A 10 "enabledMcpjsonServers" ~/.claude/settings.local.json | grep '"' | sed 's/[",]//g' | sed 's/^/  - /'
    fi
else
    echo -e "⚠️  ${YELLOW}settings.local.json not found${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE} Environment Variables${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check GITHUB_TOKEN
if [ -n "$GITHUB_TOKEN" ]; then
    if [[ "$GITHUB_TOKEN" == ghp_* ]] || [[ "$GITHUB_TOKEN" == github_pat_* ]]; then
        TOKEN_PREFIX="${GITHUB_TOKEN:0:15}"
        echo -e "✅ ${GREEN}GITHUB_TOKEN set${NC} (${TOKEN_PREFIX}...)"
    else
        echo -e "⚠️  ${YELLOW}GITHUB_TOKEN set but format looks incorrect${NC}"
        echo -e "   Expected: ghp_... or github_pat_..."
    fi
else
    echo -e "❌ ${RED}GITHUB_TOKEN not set${NC}"
    echo -e "   Run: ${BLUE}~/.claude/setup_mcp_tokens.sh${NC}"
fi

# Check SLACK_BOT_TOKEN
if [ -n "$SLACK_BOT_TOKEN" ]; then
    if [[ "$SLACK_BOT_TOKEN" == xoxb-* ]]; then
        TOKEN_PREFIX="${SLACK_BOT_TOKEN:0:15}"
        echo -e "✅ ${GREEN}SLACK_BOT_TOKEN set${NC} (${TOKEN_PREFIX}...)"
    else
        echo -e "⚠️  ${YELLOW}SLACK_BOT_TOKEN set but format looks incorrect${NC}"
        echo -e "   Expected: xoxb-..."
    fi
else
    echo -e "❌ ${RED}SLACK_BOT_TOKEN not set${NC}"
    echo -e "   Run: ${BLUE}~/.claude/setup_mcp_tokens.sh${NC}"
fi

# Check SLACK_TEAM_ID
if [ -n "$SLACK_TEAM_ID" ]; then
    if [[ "$SLACK_TEAM_ID" == T* ]]; then
        echo -e "✅ ${GREEN}SLACK_TEAM_ID set${NC} ($SLACK_TEAM_ID)"
    else
        echo -e "⚠️  ${YELLOW}SLACK_TEAM_ID set but format looks incorrect${NC}"
        echo -e "   Expected: T0..."
    fi
else
    echo -e "❌ ${RED}SLACK_TEAM_ID not set${NC}"
    echo -e "   Run: ${BLUE}~/.claude/setup_mcp_tokens.sh${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE} Dependencies${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check npx
if command -v npx &> /dev/null; then
    NPX_VERSION=$(npx --version 2>/dev/null)
    echo -e "✅ ${GREEN}npx available${NC} (v${NPX_VERSION})"
else
    echo -e "❌ ${RED}npx not found${NC}"
    echo -e "   Install Node.js: ${BLUE}brew install node${NC}"
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version 2>/dev/null)
    echo -e "✅ ${GREEN}npm available${NC} (v${NPM_VERSION})"
else
    echo -e "❌ ${RED}npm not found${NC}"
    echo -e "   Install Node.js: ${BLUE}brew install node${NC}"
fi

# Check if Claude is available
if command -v claude &> /dev/null; then
    echo -e "✅ ${GREEN}claude command available${NC}"
else
    echo -e "⚠️  ${YELLOW}claude command not found in PATH${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE} MCP Server Test${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test GitHub MCP server
if [ -n "$GITHUB_TOKEN" ] && command -v npx &> /dev/null; then
    echo -e "${YELLOW}Testing GitHub API...${NC}"
    GITHUB_TEST=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user 2>/dev/null)
    if echo "$GITHUB_TEST" | grep -q '"login"'; then
        GITHUB_USER=$(echo "$GITHUB_TEST" | grep '"login"' | cut -d'"' -f4)
        echo -e "✅ ${GREEN}GitHub API working${NC} (logged in as: $GITHUB_USER)"
    else
        echo -e "⚠️  ${YELLOW}GitHub API test failed${NC}"
        echo -e "   Check token permissions"
    fi
fi

# Test Slack API
if [ -n "$SLACK_BOT_TOKEN" ] && command -v curl &> /dev/null; then
    echo -e "${YELLOW}Testing Slack API...${NC}"
    SLACK_TEST=$(curl -s -H "Authorization: Bearer $SLACK_BOT_TOKEN" https://slack.com/api/auth.test 2>/dev/null)
    if echo "$SLACK_TEST" | grep -q '"ok":true'; then
        SLACK_USER=$(echo "$SLACK_TEST" | grep '"user"' | cut -d'"' -f4)
        echo -e "✅ ${GREEN}Slack API working${NC} (bot user: $SLACK_USER)"
    else
        echo -e "⚠️  ${YELLOW}Slack API test failed${NC}"
        echo -e "   Check bot token"
    fi
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE} Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Count what's working
ISSUES=0

[ ! -f ~/.claude/settings.json ] && ((ISSUES++))
[ -z "$GITHUB_TOKEN" ] && ((ISSUES++))
[ -z "$SLACK_BOT_TOKEN" ] && ((ISSUES++))
[ -z "$SLACK_TEAM_ID" ] && ((ISSUES++))
! command -v npx &> /dev/null && ((ISSUES++))

if [ $ISSUES -eq 0 ]; then
    echo -e "🎉 ${GREEN}All systems operational!${NC}"
    echo ""
    echo "You can now use:"
    echo "  - GitHub MCP for repo management"
    echo "  - Slack MCP for messaging"
    echo "  - Filesystem MCP for file operations"
    echo "  - Memory MCP for knowledge persistence"
    echo ""
    echo "Start Claude: ${BLUE}claude${NC}"
elif [ $ISSUES -le 2 ]; then
    echo -e "⚠️  ${YELLOW}Minor issues detected (${ISSUES} items)${NC}"
    echo ""
    echo "Most MCP servers should work. Fix issues above for full functionality."
else
    echo -e "❌ ${RED}Setup incomplete (${ISSUES} issues)${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run setup script: ${BLUE}~/.claude/setup_mcp_tokens.sh${NC}"
    echo "  2. Install Node.js: ${BLUE}brew install node${NC}"
    echo "  3. Read guide: ${BLUE}cat ~/.claude/MCP_SETUP_GUIDE.md${NC}"
fi

echo ""
echo "Documentation:"
echo "  - Full guide: ${BLUE}~/.claude/MCP_SETUP_GUIDE.md${NC}"
echo "  - Summary: ${BLUE}~/.claude/MCP_INSTALLATION_SUMMARY.md${NC}"
echo "  - Setup tokens: ${BLUE}~/.claude/setup_mcp_tokens.sh${NC}"
echo ""
