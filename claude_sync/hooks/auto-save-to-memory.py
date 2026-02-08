#!/usr/bin/env python3
"""
Auto-Save to Supermemory Hook
Automatically saves important changes to Supermemory in real-time

Triggers on: PostToolUse (after Edit, Write, Bash)
Philosophy: Capture important work immediately, don't wait for session end
"""

import sys
import json
import requests
from datetime import datetime
from pathlib import Path

SUPERMEMORY_API = "http://localhost:3456"
HOOK_LOG = Path.home() / ".claude" / "logs" / "auto_save_memory.log"


def log(message):
    """Log to file"""
    HOOK_LOG.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HOOK_LOG, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def should_save_to_memory(tool_name, file_path):
    """Determine if this change is important enough to save to memory"""

    # Always save these critical files
    important_files = [
        "autonomous_organizer.py",
        "autonomous_monitor.py",
        "autonomous_ngrok.py",
        "settings.json",
        "CLAUDE.md",
        "MEMORY.md",
        "API_REGISTRY.json",
        "DIRECTORY_INDEX.json",
    ]

    # Always save to important directories
    important_dirs = [
        "autonomous/",
        "hooks/",
        "docs/",
        ".plist",  # LaunchAgent files
    ]

    file_name = Path(file_path).name if file_path else ""

    # Check if important file
    if any(important in file_name for important in important_files):
        return True

    # Check if important directory
    if any(important in file_path for important in important_dirs):
        return True

    # Save new autonomous systems
    if "autonomous" in file_path.lower() and tool_name == "Write":
        return True

    # Save installation scripts
    if "install" in file_name and file_name.endswith(".sh"):
        return True

    return False


def extract_summary(tool_use_data):
    """Extract a summary of what was changed"""
    tool_name = tool_use_data.get("tool", "Unknown")
    params = tool_use_data.get("params", {})

    if tool_name == "Write":
        file_path = params.get("file_path", "unknown")
        content_preview = params.get("content", "")[:200]
        lines = len(params.get("content", "").split("\n"))
        return {
            "action": "Created file",
            "file": file_path,
            "details": f"New file with {lines} lines",
            "preview": content_preview
        }

    elif tool_name == "Edit":
        file_path = params.get("file_path", "unknown")
        old_str = params.get("old_string", "")[:100]
        new_str = params.get("new_string", "")[:100]
        return {
            "action": "Edited file",
            "file": file_path,
            "details": f"Changed: {old_str[:50]}... → {new_str[:50]}...",
            "preview": new_str[:200]
        }

    elif tool_name == "Bash":
        command = params.get("command", "unknown")
        description = params.get("description", "")
        return {
            "action": "Ran command",
            "command": command[:100],
            "details": description,
            "preview": command
        }

    return None


def save_to_supermemory(summary, tool_use_data):
    """Save important change to Supermemory"""
    try:
        # Build memory content
        content = f"{summary['action']}: {summary['file'] if 'file' in summary else summary.get('command', 'unknown')}"
        if summary.get('details'):
            content += f". {summary['details']}"

        # Add timestamp
        content += f" (Created: {datetime.now().strftime('%Y-%m-%d %H:%M')})"

        # Determine tags
        tags = ["auto_saved", "claude_code"]
        file_path = summary.get('file', summary.get('command', ''))

        if 'autonomous' in file_path.lower():
            tags.append("autonomous_system")
        if 'hook' in file_path.lower():
            tags.append("hooks")
        if 'organizer' in file_path.lower():
            tags.append("code_organization")
        if '.plist' in file_path:
            tags.append("launchagent")

        # Save to Supermemory
        payload = {
            "content": content,
            "containerTag": tags[0],  # Primary tag
            "metadata": {
                "tags": tags,
                "tool": tool_use_data.get("tool"),
                "file": summary.get('file', ''),
                "auto_saved": True
            }
        }

        response = requests.post(
            f"{SUPERMEMORY_API}/api/memory/save",
            json=payload,
            timeout=3
        )

        if response.status_code == 200:
            log(f"✅ Saved to memory: {content[:100]}")
            return True
        else:
            log(f"⚠️  Failed to save (status {response.status_code}): {content[:50]}")
            return False

    except Exception as e:
        log(f"❌ Error saving to memory: {e}")
        return False


def main():
    """Main hook function"""
    try:
        # Read hook input from stdin
        hook_input = sys.stdin.read()
        if not hook_input:
            return

        data = json.loads(hook_input)
        tool_use_data = data.get("toolUse", {})
        tool_name = tool_use_data.get("tool", "")
        params = tool_use_data.get("params", {})

        # Get file path
        file_path = params.get("file_path") or params.get("command", "")

        # Check if we should save this
        if not should_save_to_memory(tool_name, file_path):
            return

        # Extract summary
        summary = extract_summary(tool_use_data)
        if not summary:
            return

        # Save to Supermemory
        save_to_supermemory(summary, tool_use_data)

    except Exception as e:
        log(f"Hook error: {e}")


if __name__ == "__main__":
    main()
