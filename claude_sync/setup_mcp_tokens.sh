#!/usr/bin/env bash

##############################################################################
# MCP Tokens Setup Script
# Helps you add GitHub and Slack tokens to your shell configuration
##############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
cat << "EOF"
   __  __  ____ ____    ____       _
  |  \/  |/ ___|  _ \  / ___|  ___| |_ _   _ _ __
  | |\/| | |   | |_) | \___ \ / _ \ __| | | | '_ \
  | |  | | |___|  __/   ___) |  __/ |_| |_| | |_) |
  |_|  |_|\____|_|     |____/ \___|\__|\__,_| .__/
                                             |_|
EOF
echo -e "${NC}"

echo -e "${GREEN}Setting up MCP server tokens...${NC}"
echo ""

# Detect shell
if [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
    SHELL_NAME="zsh"
elif [ -n "$BASH_VERSION" ]; then
    if [ -f "$HOME/.bash_profile" ]; then
        SHELL_CONFIG="$HOME/.bash_profile"
    else
        SHELL_CONFIG="$HOME/.bashrc"
    fi
    SHELL_NAME="bash"
else
    SHELL_CONFIG="$HOME/.profile"
    SHELL_NAME="sh"
fi

echo -e "${BLUE}Detected shell: ${SHELL_NAME}${NC}"
echo -e "${BLUE}Config file: ${SHELL_CONFIG}${NC}"
echo ""

# Check if tokens already exist
if grep -q "GITHUB_TOKEN" "$SHELL_CONFIG" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  GITHUB_TOKEN already exists in ${SHELL_CONFIG}${NC}"
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    UPDATE_GITHUB=$REPLY
else
    UPDATE_GITHUB="y"
fi

if grep -q "SLACK_BOT_TOKEN" "$SHELL_CONFIG" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  SLACK_BOT_TOKEN already exists in ${SHELL_CONFIG}${NC}"
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    UPDATE_SLACK=$REPLY
else
    UPDATE_SLACK="y"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  GitHub Token Setup${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [[ $UPDATE_GITHUB =~ ^[Yy]$ ]]; then
    echo "To get a GitHub token:"
    echo "1. Visit: https://github.com/settings/tokens"
    echo "2. Generate new token (classic)"
    echo "3. Select scopes: repo, read:org, read:user, user:email"
    echo ""
    read -p "Enter your GitHub token (ghp_...): " GITHUB_TOKEN

    if [ -n "$GITHUB_TOKEN" ]; then
        # Remove old token if exists
        sed -i.bak '/export GITHUB_TOKEN=/d' "$SHELL_CONFIG" 2>/dev/null || true

        # Add new token
        echo "" >> "$SHELL_CONFIG"
        echo "# GitHub MCP Token (added $(date))" >> "$SHELL_CONFIG"
        echo "export GITHUB_TOKEN=\"$GITHUB_TOKEN\"" >> "$SHELL_CONFIG"

        echo -e "${GREEN}✅ GitHub token added to ${SHELL_CONFIG}${NC}"
    else
        echo -e "${YELLOW}⚠️  Skipped GitHub token (empty input)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Skipped GitHub token (user choice)${NC}"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Slack Token Setup${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [[ $UPDATE_SLACK =~ ^[Yy]$ ]]; then
    echo "To get Slack tokens:"
    echo "1. Visit: https://api.slack.com/apps"
    echo "2. Create New App → From scratch"
    echo "3. Add OAuth scopes: channels:history, chat:write, etc."
    echo "4. Install to Workspace"
    echo "5. Copy Bot User OAuth Token (xoxb-...)"
    echo ""
    read -p "Enter your Slack Bot Token (xoxb-...): " SLACK_BOT_TOKEN
    echo ""
    echo "To find your Team ID:"
    echo "1. In Slack, click workspace name → Settings & administration"
    echo "2. Team ID is in URL or at bottom of settings page (T0XXXXXXXXX)"
    echo ""
    read -p "Enter your Slack Team ID (T0...): " SLACK_TEAM_ID

    if [ -n "$SLACK_BOT_TOKEN" ] && [ -n "$SLACK_TEAM_ID" ]; then
        # Remove old tokens if exist
        sed -i.bak '/export SLACK_BOT_TOKEN=/d' "$SHELL_CONFIG" 2>/dev/null || true
        sed -i.bak '/export SLACK_TEAM_ID=/d' "$SHELL_CONFIG" 2>/dev/null || true

        # Add new tokens
        echo "" >> "$SHELL_CONFIG"
        echo "# Slack MCP Tokens (added $(date))" >> "$SHELL_CONFIG"
        echo "export SLACK_BOT_TOKEN=\"$SLACK_BOT_TOKEN\"" >> "$SHELL_CONFIG"
        echo "export SLACK_TEAM_ID=\"$SLACK_TEAM_ID\"" >> "$SHELL_CONFIG"

        echo -e "${GREEN}✅ Slack tokens added to ${SHELL_CONFIG}${NC}"
    else
        echo -e "${YELLOW}⚠️  Skipped Slack tokens (incomplete input)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Skipped Slack tokens (user choice)${NC}"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Next steps:"
echo ""
echo -e "1. ${YELLOW}Reload your shell configuration:${NC}"
echo -e "   ${BLUE}source ${SHELL_CONFIG}${NC}"
echo ""
echo -e "2. ${YELLOW}Verify tokens are set:${NC}"
echo -e "   ${BLUE}echo \$GITHUB_TOKEN${NC}"
echo -e "   ${BLUE}echo \$SLACK_BOT_TOKEN${NC}"
echo ""
echo -e "3. ${YELLOW}Restart Claude Code:${NC}"
echo -e "   ${BLUE}claude${NC}"
echo ""
echo -e "4. ${YELLOW}Read the full guide:${NC}"
echo -e "   ${BLUE}cat ~/.claude/MCP_SETUP_GUIDE.md${NC}"
echo ""
echo -e "${GREEN}MCP servers (GitHub, Slack, Filesystem, Memory) are now configured!${NC}"
echo ""
