#!/usr/bin/env python3
"""
Post-Tool-Use Hook: Automatic Knowledge Sync & Self-Modification Detection
Activates Level 7 (collective intelligence) and Level 9 (self-modification) automatically.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import hashlib

def extract_learning_pattern(tool_name, tool_input, tool_output, success):
    """Extract reusable patterns from successful operations"""
    if not success:
        return None

    learning = None

    # Code patterns
    if tool_name in ["Edit", "Write"] and success:
        learning = {
            "type": "code_pattern",
            "tool": tool_name,
            "success": True,
            "timestamp": datetime.utcnow().isoformat()
        }

    # Search patterns
    if tool_name in ["Grep", "Glob"] and "pattern" in str(tool_input):
        learning = {
            "type": "search_pattern",
            "tool": tool_name,
            "pattern": str(tool_input).get("pattern", ""),
            "timestamp": datetime.utcnow().isoformat()
        }

    # Command patterns
    if tool_name == "Bash" and success:
        learning = {
            "type": "command_pattern",
            "tool": tool_name,
            "success": True,
            "timestamp": datetime.utcnow().isoformat()
        }

    return learning

def sync_to_collective(learning):
    """Level 7: Sync learning to collective intelligence"""
    if not learning:
        return

    collective_log = Path.home() / ".agent-collective" / "learnings.jsonl"
    collective_log.parent.mkdir(parents=True, exist_ok=True)

    with open(collective_log, "a") as f:
        f.write(json.dumps(learning) + "\n")

def detect_self_modification(tool_name, tool_input):
    """Level 9: Detect if instructions were modified"""
    if tool_name not in ["Edit", "Write"]:
        return False

    file_path = str(tool_input.get("file_path", ""))

    # Check if critical instruction files were modified
    instruction_files = [
        "CLAUDE.md",
        ".claude/CLAUDE.md",
        "AGENT_INSTRUCTIONS.md",
        ".claudeconfig",
        "settings.json"
    ]

    for inst_file in instruction_files:
        if inst_file in file_path:
            return True

    return False

def log_self_modification(file_path, timestamp):
    """Track self-modifications for Level 9"""
    mod_log = Path.home() / ".agent-daemon" / "logs" / "self_modifications.jsonl"
    mod_log.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": timestamp,
        "file": file_path,
        "type": "instruction_modification"
    }

    with open(mod_log, "a") as f:
        f.write(json.dumps(entry) + "\n")

def accumulate_for_goal_discovery(tool_name, success):
    """Level 10: Accumulate usage patterns for emergent goal discovery"""
    pattern_file = Path.home() / ".agent-daemon" / "logs" / "usage_patterns.jsonl"
    pattern_file.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "tool": tool_name,
        "success": success
    }

    with open(pattern_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


def record_dr_zero_result(tool_name, tool_input, tool_output, success):
    """Record task result in Dr. Zero evolution system"""
    try:
        # Import evolution engine
        sys.path.insert(0, str(Path.home() / ".claude" / "evolution"))
        from dr_zero_engine import get_engine, Domain

        engine = get_engine()

        # Build task description from tool context
        task_desc = f"{tool_name}"
        if isinstance(tool_input, dict):
            if "file_path" in tool_input:
                task_desc += f" {tool_input['file_path']}"
            elif "command" in tool_input:
                task_desc += f" {tool_input['command'][:50]}"
            elif "pattern" in tool_input:
                task_desc += f" pattern:{tool_input['pattern']}"

        # Classify domain
        context = {"available_tools": [tool_name]}
        domain = engine.classify_task_domain(task_desc, context)

        if not domain:
            return

        # Calculate score (0-10 scale)
        score = 8.0 if success else 3.0

        # Extract approach
        approach = f"{tool_name} execution"
        if isinstance(tool_input, dict) and "description" in tool_input:
            approach = tool_input["description"][:100]

        # Record result
        from dr_zero_engine import record_task_result
        record_task_result(domain.value, task_desc, success, score, approach)

    except Exception:
        # Silently fail - evolution is enhancement, not critical path
        pass

def main():
    # Read tool result from stdin
    try:
        context = json.loads(sys.stdin.read())
        tool_name = context.get("toolName", "")
        tool_input = context.get("toolInput", {})
        tool_output = context.get("toolOutput", "")
        success = not context.get("isError", False)
    except:
        # Fallback
        tool_name = os.environ.get("TOOL_NAME", "unknown")
        tool_input = {}
        tool_output = ""
        success = True

    # Extract learning pattern
    learning = extract_learning_pattern(tool_name, tool_input, tool_output, success)

    # Level 7: Sync to collective intelligence
    sync_to_collective(learning)

    # Level 9: Detect self-modification
    if detect_self_modification(tool_name, tool_input):
        file_path = tool_input.get("file_path", "unknown")
        log_self_modification(file_path, datetime.utcnow().isoformat())

    # Level 10: Accumulate for emergent goal discovery
    accumulate_for_goal_discovery(tool_name, success)

    # Dr. Zero: Record task result in evolution system
    record_dr_zero_result(tool_name, tool_input, tool_output, success)

    sys.exit(0)

if __name__ == "__main__":
    main()
