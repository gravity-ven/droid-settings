#!/usr/bin/env python3
"""
SessionStart Hook - Initializes session context.

This hook runs when a Claude Code session starts and can:
1. Load development context (git status, recent changes)
2. Set environment variables
3. Check system health
4. Load user preferences

Exit codes:
- 0: Success (stdout added as context)
- 2: Block with error
- Other: Non-blocking error
"""

import json
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
MEMORY_FILE = CLAUDE_DIR / "memory" / "knowledge.json"
USER_CONTEXT_FILE = CLAUDE_DIR / "memory" / "user_context.md"
MEMORY_LOG_FILE = CLAUDE_DIR / "memory" / "memory_log.json"
GENIUS_LOADER = CLAUDE_DIR / "genius_loader.py"
GENIUS_KNOWLEDGE_DIR = CLAUDE_DIR / "knowledge"
CANVAS_ROOT = CLAUDE_DIR / "plugins" / "claude-canvas"

def get_git_context() -> dict:
    """Get current git status and recent activity."""
    context = {}

    try:
        # Check if in a git repo
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return {"git": "Not a git repository"}

        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5
        )
        context["branch"] = result.stdout.strip()

        # Get status summary
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5
        )
        status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
        context["uncommitted_changes"] = len(status_lines)

        # Get recent commits (last 3)
        result = subprocess.run(
            ["git", "log", "--oneline", "-3"],
            capture_output=True,
            text=True,
            timeout=5
        )
        context["recent_commits"] = result.stdout.strip().split('\n') if result.stdout.strip() else []

    except Exception as e:
        context["git_error"] = str(e)

    return context

