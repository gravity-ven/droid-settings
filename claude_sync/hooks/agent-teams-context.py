#!/usr/bin/env python3
"""
Agent Teams Context Hook - Injects context about when/how to use agent teams

Triggered by UserPromptSubmit hook to provide intelligent guidance about
using agent teams for parallel coordination vs subagents for focused work.
"""

import sys
import json
import re

def analyze_task_for_teams(prompt):
    """Analyze if the task would benefit from agent teams vs subagents."""

    # Keywords suggesting agent teams would be beneficial
    team_indicators = [
        # Parallel exploration
        'explore different', 'multiple perspectives', 'various approaches',
        'different angles', 'competing hypotheses', 'parallel investigation',

        # Research & review
        'review from', 'research multiple', 'investigate different',
        'analyze from different', 'comprehensive review',

        # Cross-domain work
        'frontend and backend', 'multiple layers', 'cross-cutting',
        'spanning multiple', 'full stack',

        # Team-like language
        'team', 'teammates', 'coordinate', 'collaborate',
        'discuss', 'debate', 'challenge each other',

        # Complex multi-faceted tasks
        'multiple modules', 'separate components', 'independent pieces',
        'parallel work', 'divide and conquer'
    ]

    # Keywords suggesting subagents are better
    subagent_indicators = [
        'search for', 'find files', 'look for', 'grep',
        'explore codebase', 'understand how', 'quick research',
        'sequential', 'step by step', 'one at a time',
        'simple', 'straightforward', 'focused'
    ]

    prompt_lower = prompt.lower()

    team_score = sum(1 for indicator in team_indicators if indicator in prompt_lower)
    subagent_score = sum(1 for indicator in subagent_indicators if indicator in prompt_lower)

    return {
        'team_score': team_score,
        'subagent_score': subagent_score,
        'suggests_teams': team_score > 0 and team_score > subagent_score
    }

def generate_context(prompt):
    """Generate contextual guidance about agent teams."""

    analysis = analyze_task_for_teams(prompt)

    if analysis['suggests_teams']:
        return """<agent-teams-context>
Agent Teams Feature Available:

Your task might benefit from AGENT TEAMS (not subagents). Key differences:

**Agent Teams** (for parallel coordination):
- Multiple independent Claude instances
- Teammates communicate directly with each other
- Shared task list for coordination
- Best for: research/review, competing hypotheses, cross-layer work
- Higher token cost, but parallelizes exploration

**Subagents** (for focused work):
- Report results back to main agent only
- No inter-agent communication
- Best for: focused searches, sequential tasks, simple delegation
- Lower token cost

To create an agent team:
```
Create an agent team with 3 teammates to [task]. Have them:
- Teammate 1: [specific role]
- Teammate 2: [specific role]
- Teammate 3: [specific role]
Ask them to coordinate and share findings with each other.
```

Example team structures:
- **Research team**: Security reviewer + Performance analyzer + Test coverage checker
- **Hypothesis team**: 3-5 agents testing competing theories, debating findings
- **Architecture team**: Frontend specialist + Backend specialist + Database expert

Teams work best when teammates can operate independently but benefit from coordination.
</agent-teams-context>"""

    # Even if not suggested, provide minimal awareness
    return """<agent-teams-awareness>
Agent Teams: Available for parallel multi-agent coordination (distinct from Task subagents).
Use when teammates need to communicate with each other, not just report back.
</agent-teams-awareness>"""

def main():
    """Main hook execution."""
    try:
        # Read stdin for hook context
        hook_input = sys.stdin.read()

        # Parse hook input
        try:
            data = json.loads(hook_input)
            prompt = data.get('userMessage', '') or data.get('prompt', '')
        except:
            # If not JSON, treat entire input as prompt
            prompt = hook_input

        # Generate context
        context = generate_context(prompt)

        # Output context
        print(context)
        return 0

    except Exception as e:
        # Silent failure - don't interrupt user workflow
        print(f"<!-- agent-teams-context error: {e} -->", file=sys.stderr)
        return 0

if __name__ == '__main__':
    sys.exit(main())
