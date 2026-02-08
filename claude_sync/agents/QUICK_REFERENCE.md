# MANUS Computer Use - Quick Reference

## ⚡ Quick Start

### Automatic (Just Use Natural Language)
```
"Take a screenshot of http://localhost:9000"
"Test the website and verify all links work"
"Navigate to GitHub and capture homepage"
```
→ MANUS triggers automatically via pre-hook

### Explicit MCP Tools
```python
# Available tools:
mcp__computer-use__run_computer_task
mcp__computer-use__computer_screenshot
mcp__computer-use__computer_click
mcp__computer-use__computer_type
mcp__computer-use__computer_key
```

### Manual Skill
```bash
/manus navigate https://example.com
/manus screenshot https://example.com /tmp/output.png
```

---

## 📊 Monitoring

```bash
# View activations
tail -f ~/.agent-daemon/logs/computer_use_activations.jsonl

# View queue
cat ~/.claude/agents/task_queue.json | python3 -m json.tool

# View results
cat ~/.claude/agents/results.json | python3 -m json.tool

# Service logs
tail -f ~/.claude/logs/manus_service.log
```

---

## 🧪 Testing

```bash
cd ~/.claude/agents && python3 test_manus_integration.py
```

Expected: 4/4 tests passed (100%)

---

## 🔧 Service Management

```bash
# Check status
ps aux | grep manus_service

# Restart
launchctl unload ~/Library/LaunchAgents/com.claude.manus-service.plist
launchctl load ~/Library/LaunchAgents/com.claude.manus-service.plist
```

---

## 📁 Key Files

- Pre-hook: `~/.claude/hooks/pre-tool-use.py`
- MCP Server: `~/.claude/agents/mcp_computer_use_server.js`
- Global Agent: `~/.claude/agents/global_computer_use.py`
- Settings: `~/.claude/settings.json` (line 137-140)
- Queue: `~/.claude/agents/task_queue.json`
- Results: `~/.claude/agents/results.json`

---

## ✅ Verification

```bash
# Test import
python3 -c "import sys; sys.path.insert(0, '~/.claude/agents'); from global_computer_use import get_computer_use; print('✅ Working')"

# Test MCP server
node ~/.claude/agents/mcp_computer_use_server.js --help
```

**Status**: ✅ Operational (Tested 2026-02-06)
