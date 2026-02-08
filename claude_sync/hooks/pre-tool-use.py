#!/usr/bin/env python3
"""
Pre-Tool-Use Hook: Intelligent Task Analysis & Autonomous Orchestration
Activates Levels 6-10 transparently based on task complexity.
Includes FAST Computer Automation for ALL CLI agents.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add fast automation to path for all agents
sys.path.insert(0, str(Path.home() / '.claude/agents'))

def detect_computer_automation(tool_name, tool_input):
    """
    Detect ANY computer automation task (not just browser)
    Returns: (needs_automation, task_category, automation_type, confidence)
    """
    input_str = str(tool_input).lower()

    # COMPLETE COMPUTER AUTOMATION - All categories
    automation_patterns = {
        # Desktop application control
        'app_control': {
            'keywords': ['open app', 'launch', 'quit', 'close app', 'switch to', 'minimize', 'maximize'],
            'type': 'desktop',
            'confidence': 'high'
        },
        # File system operations
        'file_operations': {
            'keywords': ['drag file', 'drop file', 'move file', 'copy file', 'rename file', 'delete file',
                        'open file', 'save file', 'open folder', 'finder', 'explorer'],
            'type': 'desktop',
            'confidence': 'high'
        },
        # Mouse actions (anywhere on screen)
        'mouse_control': {
            'keywords': ['click', 'double-click', 'right-click', 'hover', 'drag', 'drop',
                        'mouse', 'cursor', 'move to', 'select'],
            'type': 'desktop',
            'confidence': 'high'
        },
        # Keyboard input (any app)
        'keyboard_input': {
            'keywords': ['type', 'press key', 'keyboard', 'shortcut', 'enter', 'escape',
                        'copy', 'paste', 'cut', 'undo', 'redo'],
            'type': 'desktop',
            'confidence': 'high'
        },
        # System navigation
        'system_navigation': {
            'keywords': ['settings', 'preferences', 'system', 'menu', 'menu bar', 'dock',
                        'notification', 'control center'],
            'type': 'desktop',
            'confidence': 'high'
        },
        # Window management
        'window_management': {
            'keywords': ['window', 'fullscreen', 'split screen', 'tab', 'workspace'],
            'type': 'desktop',
            'confidence': 'medium'
        },
        # Browser automation (existing)
        'browser': {
            'keywords': ['screenshot', 'capture screen', 'navigate to', 'open browser',
                        'click button', 'fill form', 'web scraping', 'website', 'url'],
            'type': 'browser',
            'confidence': 'high'
        },
        # UI testing
        'ui_testing': {
            'keywords': ['test ui', 'verify', 'check element', 'validate', 'automated test'],
            'type': 'desktop',
            'confidence': 'high'
        }
    }

    # Check all patterns
    for category, pattern in automation_patterns.items():
        for keyword in pattern['keywords']:
            if keyword in input_str:
                return (True, category, pattern['type'], pattern['confidence'])

    # Check tool-specific patterns
    if tool_name == "Bash":
        # System commands that might need GUI automation
        gui_commands = ['open', 'xdg-open', 'start', 'osascript']
        if any(cmd in input_str for cmd in gui_commands):
            return (True, 'system_command', 'desktop', 'medium')

    return (False, None, None, None)

def execute_fast_automation(task_description, category):
    """
    Execute automation INSTANTLY using fast automation system
    No queueing - immediate execution
    Returns: result
    """
    try:
        from fast_automation import FastAutomation

        # Create fast automation instance
        auto = FastAutomation(fast_mode=True)

        # Parse task and execute
        result = auto.execute_command(task_description)

        # Log execution
        log_file = Path.home() / '.claude/logs/fast_automation.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} | {category} | {task_description} | {result}\n")

        return result
    except Exception as e:
        # Fail silently
        return None

def queue_computer_automation(task_description, category, automation_type):
    """
    Queue complete computer automation task
    Supports: desktop actions, browser, files, apps, system
    Returns: task_id
    """
    try:
        # FAST MODE: Try to execute immediately first
        result = execute_fast_automation(task_description, category)
        if result:
            return result

        # Fallback: Queue for background processing
        # Generate task ID
        task_id = f"auto-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Create task object with automation details
        task = {
            'id': task_id,
            'type': 'complete_computer_automation',  # New type
            'category': category,  # app_control, mouse_control, browser, etc.
            'automation_type': automation_type,  # 'desktop' or 'browser'
            'description': task_description,
            'requires_human_movement': False,  # FAST mode (0.3s)
            'natural_cursor': True,  # Still smooth
            'triggered_by': 'pre_tool_use_hook',
            'max_steps': 50,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Add to queue
        queue_file = Path.home() / '.claude/agents/task_queue.json'
        queue_file.parent.mkdir(parents=True, exist_ok=True)

        if queue_file.exists():
            try:
                queue = json.loads(queue_file.read_text())
            except:
                queue = []
        else:
            queue = []

        queue.append(task)
        queue_file.write_text(json.dumps(queue, indent=2))

        # Log the queue action with full details
        log_file = Path.home() / '.claude/logs/computer_automation.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} | Queued: {task_id} | Category: {category} | Type: {automation_type}\n")

        return task_id
    except Exception as e:
        # Fail silently - don't block tool execution
        return None

def analyze_task_complexity(tool_name, tool_input):
    """
    Determine cognitive level needed for this task.
    Returns: (level_needed, spawn_swarm, reasoning)
    """
    complexity_score = 0
    indicators = []

    # Level 6: Multi-agent swarm indicators
    swarm_keywords = ['explore', 'research', 'analyze multiple', 'compare', 'comprehensive', 'thorough']
    if any(kw in str(tool_input).lower() for kw in swarm_keywords):
        complexity_score += 2
        indicators.append("Multiple perspectives needed")

    # Check for parallel work opportunities
    if tool_name == "Task" and "explore" in str(tool_input).lower():
        complexity_score += 3
        indicators.append("Exploration task - swarm beneficial")

    # Large codebase operations
    if tool_name in ["Grep", "Glob"] and "**" in str(tool_input):
        complexity_score += 1
        indicators.append("Large-scale search")

    # Multi-file operations
    if tool_name == "Edit" or tool_name == "Write":
        complexity_score += 1

    # Determine level
    if complexity_score >= 4:
        return (6, True, "Task complexity warrants multi-agent swarm")
    elif complexity_score >= 2:
        return (5, False, "Complex single-agent task")
    else:
        return (4, False, "Standard operation")

def should_activate_daemon():
    """Check if background daemons should run (Level 8)"""
    daemon_flag = Path.home() / ".agent-daemon" / "next_run.txt"
    if daemon_flag.exists():
        next_run = daemon_flag.read_text().strip()
        if next_run == "now":
            return True
    return False

def log_task_analysis(level, spawn_swarm, reasoning, tool_name):
    """Log task analysis for Level 10 emergent goal discovery"""
    log_file = Path.home() / ".agent-daemon" / "logs" / "task_analysis.jsonl"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "tool": tool_name,
        "level_needed": level,
        "spawn_swarm": spawn_swarm,
        "reasoning": reasoning
    }

    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

def main():
    # Read tool context from stdin
    try:
        context = json.loads(sys.stdin.read())
        tool_name = context.get("toolName", "")
        tool_input = context.get("toolInput", {})
    except:
        # Fallback if no context provided
        tool_name = os.environ.get("TOOL_NAME", "unknown")
        tool_input = {}

    # UNIVERSAL FAST AUTOMATION - DEFAULT for ALL computer tasks (Level 7)
    # Works with: ANY app, browser, system, desktop - EVERYTHING
    needs_automation, category, automation_type, confidence = detect_computer_automation(tool_name, tool_input)

    if needs_automation:
        # INSTANT EXECUTION (default behavior for all CLI agents)
        if confidence in ['high', 'medium']:  # Execute for high and medium confidence
            task_description = str(tool_input)

            # DEFAULT: Fast automation (instant, universal)
            result = execute_fast_automation(task_description, category)

            if result:
                # Log successful fast automation
                log_file = Path.home() / ".agent-daemon" / "logs" / "fast_automation_activations.jsonl"
                log_file.parent.mkdir(parents=True, exist_ok=True)

                activation = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "result": result,
                    "category": category,
                    "automation_type": automation_type,
                    "confidence": confidence,
                    "tool": tool_name,
                    "execution_mode": "fast_instant",  # Default mode
                    "triggered_by": "pre_tool_use_hook",
                    "cli_agent": "all"  # Available to ALL agents
                }

                with open(log_file, "a") as f:
                    f.write(json.dumps(activation) + "\n")

    # Analyze task complexity
    level, spawn_swarm, reasoning = analyze_task_complexity(tool_name, tool_input)

    # Log for emergent goal discovery (Level 10)
    log_task_analysis(level, spawn_swarm, reasoning, tool_name)

    # Level 8: Check if daemons should activate
    if should_activate_daemon():
        daemon_script = Path.home() / ".claude" / "autonomous_orchestrator.py"
        if daemon_script.exists():
            os.system(f"python3 {daemon_script} &")

    # Level 6: If swarm needed, signal it (implementation will spawn agents)
    if spawn_swarm:
        swarm_flag = Path.home() / ".agent-daemon" / "swarm_requested.json"
        swarm_flag.write_text(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "tool": tool_name,
            "reasoning": reasoning
        }))

    # Success - tool proceeds
    sys.exit(0)

if __name__ == "__main__":
    main()
