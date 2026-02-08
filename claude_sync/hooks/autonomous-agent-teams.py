#!/usr/bin/env python3
"""
Autonomous Agent Teams System - Proactive team spawning and coordination

This hook analyzes tasks and AUTOMATICALLY suggests/spawns agent teams when:
1. Task complexity warrants parallel exploration
2. Multiple independent subtasks detected
3. Cross-domain work requiring specialization
4. Competing hypotheses need parallel testing

Philosophy: Like autonomous_monitor.py for services, but for agent teams.
"""

import sys
import json
import re
from datetime import datetime

def calculate_task_complexity(prompt):
    """Calculate task complexity score to determine if team is warranted."""

    complexity_indicators = {
        # High complexity (3 points each)
        'very_high': [
            'refactor entire', 'rebuild', 'redesign', 'architect',
            'comprehensive review', 'full analysis', 'investigate all',
            'multiple systems', 'end-to-end', 'full stack'
        ],

        # Medium-high (2 points each)
        'high': [
            'multiple perspectives', 'different angles', 'various approaches',
            'competing hypotheses', 'parallel', 'coordinate',
            'frontend and backend', 'cross-cutting', 'spanning',
            'independent modules', 'separate components'
        ],

        # Medium (1 point each)
        'medium': [
            'review', 'analyze', 'investigate', 'research',
            'explore', 'examine', 'assess', 'evaluate',
            'multiple', 'several', 'various', 'different'
        ]
    }

    prompt_lower = prompt.lower()
    score = 0

    for weight, indicators in [('very_high', 3), ('high', 2), ('medium', 1)]:
        indicators_list = complexity_indicators.get(weight, [])
        for indicator in indicators_list:
            if indicator in prompt_lower:
                score += weight if weight in [2, 3] else 1

    # Bonus for explicit team language
    if 'team' in prompt_lower or 'teammates' in prompt_lower:
        score += 5

    # Bonus for numbered lists suggesting parallel work
    list_patterns = re.findall(r'[1-9]\.\s+', prompt) or re.findall(r'\-\s+\w+:', prompt)
    if len(list_patterns) >= 3:
        score += 2

    return score

def detect_team_structure(prompt):
    """Detect if user has already specified a team structure."""

    # Look for explicit team member definitions
    member_patterns = [
        r'teammate\s+\d+:', r'agent\s+\d+:', r'member\s+\d+:',
        r'\d+\.\s+\w+\s+(reviewer|specialist|analyst|developer|architect|engineer)',
        r'\-\s+\w+\s*:\s*\w+'
    ]

    for pattern in member_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            return True

    return False

def suggest_team_composition(prompt):
    """Suggest optimal team composition based on task analysis."""

    prompt_lower = prompt.lower()
    suggestions = []

    # Code review scenario
    if any(word in prompt_lower for word in ['review', 'pr', 'pull request', 'code quality']):
        suggestions.append({
            'type': 'code_review',
            'size': 3,
            'roles': [
                'Security reviewer: Check authentication, input validation, vulnerabilities',
                'Performance analyst: Query optimization, caching, bottlenecks',
                'Test coverage specialist: Unit tests, integration tests, edge cases'
            ]
        })

    # Bug investigation scenario
    elif any(word in prompt_lower for word in ['bug', 'crash', 'error', 'broken', 'not working']):
        suggestions.append({
            'type': 'bug_investigation',
            'size': 4,
            'roles': [
                'Root cause investigator: Trace error origins, stack analysis',
                'State debugger: Check variable states, data flow',
                'Integration tester: Test component interactions',
                'Hypothesis challenger: Test competing theories, debate findings'
            ]
        })

    # Architecture/design scenario
    elif any(word in prompt_lower for word in ['architecture', 'design', 'architect', 'structure']):
        suggestions.append({
            'type': 'architecture',
            'size': 3,
            'roles': [
                'System architect: High-level design, patterns, trade-offs',
                'Technical specialist: Implementation details, technology choices',
                'Security reviewer: Security implications, threat modeling'
            ]
        })

    # Feature implementation scenario
    elif any(word in prompt_lower for word in ['implement', 'build', 'create', 'add feature']):
        if 'frontend' in prompt_lower or 'backend' in prompt_lower or 'full stack' in prompt_lower:
            suggestions.append({
                'type': 'full_stack_feature',
                'size': 4,
                'roles': [
                    'Frontend developer: UI components, state management, UX',
                    'Backend developer: API endpoints, business logic, validation',
                    'Database architect: Schema design, migrations, optimization',
                    'QA engineer: Test coverage, E2E tests, validation'
                ]
            })

    # Research scenario
    elif any(word in prompt_lower for word in ['research', 'explore', 'investigate', 'analyze']):
        suggestions.append({
            'type': 'research',
            'size': 3,
            'roles': [
                'Researcher 1: Primary investigation, main approach',
                'Researcher 2: Alternative approaches, competing methods',
                'Synthesizer: Combine findings, identify patterns, report'
            ]
        })

    # Default parallel work scenario
    if not suggestions:
        suggestions.append({
            'type': 'general_parallel',
            'size': 3,
            'roles': [
                'Specialist 1: Focus on primary aspect',
                'Specialist 2: Focus on secondary aspect',
                'Coordinator: Synthesize findings, identify gaps'
            ]
        })

    return suggestions[0]

