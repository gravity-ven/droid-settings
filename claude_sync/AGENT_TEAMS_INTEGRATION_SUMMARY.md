# Agent Teams Integration - Complete

**Date**: 2026-02-06
**Feature**: Anthropic Agent Teams (released Feb 5, 2026)
**Status**: ✅ Fully Integrated

## What Was Integrated

Anthropic's new **Agent Teams** feature - multi-agent coordination where independent Claude instances work together, communicate directly, and share task lists (distinct from existing Task subagents).

## Integration Components

### 1. Global Enable
**File**: `~/.claude/settings.json`
```json
"env": {
  "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
}
```

### 2. Auto-Context Hook
**File**: `~/.claude/hooks/agent-teams-context.py`
- Triggered on UserPromptSubmit
- Analyzes prompt for parallel coordination needs
- Injects contextual guidance about teams vs subagents
- Provides syntax examples when appropriate

**Hook Logic**:
- Detects keywords: "multiple perspectives", "competing hypotheses", "cross-layer", "team"
- Calculates team_score vs subagent_score
- Injects full context if team_score > subagent_score
- Minimal awareness notice otherwise

### 3. Hook Registration
**File**: `~/.claude/settings.json`
```json
"UserPromptSubmit": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python3 ~/.claude/hooks/agent-teams-context.py",
        "timeout": 3,
        "description": "Inject agent teams context when appropriate"
      }
    ]
  }
]
```

### 4. Comprehensive Documentation
**File**: `~/.claude/docs/AGENT_TEAMS_GUIDE.md` (408 lines)

Covers:
- What are agent teams vs subagents
- When to use (decision tree)
- How to create teams (syntax + examples)
- Advanced features (plan approval, delegate mode, split panes)
- Team management (messaging, cleanup, monitoring)
- Architecture details (storage, components, communication)
- Token usage guidance
- Best practices
- Troubleshooting
- Integration with existing CLI
- Examples library (code review, hypothesis testing, cross-layer features)
- Current limitations

### 5. CLAUDE.md Integration
**File**: `~/.claude/CLAUDE.md`
- Added "Agent Teams Integration" section
- Quick reference for teams vs subagents
- Basic usage syntax
- When to use guidance
- Link to full documentation

### 6. Quick Reference Skill
**File**: `~/.claude/skills/agent-teams.md`
- Command: `/agent-teams` or `agent-teams`
- Displays quick reference with examples
- Decision tree for teams vs subagents
- Common patterns (code review, bug investigation, architecture)
- Key commands and troubleshooting

### 7. Integration Test
**File**: `~/.claude/test-agent-teams.sh`
- Verifies environment variable
- Checks hook registration
- Tests hook execution
- Validates documentation
- Confirms CLAUDE.md update

## How It Works

### Automatic Flow

1. **User submits prompt** → Triggers UserPromptSubmit hook
2. **Hook analyzes prompt** → Looks for parallel coordination indicators
3. **Context injected** → Guidance appears in system message if appropriate
4. **Claude receives context** → Knows when/how to suggest agent teams
5. **User creates team** → Natural language team creation
6. **Teammates coordinate** → Direct communication via shared task list

### Example User Experience

**User**: "Create a team to review this PR from security, performance, and testing perspectives"

**Hook detects**: "multiple perspectives", "team"

**Injected context**:
```
<agent-teams-context>
Agent Teams Feature Available:
[Full guidance with syntax and examples]
</agent-teams-context>
```

**Claude responds**: Creates 3-person team with specialized roles

## Key Differentiators

### Agent Teams vs Task Subagents

| Aspect | Agent Teams | Task Subagents |
|--------|-------------|----------------|
| **Communication** | Inter-agent messaging | Report to main only |
| **Context** | Independent windows | Inherit main context |
| **Coordination** | Shared task list | Managed by main |
| **Use Case** | Parallel exploration | Focused searches |
| **Token Cost** | Higher (N instances) | Lower (shared context) |

## When to Use

