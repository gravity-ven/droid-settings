# Supermemory Integration - Complete Setup Guide

**Installation Date**: 2026-02-05
**Status**: ✅ Installed, ⚠️ Requires API Key Configuration

## What is Supermemory?

Supermemory gives Claude Code persistent memory across sessions. Your AI remembers:
- What you worked on across sessions and projects
- Your coding preferences and patterns
- Project architecture and conventions
- Previous conversations and decisions

## Components Installed

### 1. Claude Code Plugin (`claude-supermemory`)
**Location**: `/Users/spartan/.claude/plugins/supermemory/`
**Status**: ✅ Installed with dependencies

**Features**:
- **Context Injection**: Relevant memories auto-injected on session start
- **Automatic Capture**: Conversation turns captured and stored
- **Codebase Indexing**: Index project architecture and patterns
- **Super-Search**: Search past work and sessions

### 2. Supermemory MCP Server
**Location**: Configured in `/Users/spartan/.claude/settings.json`
**Status**: ✅ Configured, ⚠️ Needs authentication

**Configuration**:
```json
{
  "supermemory": {
    "url": "https://mcp.supermemory.ai/mcp",
    "transport": "sse"
  }
}
```

## Setup Steps (Required)

### Step 1: Get Your Supermemory API Key

1. Visit: https://console.supermemory.ai/keys
2. Create account or sign in
3. Generate new API key (format: `sm_...`)
4. Copy the key

**Note**: Requires Supermemory Pro plan subscription

### Step 2: Configure Environment Variables

Add to your shell configuration:

**For zsh (macOS default)**:
```bash
echo 'export SUPERMEMORY_CC_API_KEY="sm_YOUR_KEY_HERE"' >> ~/.zshrc
source ~/.zshrc
```

**For bash**:
```bash
echo 'export SUPERMEMORY_CC_API_KEY="sm_YOUR_KEY_HERE"' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Verify Installation

Restart Claude Code and check:
```bash
# In Claude Code conversation
/claude-supermemory:index
```

This should index your current codebase into Supermemory.

## Available Commands

### `/claude-supermemory:index`
Index your codebase into Supermemory. Explores project structure, architecture, conventions, and key files.

```bash
/claude-supermemory:index
```

### `/claude-supermemory:logout`
Log out from Supermemory and clear saved credentials.

```bash
/claude-supermemory:logout
```

### Super-Search Skill
Automatically activated when you ask about:
- "What did we work on last session?"
- "Recall the authentication flow we built"
- "Search my memories for the API endpoint"

## Configuration Files

### Plugin Settings
**Location**: `~/.supermemory-claude/settings.json`

```json
{
  "skipTools": ["Read", "Glob", "Grep"],
  "captureTools": ["Edit", "Write", "Bash", "Task"],
  "maxProfileItems": 10,
  "debug": false
}
```

**Options**:
- `skipTools`: Tools to NOT capture in memory
- `captureTools`: Tools to capture and remember
- `maxProfileItems`: Max number of profile items to track
- `debug`: Enable debug logging

### Environment Variables

**Required**:
- `SUPERMEMORY_CC_API_KEY`: Your API key from console.supermemory.ai

**Optional**:
- `SUPERMEMORY_SKIP_TOOLS`: Comma-separated list of tools to skip (e.g., "Read,Glob,Grep")
- `SUPERMEMORY_DEBUG`: Enable debug logging (true/false)

## How It Works

### On Session Start
```
<supermemory-context>
The following is recalled context about the user...

## User Profile (Persistent)
- Prefers TypeScript over JavaScript
- Uses Bun as package manager
- Autonomous execution preferred

## Recent Context
- Working on Spartan Research financial platform
- Recently integrated Claude Code Playgrounds
- Focus on real-time market analysis