def generate_autonomous_context(prompt):
    """Generate proactive agent team suggestion with auto-spawn option."""

    complexity = calculate_task_complexity(prompt)
    has_explicit_structure = detect_team_structure(prompt)

    # Thresholds for autonomous action
    AUTO_SPAWN_THRESHOLD = 8  # Very clear parallel work
    SUGGEST_THRESHOLD = 5     # Likely benefits from team
    MENTION_THRESHOLD = 3     # Worth mentioning

    if complexity < MENTION_THRESHOLD:
        return None  # Task too simple for teams

    suggestion = suggest_team_composition(prompt)

    # Build context based on complexity
    if complexity >= AUTO_SPAWN_THRESHOLD or has_explicit_structure:
        # High confidence - auto-spawn mode
        return f"""<autonomous-agent-teams mode="auto-spawn">
AUTONOMOUS AGENT TEAM DETECTION

Confidence: HIGH (score: {complexity}/10)
Action: Ready to auto-spawn team

**Detected task type**: {suggestion['type'].replace('_', ' ').title()}
**Optimal team size**: {suggestion['size']} teammates

**Suggested composition**:
{chr(10).join(f"- {role}" for role in suggestion['roles'])}

**Auto-spawn command**:
```
Create an agent team with {suggestion['size']} teammates:
{chr(10).join(f"- {role}" for role in suggestion['roles'])}
Have them coordinate autonomously and share findings.
```

**Why autonomous?**
- Task complexity warrants parallel exploration
- Independent workstreams can proceed simultaneously
- Team coordination adds value over sequential work
- Higher token cost justified by time savings

**Autonomous features**:
✓ Teams self-coordinate via shared task list
✓ Teammates communicate directly (no bottleneck)
✓ Auto-cleanup when all tasks completed
✓ Idle notifications for monitoring

To proceed: Just confirm "yes" or directly start working with the team.
To customize: Specify different roles/structure.
To skip: Use single session or Task subagents instead.
</autonomous-agent-teams>"""

    elif complexity >= SUGGEST_THRESHOLD:
        # Medium confidence - suggest with reasoning
        return f"""<autonomous-agent-teams mode="suggest">
AGENT TEAM RECOMMENDED

Confidence: MEDIUM (score: {complexity}/10)
Action: Consider using agent team

**Task type**: {suggestion['type'].replace('_', ' ').title()}
**Suggested size**: {suggestion['size']} teammates

**Suggested roles**:
{chr(10).join(f"- {role}" for role in suggestion['roles'])}

**Benefits of team approach**:
- Parallel exploration of independent aspects
- Multiple perspectives reduce blind spots
- Faster completion via concurrent work
- Team coordination enables challenge/debate

**Alternative**: Use Task subagents if work is sequential or has many dependencies.

**To create team**:
```
Create an agent team with {suggestion['size']} teammates:
[specify roles based on your needs]
```
</autonomous-agent-teams>"""

    else:
        # Low confidence - minimal mention
        return f"""<autonomous-agent-teams mode="mention">
Agent team option available (complexity: {complexity}/10). Consider if task benefits from parallel coordination.
</autonomous-agent-teams>"""

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
            prompt = hook_input

        # Generate autonomous context
        context = generate_autonomous_context(prompt)

        if context:
            print(context)

            # Log decision for monitoring (like autonomous_monitor.py logs)
            try:
                import os
                log_dir = os.path.expanduser('~/.claude/logs')
                os.makedirs(log_dir, exist_ok=True)

                with open(f'{log_dir}/autonomous_teams.log', 'a') as f:
                    timestamp = datetime.now().isoformat()
                    complexity = calculate_task_complexity(prompt)
                    f.write(f"[{timestamp}] Complexity: {complexity}/10 | Prompt: {prompt[:100]}...\n")
            except:
                pass  # Silent failure on logging

        return 0

    except Exception as e:
        # Silent failure - don't interrupt user workflow
        print(f"<!-- autonomous-agent-teams error: {e} -->", file=sys.stderr)
        return 0

if __name__ == '__main__':
    sys.exit(main())
