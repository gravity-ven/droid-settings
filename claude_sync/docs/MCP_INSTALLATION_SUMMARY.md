# MCP Servers Installation Summary

**Date**: February 2, 2026
**Status**: ✅ Configured (Pending API Tokens)

---

## What Was Added

### 1. GitHub MCP Server
- **Package**: `@modelcontextprotocol/server-github`
- **Capabilities**:
  - Repository management (create, update, delete)
  - File operations (read, write, push)
  - Issues and Pull Requests
  - Code search across GitHub
  - Commit history and branches
  - Merging and reviewing
- **Required**: `GITHUB_TOKEN` environment variable

### 2. Slack MCP Server
- **Package**: `@modelcontextprotocol/server-slack`
- **Capabilities**:
  - Send messages to channels
  - Read channel history
  - Search messages
  - Thread management
  - User information
  - Channel listings
- **Required**: `SLACK_BOT_TOKEN` and `SLACK_TEAM_ID` environment variables

### 3. Filesystem MCP Server
- **Package**: `@modelcontextprotocol/server-filesystem`
- **Capabilities**:
  - Enhanced file reading (includes grep-like search)
  - File writing and editing
  - Directory operations
  - File search across directories
  - Pattern matching
- **Scope**: `/Users/spartan` (can be restricted further)
- **No tokens required**

### 4. Memory MCP Server (Already Configured)
- **Package**: `@modelcontextprotocol/server-memory`
- **Capabilities**:
  - Persistent knowledge graph
  - Entity storage
  - Relationship mapping
  - Context retention across sessions
- **Storage**: `~/.claude/memory/knowledge.json`

---

## Configuration Files Modified

### 1. `~/.claude/settings.json`
```json
{
  "mcpServers": {
    "memory": { ... },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}" }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
        "SLACK_TEAM_ID": "${SLACK_TEAM_ID}"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/spartan"
      ]
    }
  }
}
```

### 2. `~/.claude/settings.local.json`
```json
{
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": [
    "github",
    "filesystem",
    "postgres",
    "slack",
    "memory"
  ]
}
```

---

## Quick Start Guide

### Step 1: Set Up API Tokens

Run the interactive setup script:
```bash
~/.claude/setup_mcp_tokens.sh
```

Or manually add to `~/.zshrc` (or `~/.bashrc`):
```bash
# GitHub Token
export GITHUB_TOKEN="ghp_your_token_here"

# Slack Tokens
export SLACK_BOT_TOKEN="xoxb-your-token-here"
export SLACK_TEAM_ID="T0XXXXXXXXX"
```

### Step 2: Reload Shell
```bash
source ~/.zshrc  # or source ~/.bashrc
```

### Step 3: Verify Tokens
```bash
echo $GITHUB_TOKEN
echo $SLACK_BOT_TOKEN
echo $SLACK_TEAM_ID
```

### Step 4: Test MCP Servers

Start Claude Code:
```bash
claude
```

Then try these commands:
```
# Test GitHub
"List my repositories"
"Create a new repo called test-mcp"

# Test Slack
"Send a message to #general channel"
"List all Slack channels"

# Test Filesystem
"Search for files containing 'TODO' in my home directory"
"Read and analyze the structure of ~/Spartan_Labs"

# Test Memory
"Remember that I prefer Python over JavaScript"
"What do you know about my preferences?"
```

---

## Available Tools

### GitHub MCP Tools (34 tools)
- `github__create_or_update_file`
- `github__search_repositories`
- `github__create_repository`
- `github__get_file_contents`
- `github__push_files`
- `github__create_issue`
- `github__create_pull_request`
- `github__fork_repository`
- `github__create_branch`
- `github__list_commits`
- `github__list_issues`
- `github__update_issue`
- `github__add_issue_comment`
- `github__search_code`
- `github__search_issues`
- `github__search_users`
- `github__get_issue`
- `github__get_pull_request`
- `github__list_pull_requests`
- `github__create_pull_request_review`
- `github__merge_pull_request`
- `github__get_pull_request_files`
- `github__get_pull_request_status`
- `github__update_pull_request_branch`
- `github__get_pull_request_comments`
- `github__get_pull_request_reviews`
- And more...

### Slack MCP Tools (10+ tools)
- `slack__send_message`
- `slack__list_channels`
- `slack__read_thread`
- `slack__get_channel_history`
- `slack__search_messages`
- `slack__get_user_info`
- `slack__list_users`
- And more...