</supermemory-context>
```

### During Session
- Every `Edit`, `Write`, `Bash`, and `Task` tool use is captured
- Conversation context is stored for future retrieval
- Memories are searchable across all projects

### Codebase Indexing
When you run `/claude-supermemory:index`:
1. Explores project structure
2. Identifies key files and patterns
3. Maps architecture and conventions
4. Stores for future context injection

## Integration with Existing Memory Systems

Supermemory **complements** your existing memory setup:

| System | Purpose | Location |
|--------|---------|----------|
| **Supermemory** | Universal memory across LLMs | Cloud (supermemory.ai) |
| **MCP Memory** | Knowledge graph (entities/relations) | `~/.claude/memory/knowledge.json` |
| **Auto Memory** | Session learnings and patterns | `~/.claude/memory/MEMORY.md` |
| **Genius DNA** | Skill registry and principles | `~/.claude/knowledge/` |

All systems work together to provide comprehensive context.

## Usage Examples

### Example 1: Recall Past Work
```
You: "What pattern did we use for the barometers API?"

Claude: [Searches Supermemory]
We used a multi-service architecture with PostgreSQL backend...
[Recalls specific implementation details from past session]
```

### Example 2: Maintain Preferences
```
Supermemory remembers:
- You prefer autonomous execution (no permission prompts)
- Dark theme with gold/green accents for Spartan platform
- Zero fake data policy for financial applications
```

### Example 3: Cross-Project Learning
```
You: "How did we implement caching in the trading system?"

Claude: [Searches across all indexed projects]
In the trading LLM system, we used Redis with...
[Provides details even if from different project]
```

## Troubleshooting

### Issue: "Not authenticated" error
**Solution**: Ensure `SUPERMEMORY_CC_API_KEY` is set in environment
```bash
echo $SUPERMEMORY_CC_API_KEY  # Should show sm_...
```

### Issue: Memories not being captured
**Solution**: Check settings in `~/.supermemory-claude/settings.json`
- Ensure tools are in `captureTools` list
- Set `debug: true` to see what's being captured

### Issue: Plugin not showing commands
**Solution**: Restart Claude Code after installing plugin
```bash
# Exit Claude Code, then restart
claude
```

### Issue: MCP server not connecting
**Solution**: Check Claude Code logs
```bash
tail -f ~/.claude/logs/mcp-supermemory.log
```

## Pricing & Limits

**Free Tier**:
- Basic memory storage
- Limited searches per day

**Pro Tier** (Required for claude-supermemory plugin):
- Unlimited memory storage
- Unlimited searches
- Cross-LLM memory sync
- Priority support

Visit: https://console.supermemory.ai/billing

## Privacy & Data

- Memories are stored on Supermemory cloud (supermemory.ai)
- OAuth authentication for secure access
- Data encrypted in transit and at rest
- Can be self-hosted (see supermemory GitHub)

## Quick Start Checklist

- [x] Plugin installed at `~/.claude/plugins/supermemory/`
- [x] MCP server configured in settings.json
- [x] Plugin settings created at `~/.supermemory-claude/settings.json`
- [ ] **API key obtained from https://console.supermemory.ai/keys**
- [ ] **Environment variable set (`SUPERMEMORY_CC_API_KEY`)**
- [ ] **Claude Code restarted**
- [ ] **Test with `/claude-supermemory:index`**

## Next Steps

1. **Get API Key**: Visit https://console.supermemory.ai/keys
2. **Set Environment Variable**: Add to `~/.zshrc` or `~/.bashrc`
3. **Restart Shell**: `source ~/.zshrc` or restart terminal
4. **Restart Claude Code**: Exit and relaunch
5. **Test**: Run `/claude-supermemory:index` in a project directory
6. **Index Projects**: Run index command in each important project
7. **Use Memory**: Ask Claude to recall past work

## Resources

- **Documentation**: https://supermemory.ai/docs/integrations/claude-code
- **GitHub Plugin**: https://github.com/supermemoryai/claude-supermemory
- **GitHub MCP**: https://github.com/supermemoryai/supermemory-mcp
- **API Console**: https://console.supermemory.ai
- **MCP Setup Guide**: https://supermemory.ai/docs/supermemory-mcp/setup
- **Blog Post**: https://supermemory.ai/blog/the-ux-and-technicalities-of-awesome-mcps

## Support

- **GitHub Issues**: https://github.com/supermemoryai/claude-supermemory/issues
- **Discord**: Join Supermemory community
- **Email**: support@supermemory.ai

---

**Installation completed by**: Claude Code (Autonomous)
**Date**: 2026-02-05
**Next action**: Get API key and complete authentication setup
