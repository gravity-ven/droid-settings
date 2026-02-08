#!/usr/bin/env python3
"""
Ralph Wiggum State Controller

Manages the state of autonomous iteration loops for Claude Code.
Based on the Ralph Wiggum plugin pattern from Anthropic.

Enhanced with Evolution Engine integration for self-improving skills.

State file: ~/.claude/ralph/state.json
"""

import json
import os
import re
import fcntl
import sys
from collections import deque
from datetime import datetime
from typing import Optional, Dict, Any

RALPH_DIR = os.path.expanduser("~/.claude/ralph")
STATE_FILE = os.path.join(RALPH_DIR, "state.json")
LOG_FILE = os.path.join(RALPH_DIR, "iterations.log")
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB
MAX_LOG_LINES = 5000

# Evolution integration
EVOLUTION_DIR = os.path.expanduser("~/.claude/evolution")
sys.path.insert(0, EVOLUTION_DIR)


def ensure_ralph_dir():
    """Ensure the Ralph directory exists."""
    os.makedirs(RALPH_DIR, exist_ok=True)


def get_state() -> Optional[Dict[str, Any]]:
    """Get current Ralph loop state with file locking."""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                return json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except (json.JSONDecodeError, IOError):
        return None


def atomic_write_state(state: Dict[str, Any]) -> bool:
    """Atomically write state with exclusive file locking."""
    ensure_ralph_dir()
    try:
        with open(STATE_FILE, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(state, f, indent=2)
                return True
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except IOError:
        return False


def check_completion_promise(transcript: str, promise: str) -> bool:
    """Check for completion promise with XML tag pattern or word boundary."""
    if not promise:
        return False

    # Check for XML tag pattern first (preferred)
    xml_pattern = f"<promise>{re.escape(promise)}</promise>"
    if re.search(xml_pattern, transcript):
        return True

    # Fallback: Check for standalone word match (case-sensitive)
    word_pattern = r'\b' + re.escape(promise) + r'\b'
    return bool(re.search(word_pattern, transcript))


def start_loop(
    prompt: str,
    max_iterations: int = 50,
    completion_promise: str = "COMPLETE"
) -> Dict[str, Any]:
    """
    Start a new Ralph loop.

    Args:
        prompt: The task prompt to iterate on
        max_iterations: Maximum number of iterations before stopping
        completion_promise: Text that signals task completion

    Returns:
        The new state object
    """
    ensure_ralph_dir()

    state = {
        "active": True,
        "prompt": prompt,
        "max_iterations": max_iterations,
        "completion_promise": completion_promise,
        "current_iteration": 0,
        "started_at": datetime.now().isoformat(),
        "last_iteration_at": None,
        "history": []
    }

    atomic_write_state(state)
    log_event("LOOP_STARTED", f"Max iterations: {max_iterations}, Promise: '{completion_promise}'")

    # Auto-spawn TUI if in tmux
    auto_spawn_tui()

    return state


def auto_spawn_tui():
    """Automatically spawn Ralph TUI in tmux if available."""
    import subprocess

    # Check if in tmux
    if not os.environ.get("TMUX"):
        return

    ralph_tui_dir = os.path.expanduser("~/.claude/plugins/ralph-tui")
    if not os.path.exists(ralph_tui_dir):
        return

    try:
        # Check if ralph-tui pane already exists
        result = subprocess.run(
            ["tmux", "list-panes", "-F", "#{pane_title}"],
            capture_output=True, text=True, timeout=2
        )
        if "ralph-tui" in result.stdout:
            return  # Already spawned

        # Spawn TUI in right pane
        subprocess.run(
            ["tmux", "split-window", "-h", "-l", "45", "-c", ralph_tui_dir,
             "bun", "run", "src/cli.ts", "run"],
            timeout=5
        )
        subprocess.run(["tmux", "select-pane", "-T", "ralph-tui"], timeout=2)
        subprocess.run(["tmux", "select-pane", "-L"], timeout=2)  # Return focus
        log_event("TUI_SPAWNED", "Ralph TUI auto-spawned in tmux pane")
    except Exception as e:
        log_event("TUI_SPAWN_ERROR", str(e))


def increment_iteration() -> Dict[str, Any]:
    """
    Increment the iteration counter and update state.

    Returns:
        Updated state object
    """
    state = get_state()
    if not state:
        return None

    state["current_iteration"] += 1
    state["last_iteration_at"] = datetime.now().isoformat()
    state["history"].append({
        "iteration": state["current_iteration"],
        "timestamp": state["last_iteration_at"]
    })

    atomic_write_state(state)
    log_event("ITERATION", f"Iteration {state['current_iteration']}/{state['max_iterations']}")

    return state


def check_completion(transcript_summary: str = "") -> Dict[str, Any]:
    """
    Check if the loop should complete.

    Args:
        transcript_summary: Summary of the current transcript

    Returns:
        Dict with 'should_continue', 'reason', and 'prompt' keys
    """
    state = get_state()

    if not state or not isinstance(state, dict):
        return {
            "should_continue": False,
            "reason": "Invalid or missing state",
            "prompt": None
        }

    if not state.get("active"):
        return {
            "should_continue": False,
            "reason": "No active Ralph loop",
            "prompt": None
        }

    # Validate required fields
    required = ["current_iteration", "max_iterations", "prompt"]
    missing = [f for f in required if f not in state]
    if missing:
        return {
            "should_continue": False,
            "reason": f"Corrupted state: missing {missing}",
            "prompt": None
        }

    # Check max iterations
    if state["current_iteration"] >= state["max_iterations"]:
        cancel_loop("max_iterations_reached", transcript_summary)
        return {
            "should_continue": False,
            "reason": f"Maximum iterations ({state['max_iterations']}) reached",
            "prompt": None
        }

    # Check completion promise using improved detection
    promise = state.get("completion_promise", "")
    if check_completion_promise(transcript_summary, promise):
        cancel_loop("completion_promise_detected", transcript_summary)
        return {
            "should_continue": False,
            "reason": f"Completion promise '{promise}' detected",
            "prompt": None
        }

    # Continue the loop
    increment_iteration()
    return {
        "should_continue": True,
        "reason": f"Continuing iteration {state['current_iteration'] + 1}/{state['max_iterations']}",
        "prompt": state["prompt"]
    }


def trigger_evolution_evaluation(transcript: str, state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Trigger evolution evaluation after loop completion.

    Evaluates the execution and updates skill metrics for self-improvement.
    """
    try:
        from evolution_engine import trigger_evaluation, run_evolution_cycle

        # Evaluate this execution
        evaluation = trigger_evaluation(transcript)

        # Store evaluation in state
        if "evaluations" not in state:
            state["evaluations"] = []
        state["evaluations"].append({
            "iteration": state.get("current_iteration", 0),
            "fitness": evaluation.get("fitness_score", 0),
            "timestamp": datetime.now().isoformat()
        })

        # Persist the updated state with evaluations
        atomic_write_state(state)

        # If loop is ending and fitness is low, trigger evolution
        if evaluation.get("fitness_score", 1.0) < 0.5:
            log_event("EVOLUTION_TRIGGERED", f"Low fitness: {evaluation['fitness_score']}")

        return evaluation
    except ImportError:
        log_event("EVOLUTION_SKIP", "Evolution engine not available")
        return None
    except Exception as e:
        log_event("EVOLUTION_ERROR", str(e))
        return None


def cancel_loop(reason: str = "user_cancelled", transcript: str = "") -> bool:
    """
    Cancel the current Ralph loop.

    Args:
        reason: Reason for cancellation
        transcript: Optional transcript for evolution evaluation

    Returns:
        True if loop was cancelled, False if no active loop
    """
    state = get_state()
    if not state:
        return False

    # Trigger evolution evaluation before ending
    if transcript and reason in ["completion_promise_detected", "max_iterations_reached"]:
        evaluation = trigger_evolution_evaluation(transcript, state)
        if evaluation:
            state["final_evaluation"] = evaluation

    state["active"] = False
    state["ended_at"] = datetime.now().isoformat()
    state["end_reason"] = reason

    atomic_write_state(state)
    log_event("LOOP_ENDED", f"Reason: {reason}, Iterations: {state.get('current_iteration', 0)}")

    # Auto-close TUI after a delay (let user see final state)
    # Note: TUI stays open to show final status, user can close with 'q'

    return True


def auto_close_tui():
    """Close Ralph TUI pane if it exists."""
    import subprocess

    if not os.environ.get("TMUX"):
        return

    try:
        result = subprocess.run(
            ["tmux", "list-panes", "-F", "#{pane_id}:#{pane_title}"],
            capture_output=True, text=True, timeout=2
        )
        for line in result.stdout.strip().split("\n"):
            if ":" in line:
                pane_id, title = line.split(":", 1)
                if title == "ralph-tui":
                    subprocess.run(["tmux", "kill-pane", "-t", pane_id], timeout=2)
                    log_event("TUI_CLOSED", "Ralph TUI pane closed")
                    return
    except Exception as e:
        log_event("TUI_CLOSE_ERROR", str(e))


def get_status() -> Dict[str, Any]:
    """Get human-readable status of the Ralph loop."""
    state = get_state()

    if not state:
        return {
            "active": False,
            "message": "No Ralph loop configured"
        }

    if not state.get("active"):
        return {
            "active": False,
            "message": f"Loop ended: {state.get('end_reason', 'unknown')}",
            "total_iterations": state.get("current_iteration", 0),
            "started_at": state.get("started_at"),
            "ended_at": state.get("ended_at")
        }

    return {
        "active": True,
        "message": f"Loop active: iteration {state['current_iteration']}/{state['max_iterations']}",
        "current_iteration": state["current_iteration"],
        "max_iterations": state["max_iterations"],
        "completion_promise": state["completion_promise"],
        "started_at": state["started_at"],
        "prompt_preview": state["prompt"][:100] + "..." if len(state["prompt"]) > 100 else state["prompt"]
    }


def log_event(event_type: str, message: str):
    """Log a Ralph event with automatic log rotation."""
    ensure_ralph_dir()
    timestamp = datetime.now().isoformat()

    # Check file size and rotate if needed
    if os.path.exists(LOG_FILE):
        try:
            size = os.path.getsize(LOG_FILE)
            if size > MAX_LOG_SIZE:
                # Keep last N lines
                with open(LOG_FILE, "r") as f:
                    lines = deque(f, maxlen=MAX_LOG_LINES)
                with open(LOG_FILE, "w") as f:
                    f.writelines(lines)
        except IOError:
            pass  # Continue logging even if rotation fails

    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} | {event_type} | {message}\n")


if __name__ == "__main__":
    # CLI interface for testing
    import sys

    if len(sys.argv) < 2:
        print(json.dumps(get_status(), indent=2))
    elif sys.argv[1] == "status":
        print(json.dumps(get_status(), indent=2))
    elif sys.argv[1] == "cancel":
        result = cancel_loop("cli_cancel")
        print(f"Loop cancelled: {result}")
    elif sys.argv[1] == "start" and len(sys.argv) >= 3:
        prompt = sys.argv[2]
        max_iter = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        promise = sys.argv[4] if len(sys.argv) > 4 else "COMPLETE"
        state = start_loop(prompt, max_iter, promise)
        print(json.dumps(state, indent=2))
    else:
        print("Usage: ralph_state.py [status|cancel|start <prompt> [max_iter] [promise]]")