### Filesystem MCP Tools (5+ tools)
- `filesystem__read_file` (with grep capabilities)
- `filesystem__write_file`
- `filesystem__search_files` (recursive grep)
- `filesystem__list_directory`
- `filesystem__get_file_info`
- And more...

### Memory MCP Tools (6 tools)
- `memory__create_entities`
- `memory__add_observations`
- `memory__create_relations`
- `memory__search_nodes`
- `memory__delete_entity`
- `memory__open_nodes`

---

## Token Setup Instructions

### GitHub Token
1. Visit: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "Claude Code MCP"
4. Scopes: `repo`, `read:org`, `read:user`, `user:email`
5. Copy token (starts with `ghp_`)

### Slack Tokens
1. Visit: https://api.slack.com/apps
2. Create New App → From scratch
3. Name: "Claude Code MCP"
4. OAuth & Permissions → Add Bot Token Scopes:
   - `channels:history`
   - `channels:read`
   - `chat:write`
   - `users:read`
   - `groups:read`
   - `im:read`
   - `mpim:read`
5. Install to Workspace
6. Copy Bot Token (starts with `xoxb-`)
7. Get Team ID from workspace settings URL

---

## Benefits

### Unified Workflow
- Manage GitHub repos without leaving Claude
- Send Slack notifications from automation scripts
- Search files with powerful grep functionality
- Persistent memory across sessions

### Automation Examples

**1. Create PR from Claude:**
```
"Create a new branch 'feature/new-api',
push these changes, and open a PR to main"
```

**2. Slack Notifications:**
```
"When the build finishes, send a message to
#deployments channel with the status"
```

**3. Code Search:**
```
"Find all TODO comments in Python files
across my Spartan_Labs project"
```

**4. Knowledge Retention:**
```
"Remember that I use PostgreSQL for this project,
not SQLite"
```

---

## Troubleshooting

### MCP Server Won't Start

**Check npx is installed:**
```bash
which npx
npm --version
```

**Test MCP server manually:**
```bash
npx -y @modelcontextprotocol/server-github
```

**Check Claude logs:**
```bash
ls -la ~/.claude/logs/
tail -f ~/.claude/logs/mcp-*.log
```

### Token Not Working

**Verify environment variables:**
```bash
env | grep -E "GITHUB_TOKEN|SLACK"
```

**Check token format:**
- GitHub: `ghp_` or `github_pat_`
- Slack Bot: `xoxb-`
- Slack Team: `T0` followed by alphanumeric

**Test token directly:**
```bash
# GitHub
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Slack
curl -H "Authorization: Bearer $SLACK_BOT_TOKEN" https://slack.com/api/auth.test
```

### Permission Denied

- **GitHub**: Token needs correct scopes
- **Slack**: Bot must be invited to channels
- **Filesystem**: Check directory permissions

---

## Security Best Practices

1. ✅ **Never commit tokens** to version control
2. ✅ **Use fine-grained tokens** when possible (GitHub)
3. ✅ **Rotate tokens regularly** (every 90 days)
4. ✅ **Restrict filesystem scope** to necessary directories only
5. ✅ **Review MCP permissions** periodically
6. ✅ **Use separate tokens** for different environments (dev/prod)
7. ✅ **Store tokens in shell config** with restricted permissions (chmod 600)

---

## Additional Resources

- **MCP Setup Guide**: `~/.claude/MCP_SETUP_GUIDE.md`
- **Interactive Setup**: `~/.claude/setup_mcp_tokens.sh`
- **MCP Docs**: https://modelcontextprotocol.io/
- **GitHub MCP**: https://github.com/modelcontextprotocol/servers
- **Claude Code Docs**: https://docs.anthropic.com/claude-code

---

## What's Next?

After setting up tokens:

1. **Test each MCP server** individually
2. **Build automation workflows** using multiple MCP servers together
3. **Create custom MCP servers** for your specific needs
4. **Share learnings** with the team via Slack using Slack MCP

---

## Support

If you encounter issues:

1. Check this guide and `MCP_SETUP_GUIDE.md`
2. Review Claude logs: `~/.claude/logs/`
3. Test MCP servers manually with npx
4. Verify tokens are correctly formatted
5. Check GitHub/Slack API status pages

---

**Configured By**: Claude Sonnet 4.5
**Configuration Valid**: All Claude CLI sessions on this machine
**Last Updated**: February 2, 2026