def check_system_health() -> dict:
    """Check system health indicators."""
    health = {}

    try:
        # Check disk space
        result = subprocess.run(
            ["df", "-h", "/"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 5:
                    health["disk_usage"] = parts[4]

        # Check if common services are running
        services_to_check = ["postgres", "redis", "docker"]
        running_services = []

        for service in services_to_check:
            result = subprocess.run(
                ["pgrep", "-x", service],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                running_services.append(service)

        health["running_services"] = running_services

    except Exception as e:
        health["error"] = str(e)

    return health

def clear_session_logs():
    """Clear logs from previous session."""
    log_dir = os.path.expanduser("~/.claude/logs")
    files_to_clear = [
        "modified_files.log"  # Start fresh each session
    ]

    for filename in files_to_clear:
        filepath = os.path.join(log_dir, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                pass

def load_learnings() -> dict:
    """Load learnings from knowledge graph for session context."""
    learnings = {
        "error_patterns": [],
        "effective_commands": [],
        "rules": [],
        "insights": [],
        "recent_learnings": []
    }

    if not MEMORY_FILE.exists():
        return learnings

    try:
        with open(MEMORY_FILE, "r") as f:
            knowledge = json.load(f)

        entities = knowledge.get("entities", [])

        for entity in entities:
            entity_type = entity.get("entityType", "")
            observations = entity.get("observations", [])

            if entity_type == "error-pattern":
                # Extract error->fix pattern
                error_cmd = ""
                fix_cmd = ""
                for obs in observations:
                    if obs.startswith("Error command:"):
                        error_cmd = obs.replace("Error command:", "").strip()
                    elif obs.startswith("Fix command:"):
                        fix_cmd = obs.replace("Fix command:", "").strip()
                if error_cmd and fix_cmd:
                    learnings["error_patterns"].append(f"{error_cmd} -> {fix_cmd}")

            elif entity_type == "learning":
                # Categorize learnings
                category = ""
                main_obs = observations[0] if observations else ""
                for obs in observations:
                    if obs.startswith("Category:"):
                        category = obs.replace("Category:", "").strip()
                        break

                if category == "effective-command":
                    learnings["effective_commands"].append(main_obs)
                elif category == "rule":
                    learnings["rules"].append(main_obs)
                elif category in ["insight", "discovery"]:
                    learnings["insights"].append(main_obs)

        # Get 5 most recent learnings for quick reference
        sorted_entities = sorted(
            [e for e in entities if e.get("entityType") in ["learning", "error-pattern"]],
            key=lambda x: next((o for o in x.get("observations", []) if "Learned:" in o), ""),
            reverse=True
        )[:5]

        for entity in sorted_entities:
            obs = entity.get("observations", [])
            if obs:
                learnings["recent_learnings"].append(f"{entity.get('name', 'unknown')}: {obs[0][:60]}")

    except Exception as e:
        learnings["load_error"] = str(e)

    return learnings

def format_learnings_context(learnings: dict) -> str:
    """Format learnings into readable context string."""
    lines = []

    if learnings.get("error_patterns"):
        lines.append("**Known Error->Fix Patterns:**")
        for p in learnings["error_patterns"][:5]:
            lines.append(f"  - {p}")

    if learnings.get("rules"):
        lines.append("**Rules Learned:**")
        for r in learnings["rules"][:5]:
            lines.append(f"  - {r}")

    if learnings.get("insights"):
        lines.append("**Insights:**")
        for i in learnings["insights"][:3]:
            lines.append(f"  - {i}")

    if learnings.get("recent_learnings"):
        lines.append("**Recent Learnings:**")
        for r in learnings["recent_learnings"]:
            lines.append(f"  - {r}")

    return "\n".join(lines) if lines else "No prior learnings loaded."


def load_genius_context() -> dict:
    """Load Genius DNA context for enhanced coding."""
    genius = {
        "available": False,
        "metrics": {},
        "top_skills": [],
        "principles": [],
        "domains": {}
    }

    # Check if genius knowledge exists
    skill_file = GENIUS_KNOWLEDGE_DIR / "skill_registry.json"
    principles_file = GENIUS_KNOWLEDGE_DIR / "first_principles.json"
    exp_file = GENIUS_KNOWLEDGE_DIR / "exponential_skills.json"

    if not skill_file.exists():
        return genius

    genius["available"] = True

    try:
        # Load skills
        with open(skill_file, "r") as f:
            skills_data = json.load(f)

        skills_list = []
        raw_skills = skills_data.get("skills", [])

        # Handle both list and dict format
        if isinstance(raw_skills, list):
            for skill in raw_skills:
                skills_list.append({
                    "name": skill.get("name", ""),
                    "domain": skill.get("domain", "unknown"),
                    "power": skill.get("power", 1.0),
                    "level": skill.get("level", 1)
                })
        else:
            for skill_id, skill in raw_skills.items():
                skills_list.append({
                    "name": skill.get("name", skill_id),
                    "domain": skill.get("domain", "unknown"),
                    "power": skill.get("power", 1.0)
                })

        # Sort by power and get top 10
        skills_list.sort(key=lambda x: x.get("power", 1) * x.get("level", 1), reverse=True)
        genius["top_skills"] = skills_list[:10]

        # Count by domain
        for skill in skills_list:
            domain = skill.get("domain", "unknown")
            genius["domains"][domain] = genius["domains"].get(domain, 0) + 1

        # Load principles
        if principles_file.exists():
            with open(principles_file, "r") as f:
                principles_data = json.load(f)

            principles_list = principles_data.get("principles", [])
            if isinstance(principles_list, list):
                for p in principles_list[:5]:
                    genius["principles"].append({
                        "content": p.get("content", "")[:100],
                        "domain": p.get("domain", "general")
                    })
            else:
                for pid, p in list(principles_list.items())[:5]:
                    genius["principles"].append({
                        "content": p.get("content", "")[:100],
                        "domain": p.get("domain", "general")
                    })

        # Load metrics (exponential file may be large/corrupted)
        genius["metrics"] = {
            "total_skills": len(skills_list),
            "synergies": 0,
            "compounds": 0,
            "growth_factor": 1.0
        }

        try:
            if exp_file.exists():
                with open(exp_file, "r") as f:
                    exp_data = json.load(f)

                genius["metrics"]["synergies"] = len(exp_data.get("synergies", {}))
                genius["metrics"]["compounds"] = len(exp_data.get("compounds", {}))
                genius["metrics"]["growth_factor"] = exp_data.get("global_multiplier", 1.0)
        except Exception:
            pass  # Skip if exponential file is corrupted

    except Exception as e:
        genius["error"] = str(e)

    return genius


def check_canvas_status() -> dict:
    """Check Claude Canvas availability and status."""
    canvas = {
        "available": False,
        "tmux_active": False,
        "canvas_types": [],
        "hint": ""
    }

    # Check if canvas is installed
    if CANVAS_ROOT.exists() and (CANVAS_ROOT / "package.json").exists():
        canvas["available"] = True
        canvas["canvas_types"] = ["calendar", "document", "flight"]

    # Check if in tmux session
    if os.environ.get("TMUX"):
        canvas["tmux_active"] = True
        canvas["hint"] = "Canvas ready. Use /canvas:calendar, /canvas:document, or /canvas:flight"
    else:
        canvas["hint"] = "For full canvas support, run: claude (auto-starts tmux)"

    return canvas


def load_extended_memory() -> dict:
    """Load extended user context from memory system."""
    memory = {
        "available": False,
        "profile": {},
        "recent_insights": [],
        "frequent_topics": [],
        "preferences": {}
    }

    # Load from memory log JSON
    if MEMORY_LOG_FILE.exists():
        try:
            with open(MEMORY_LOG_FILE, "r") as f:
                log = json.load(f)

            memory["available"] = True

            # Get recent insights (last 5)
            insights = sorted(
                log.get("insights", []),
                key=lambda x: x.get("timestamp", ""),
                reverse=True
            )[:5]
            memory["recent_insights"] = [
                f"[{i.get('date')}] {i.get('topic')}: {i.get('insight')[:80]}"
                for i in insights
            ]

            # Get top topics
            topics = sorted(
                log.get("topics", []),
                key=lambda x: x.get("count", 0),
                reverse=True
            )[:5]
            memory["frequent_topics"] = [t.get("name") for t in topics]

            # Get preferences
            memory["preferences"] = log.get("preferences", {})

        except Exception as e:
            memory["error"] = str(e)

    # Also check if user_context.md exists for profile info
    if USER_CONTEXT_FILE.exists():
        memory["context_file"] = True

    return memory


def format_extended_memory(memory: dict) -> str:
    """Format extended memory for injection."""
    if not memory.get("available") and not memory.get("context_file"):
        return ""

    lines = ["## Extended Memory (User Context)"]

    if memory.get("frequent_topics"):
        lines.append(f"**Frequent Topics**: {', '.join(memory['frequent_topics'])}")

    if memory.get("recent_insights"):
        lines.append("**Recent Session Insights:**")
        for insight in memory["recent_insights"][:3]:
            lines.append(f"  - {insight}")

    if memory.get("preferences"):
        lines.append("**Known Preferences:**")
        for k, v in list(memory["preferences"].items())[:5]:
            lines.append(f"  - {k}: {v}")

    if memory.get("context_file"):
        lines.append("**Extended context**: ~/.claude/memory/user_context.md")

    return "\n".join(lines)


def format_genius_context(genius: dict) -> str:
    """Format genius context for injection."""
    if not genius.get("available"):
        return ""

    lines = ["## Genius DNA Context"]

    # Metrics summary
    metrics = genius.get("metrics", {})
    if metrics:
        lines.append(f"Skills: {metrics.get('total_skills', 0)} | " +
                    f"Synergies: {metrics.get('synergies', 0)} | " +
                    f"Growth: {metrics.get('growth_factor', 1.0):.1f}x")

    # Top domains
    domains = genius.get("domains", {})
    if domains:
        top_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)[:3]
        lines.append(f"Top Domains: {', '.join([d[0] for d in top_domains])}")

    # Top skills
    skills = genius.get("top_skills", [])
    if skills:
        lines.append("**Top Skills:**")
        for s in skills[:5]:
            lines.append(f"  - {s['name']} ({s['domain']})")

    # Principles
    principles = genius.get("principles", [])
    if principles:
        lines.append("**First Principles:**")
        for p in principles[:3]:
            lines.append(f"  - {p['content'][:80]}...")

    return "\n".join(lines)

def main():
    # Clear previous session logs
    clear_session_logs()

    # Gather context
    context = {
        "session_start": datetime.now().isoformat(),
        "working_directory": os.getcwd()
    }

    # Add git context
    git_context = get_git_context()
    if git_context:
        context["git"] = git_context

    # Add system health
    health = check_system_health()
    if health:
        context["system"] = health

    # Check for project-specific context files
    project_context_files = [
        "CLAUDE.md",
        ".claude/CLAUDE.md",
        "README.md"
    ]

    found_context_files = []
    for cf in project_context_files:
        if os.path.exists(cf):
            found_context_files.append(cf)

    if found_context_files:
        context["project_context_files"] = found_context_files

    # Load and include learnings from knowledge graph
    learnings = load_learnings()
    learnings_context = format_learnings_context(learnings)
    context["experiential_learnings"] = learnings

    # Load Genius DNA context
    genius = load_genius_context()
    genius_context = format_genius_context(genius)
    context["genius_dna"] = genius

    # Load Extended Memory (User Context)
    extended_memory = load_extended_memory()
    extended_memory_context = format_extended_memory(extended_memory)
    context["extended_memory"] = extended_memory

    # Check Canvas status
    canvas = check_canvas_status()
    context["canvas"] = canvas

    # Build full context string
    full_context = json.dumps(context, indent=2)
    full_context += "\n\n---\n## Prior Learnings\n" + learnings_context

    if extended_memory_context:
        full_context += "\n\n---\n" + extended_memory_context

    if genius_context:
        full_context += "\n\n---\n" + genius_context

    # Add canvas context
    if canvas.get("available"):
        full_context += "\n\n---\n## Canvas TUI\n"
        full_context += f"Status: {'Ready (tmux active)' if canvas.get('tmux_active') else 'Available (start tmux for spawning)'}\n"
        full_context += f"Types: {', '.join(canvas.get('canvas_types', []))}\n"
        full_context += f"Hint: {canvas.get('hint', '')}"

    # Output context for Claude
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": full_context
        }
    }

    print(json.dumps(output))
    sys.exit(0)

if __name__ == "__main__":
    main()
