# MCP Servers Setup Guide

## Overview
You now have the following MCP servers configured for all Claude CLI agents:

1. **GitHub** - Repository management, issues, PRs, code search
2. **Slack** - Send messages, read channels, manage conversations
3. **Filesystem** - Enhanced file operations (includes grep functionality)
4. **Memory** - Persistent knowledge graph storage
5. **PostgreSQL** - Database access (already configured)

## Required Environment Variables

### 1. GitHub MCP Server

**Create a GitHub Personal Access Token:**

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a descriptive name: "Claude Code MCP"
4. Select scopes:
   - ✅ `repo` (full repository access)
   - ✅ `read:org` (read organization data)
   - ✅ `read:user` (read user profile)
   - ✅ `user:email` (access user email)
5. Generate and copy the token

**Add to shell config:**

```bash
# Add to ~/.zshrc (or ~/.bashrc if using bash)
export GITHUB_TOKEN="ghp_your_token_here"
```

### 2. Slack MCP Server

**Create a Slack App and Get Tokens:**

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name it: "Claude Code MCP"
4. Select your workspace
5. Go to "OAuth & Permissions"
6. Add Bot Token Scopes:
   - ✅ `channels:history` (View messages in channels)
   - ✅ `channels:read` (View basic channel info)
   - ✅ `chat:write` (Send messages as bot)
   - ✅ `users:read` (View people in workspace)
   - ✅ `groups:read` (View private channels)
   - ✅ `im:read` (View direct messages)
   - ✅ `mpim:read` (View group direct messages)
7. Click "Install to Workspace"
8. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

**Get your Slack Team ID:**

1. In Slack, click your workspace name (top left)
2. Go to "Settings & administration" → "Workspace settings"
3. The Team ID is in the URL: `https://app.slack.com/client/T0XXXXXXXXX/`
4. Or find it at the bottom of the workspace settings page

**Add to shell config:**

```bash
# Add to ~/.zshrc (or ~/.bashrc if using bash)
export SLACK_BOT_TOKEN="xoxb-your-token-here"
export SLACK_TEAM_ID="T0XXXXXXXXX"
```

### 3. Apply Environment Variables

After adding tokens to your shell config:

```bash
# Reload shell configuration
source ~/.zshrc  # or source ~/.bashrc

# Verify tokens are set
echo $GITHUB_TOKEN
echo $SLACK_BOT_TOKEN
echo $SLACK_TEAM_ID
```

## Verify MCP Servers are Working

Start Claude and run:

```bash
# Test GitHub MCP
# You should be able to use GitHub-related tools

# Test Slack MCP
# You should be able to send Slack messages

# Test Filesystem MCP
# Enhanced file operations should be available
```

## Configuration Files Updated

The following files have been configured:

1. **`~/.claude/settings.json`** - Main MCP server definitions
2. **`~/.claude/settings.local.json`** - Enabled MCP servers list

## Available MCP Tools

### GitHub Tools
- `github__create_or_update_file` - Create/update files in repos
- `github__search_repositories` - Search GitHub repos
- `github__create_repository` - Create new repos
- `github__get_file_contents` - Read file contents
- `github__push_files` - Push multiple files
- `github__create_issue` - Create issues
- `github__create_pull_request` - Create PRs
- `github__list_commits` - View commit history
- And many more...

### Slack Tools
- `slack__send_message` - Send messages to channels
- `slack__list_channels` - List all channels
- `slack__read_thread` - Read message threads
- `slack__get_channel_history` - Read channel messages
- `slack__search_messages` - Search messages
- And more...

### Filesystem Tools
- `filesystem__read_file` - Read files with grep-like capabilities
- `filesystem__write_file` - Write files
- `filesystem__search_files` - Search file contents (grep functionality)
- `filesystem__list_directory` - List directories
- And more...

### Memory Tools
- `memory__create_entities` - Store knowledge entities
- `memory__add_observations` - Add observations
- `memory__create_relations` - Link entities
- `memory__search_nodes` - Search knowledge graph

## Troubleshooting

### MCP Server Not Starting

```bash
# Check if npx is installed
which npx

# Test running MCP server manually
npx -y @modelcontextprotocol/server-github

# Check Claude logs
tail -f ~/.claude/logs/mcp-*.log
```

### Token Issues

```bash
# Verify tokens are exported
env | grep -E "GITHUB_TOKEN|SLACK_BOT_TOKEN|SLACK_TEAM_ID"

# Check token format
# GitHub: should start with ghp_ or github_pat_
# Slack Bot: should start with xoxb-
```

### Permissions Issues

- **GitHub**: Make sure your token has the required scopes
- **Slack**: Ensure bot is invited to channels you want to access
- **Filesystem**: MCP server is scoped to /Users/spartan by default

## Security Notes

- **Never commit tokens** to git repositories
- Store tokens only in shell config files (with restricted permissions)
- Rotate tokens regularly
- Use fine-grained permissions where possible
- GitHub fine-grained tokens are more secure than classic tokens

## Advanced Configuration

### Limiting Filesystem Access

Edit `~/.claude/settings.json` to restrict filesystem MCP to specific directories:

```json
"filesystem": {
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-filesystem",
    "/Users/spartan/Spartan_Labs",
    "/Users/spartan/projects"
  ]
}
```

### Adding More MCP Servers

Available official MCP servers:
- `@modelcontextprotocol/server-brave-search` - Web search via Brave
- `@modelcontextprotocol/server-puppeteer` - Browser automation
- `@modelcontextprotocol/server-sequential-thinking` - Complex reasoning
- `@modelcontextprotocol/server-everything` - Local file search

Add to `settings.json` mcpServers section following the same pattern.

## Documentation

- MCP Documentation: https://modelcontextprotocol.io/
- GitHub MCP: https://github.com/modelcontextprotocol/servers
- Slack API: https://api.slack.com/docs

---

**Last Updated**: February 2, 2026
**Status**: Configured and Ready (pending environment variables)