### ✅ Agent Teams
- Multiple perspectives needed simultaneously
- Competing hypotheses to test in parallel
- Cross-layer coordination (frontend + backend + tests)
- Research requiring debate/challenge
- Independent modules benefiting from coordination

### ❌ Task Subagents (instead)
- Sequential tasks
- Simple searches (grep, find files)
- Single-file edits
- Focused work with clear path

## User Commands

### Create Team
```
Create an agent team with 3 teammates to [task]:
- Teammate 1: [specific role]
- Teammate 2: [specific role]
- Teammate 3: [specific role]
Have them coordinate and share findings.
```

### Monitor
```
What's the status of all teammates?
Show me the task list.
```

### Direct Communication
- **In-process mode**: Shift+Up/Down to select, type to message
- **Split panes**: Click into pane

### Cleanup
```
Ask all teammates to shut down.
Clean up the team.
```

## Technical Details

### Storage
```
~/.claude/teams/{team-name}/config.json    # Team configuration
~/.claude/tasks/{team-name}/                # Shared task list
```

### Components
- **Team Lead**: Main session (creates team, coordinates)
- **Teammates**: Independent Claude instances
- **Task List**: Shared work items (pending → in_progress → completed)
- **Mailbox**: Inter-agent messaging system

### Display Modes
- **In-process** (default): All teammates in main terminal
- **Split panes**: Each teammate in own pane (requires tmux or iTerm2)

## Token Considerations

⚠️ **Each teammate = separate Claude instance = higher token usage**

**Worth it for**:
- Critical architecture decisions
- Complex debugging
- Comprehensive reviews
- Multi-perspective research

**Not worth it for**:
- Routine tasks
- Simple searches
- Sequential work

## Testing

Run integration test:
```bash
~/.claude/test-agent-teams.sh
```

All checks should show ✅:
1. Environment variable configured
2. Hook registered
3. Hook file executable
4. Hook executes successfully
5. Documentation created
6. CLAUDE.md updated

## Next Steps for Users

1. **Try it**: `claude` → "Create an agent team with 3 members to review this code"
2. **Read docs**: `cat ~/.claude/docs/AGENT_TEAMS_GUIDE.md`
3. **Quick ref**: `/agent-teams` skill command
4. **Experiment**: Start with research/review tasks before complex implementation

## Integration Benefits

1. **Automatic guidance**: Hook injects context when appropriate (no manual lookup)
2. **Seamless workflow**: Works alongside existing Task subagents
3. **Genius DNA integration**: Teammates inherit project context and skills
4. **Memory system**: All teammates access central supermemory
5. **Documentation**: Comprehensive guide with examples
6. **Testing**: Validation script ensures everything works

## Current Limitations (Experimental Feature)

- No session resumption with in-process teammates
- Task status can lag (manual update if stuck)
- One team per session
- No nested teams
- Lead role fixed (can't transfer)
- Split panes not in VS Code terminal

## Files Modified/Created

**Modified**:
- `/Users/spartan/.claude/settings.json` (env var + hook registration)
- `/Users/spartan/.claude/CLAUDE.md` (agent teams section)

**Created**:
- `/Users/spartan/.claude/hooks/agent-teams-context.py` (auto-injection hook)
- `/Users/spartan/.claude/docs/AGENT_TEAMS_GUIDE.md` (comprehensive guide)
- `/Users/spartan/.claude/skills/agent-teams.md` (quick reference skill)
- `/Users/spartan/.claude/test-agent-teams.sh` (integration test)
- `/Users/spartan/.claude/AGENT_TEAMS_INTEGRATION_SUMMARY.md` (this file)

## References

- **Official Docs**: https://code.claude.com/docs/en/agent-teams
- **Release**: TechCrunch Feb 5, 2026 - https://techcrunch.com/2026/02/05/anthropic-releases-opus-4-6-with-new-agent-teams/
- **Feature Overview**: https://www.anthropic.com/news/claude-opus-4-6

---

**Integration Complete**: ✅ All components installed and tested
**Status**: Ready for immediate use
**Command**: `claude` → "Create an agent team..."
