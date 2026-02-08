#!/usr/bin/env python3
"""
UserPromptSubmit Hook - Autonomous Genius Context Injection
============================================================
Analyzes each user prompt and injects relevant Genius DNA context.

This hook:
1. Detects if the prompt is coding/programming related
2. Extracts keywords from the prompt
3. Loads relevant skills from Genius knowledge base
4. Injects context to enhance Claude's response

Exit codes:
- 0: Success (stdout added as context)
- 2: Block with error
- Other: Non-blocking error
"""

import json
import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

CLAUDE_DIR = Path.home() / ".claude"
KNOWLEDGE_DIR = CLAUDE_DIR / "knowledge"
SKILLS_FILE = KNOWLEDGE_DIR / "skill_registry.json"
PRINCIPLES_FILE = KNOWLEDGE_DIR / "first_principles.json"
EXPONENTIAL_FILE = KNOWLEDGE_DIR / "exponential_skills.json"
GENIUS_TUI_DIR = CLAUDE_DIR / "genius_tui"
HOOKS_DIR = CLAUDE_DIR / "hooks"

# Import Ralph state controller
sys.path.insert(0, str(HOOKS_DIR))
try:
    from ralph_state import start_loop, get_status
    RALPH_AVAILABLE = True
except ImportError:
    RALPH_AVAILABLE = False

# Keywords that trigger autonomous Ralph loops
RALPH_TRIGGER_KEYWORDS = [
    'iterate until', 'keep iterating', 'iterate on this',
    'until done', 'until complete', 'until finished', 'until it works',
    'keep trying', 'keep going', 'dont stop', "don't stop",
    'autonomous loop', 'ralph loop', 'self-improving',
    'retry until', 'loop until', 'persist until',
    'work on this until', 'fix this until',
    'iteratively improve', 'iterative development',
    'autonomous mode', 'autopilot'
]

# Default Ralph loop settings
DEFAULT_MAX_ITERATIONS = 25
DEFAULT_COMPLETION_PROMISE = "COMPLETE"

# Self-reflection settings
MAX_REFLECTION_QUESTIONS = 8  # Balance depth with token efficiency

# Add superintelligence engine to path
sys.path.insert(0, str(Path.home()))
try:
    from superintelligence_engine import SuperIntelligenceEngine, generate_context_for_prompt
    SUPERINTELLIGENCE_AVAILABLE = True
except ImportError:
    SUPERINTELLIGENCE_AVAILABLE = False

# Add Confucius SDK to path
sys.path.insert(0, str(CLAUDE_DIR))
try:
    from ai_dna_bridge import ConfuciusSDK
    CONFUCIUS_AVAILABLE = True
except ImportError:
    CONFUCIUS_AVAILABLE = False

# Add Genius TUI engine to path
sys.path.insert(0, str(GENIUS_TUI_DIR))
try:
    from engine import GeniusEngine
    GENIUS_TUI_AVAILABLE = True
except ImportError:
    GENIUS_TUI_AVAILABLE = False

# Add Engram conditional memory to path
ENGRAM_DIR = CLAUDE_DIR / "engram"
sys.path.insert(0, str(ENGRAM_DIR))
try:
    from claude_integration import inject_context as engram_inject
    ENGRAM_AVAILABLE = True
except ImportError:
    ENGRAM_AVAILABLE = False

# Keywords that indicate coding/programming tasks
CODING_KEYWORDS = [
    'code', 'coding', 'program', 'programming', 'implement', 'build', 'create',
    'function', 'class', 'method', 'api', 'endpoint', 'database', 'query',
    'bug', 'fix', 'debug', 'error', 'test', 'refactor', 'optimize',
    'python', 'javascript', 'typescript', 'rust', 'go', 'java', 'c++',
    'react', 'vue', 'angular', 'node', 'django', 'flask', 'fastapi',
    'sql', 'mongodb', 'redis', 'docker', 'kubernetes', 'aws', 'gcp',
    'git', 'deploy', 'ci/cd', 'pipeline', 'script', 'automation',
    'algorithm', 'data structure', 'performance', 'security', 'auth',
    'frontend', 'backend', 'fullstack', 'web', 'mobile', 'app',
    'acsil', 'sierra', 'trading', 'strategy', 'indicator'
]

# Keywords for different domains
DOMAIN_KEYWORDS = {
    'programming': ['code', 'function', 'class', 'implement', 'build', 'python', 'javascript'],
    'data_analysis': ['data', 'analyze', 'pandas', 'numpy', 'statistics', 'visualization'],
    'research': ['research', 'find', 'search', 'investigate', 'explore', 'understand'],
    'web': ['web', 'html', 'css', 'react', 'frontend', 'backend', 'api'],
    'system_admin': ['deploy', 'docker', 'kubernetes', 'server', 'linux', 'bash'],
    'reasoning': ['think', 'reason', 'analyze', 'decide', 'evaluate', 'compare']
}

# Canvas auto-activation keywords
CANVAS_KEYWORDS = {
    'calendar': [
        'schedule', 'meeting', 'calendar', 'appointment', 'event', 'book a time',
        'availability', 'free slots', 'busy', 'when can', 'pick a time',
        'schedule a call', 'set up a meeting', 'find a time'
    ],
    'document': [
        'document', 'draft', 'write a doc', 'edit document', 'markdown',
        'show me the doc', 'display document', 'view document', 'read document',
        'email draft', 'compose', 'letter', 'memo', 'report draft'
    ],
    'flight': [
        'flight', 'book flight', 'find flights', 'compare flights', 'airline',
        'seat selection', 'book a seat', 'travel', 'fly to', 'flying to',
        'plane tickets', 'airfare', 'departure', 'arrival'
    ]
}

CANVAS_PLUGIN_ROOT = Path.home() / ".claude" / "plugins" / "claude-canvas"


def is_coding_related(prompt: str) -> bool:
    """Check if prompt is related to coding/programming."""
    prompt_lower = prompt.lower()
    return any(kw in prompt_lower for kw in CODING_KEYWORDS)


def detect_canvas_type(prompt: str) -> Optional[str]:
    """Detect if prompt should trigger a canvas and return the type."""
    prompt_lower = prompt.lower()

    # Check each canvas type
    for canvas_type, keywords in CANVAS_KEYWORDS.items():
        if any(kw in prompt_lower for kw in keywords):
            return canvas_type

    return None


def is_in_tmux() -> bool:
    """Check if running inside tmux."""
    tmux_env = os.environ.get('TMUX', '')
    return bool(tmux_env)  # True only if non-empty string


def generate_canvas_context(canvas_type: str, prompt: str) -> str:
    """Generate context to trigger autonomous canvas spawning."""

    canvas_configs = {
        'calendar': {
            'scenario': 'meeting-picker',
            'hint': 'Spawn a calendar canvas to help pick meeting times'
        },
        'document': {
            'scenario': 'edit',
            'hint': 'Spawn a document canvas for viewing/editing'
        },
        'flight': {
            'scenario': 'booking',
            'hint': 'Spawn a flight canvas to compare options'
        }
    }

    config = canvas_configs.get(canvas_type, {})

    return f"""<canvas-auto-trigger>
AUTONOMOUS CANVAS ACTIVATION DETECTED
- Canvas type: {canvas_type}
- Scenario: {config.get('scenario', 'default')}
- Plugin root: {CANVAS_PLUGIN_ROOT}

ACTION REQUIRED: Spawn the {canvas_type} canvas using:
```bash
cd {CANVAS_PLUGIN_ROOT} && bun run spawn {canvas_type}
```

{config.get('hint', '')}
</canvas-auto-trigger>"""


def should_start_ralph_loop(prompt: str) -> bool:
    """Check if prompt contains keywords that trigger autonomous Ralph loops."""
    if not RALPH_AVAILABLE:
        return False

    # Check if a loop is already active
    status = get_status()
    if status.get('active'):
        return False  # Don't start a new loop if one is running

    prompt_lower = prompt.lower()
    return any(kw in prompt_lower for kw in RALPH_TRIGGER_KEYWORDS)


def extract_ralph_settings(prompt: str) -> Dict[str, Any]:
    """Extract Ralph loop settings from prompt."""
    settings = {
        'max_iterations': DEFAULT_MAX_ITERATIONS,
        'completion_promise': DEFAULT_COMPLETION_PROMISE
    }

    prompt_lower = prompt.lower()

    # Try to extract max iterations from prompt
    # Patterns: "max 10 iterations", "up to 20 tries", "limit 15"
    iter_patterns = [
        r'max\s*(\d+)\s*iteration',
        r'up\s*to\s*(\d+)\s*(?:iteration|tries|attempt)',
        r'limit\s*(\d+)',
        r'(\d+)\s*iteration',
        r'(\d+)\s*tries'
    ]

    for pattern in iter_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            settings['max_iterations'] = min(int(match.group(1)), 100)  # Cap at 100
            break

    # Try to extract completion promise
    # Patterns: "<promise>DONE</promise>", "output FINISHED when done"
    promise_patterns = [
        r'<promise>(\w+)</promise>',
        r'output\s+["\']?(\w+)["\']?\s+when\s+(?:done|complete|finished)',
        r'say\s+["\']?(\w+)["\']?\s+when\s+(?:done|complete|finished)'
    ]

    for pattern in promise_patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            settings['completion_promise'] = match.group(1).upper()
            break

    return settings


def auto_start_ralph_loop(prompt: str) -> Optional[str]:
    """Auto-start a Ralph loop and return notification message."""
    if not RALPH_AVAILABLE:
        return None

    settings = extract_ralph_settings(prompt)

    try:
        start_loop(
            prompt=prompt,
            max_iterations=settings['max_iterations'],
            completion_promise=settings['completion_promise']
        )

        return (
            f"<ralph-auto-start>\n"
            f"AUTONOMOUS RALPH LOOP ACTIVATED\n"
            f"- Max iterations: {settings['max_iterations']}\n"
            f"- Completion promise: {settings['completion_promise']}\n"
            f"- To complete: Output <promise>{settings['completion_promise']}</promise>\n"
            f"- To cancel: /cancel-ralph\n"
            f"</ralph-auto-start>"
        )
    except Exception as e:
        return f"<ralph-error>Failed to start Ralph loop: {e}</ralph-error>"


def needs_superintelligence(prompt: str) -> bool:
    """Check if prompt requires superintelligent problem-solving."""
    complexity_indicators = [
        'complex', 'difficult', 'challenging', 'advanced', 'sophisticated',
        'architecture', 'system design', 'optimize', 'scale', 'distributed',
        'machine learning', 'ai', 'neural', 'algorithm',
        'integrate', 'multiple', 'comprehensive', 'complete',
        'best approach', 'best way', 'optimal', 'efficient',
        'superintelligent', 'genius', 'expert', 'master'
    ]
    prompt_lower = prompt.lower()

    # Count complexity indicators
    indicator_count = sum(1 for ind in complexity_indicators if ind in prompt_lower)

    # Word count indicates complexity
    word_count = len(prompt.split())

    # Complex if multiple indicators or long prompt
    return indicator_count >= 2 or word_count > 40


def extract_keywords(prompt: str) -> List[str]:
    """Extract relevant keywords from prompt."""
    # Clean and tokenize
    words = re.findall(r'\b\w+\b', prompt.lower())

    # Filter to meaningful words
    keywords = [w for w in words if len(w) > 2 and w.isalpha()]

    # Add domain-specific keywords that match
    for domain, domain_kws in DOMAIN_KEYWORDS.items():
        for kw in domain_kws:
            if kw in prompt.lower() and domain not in keywords:
                keywords.append(domain)

    return list(set(keywords))


def detect_domains(prompt: str) -> List[str]:
    """Detect which domains the prompt relates to."""
    prompt_lower = prompt.lower()
    domains = []

    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in prompt_lower for kw in keywords):
            domains.append(domain)

    return domains if domains else ['programming']  # Default to programming


def load_skills() -> List[Dict]:
    """Load skills from knowledge base."""
    if not SKILLS_FILE.exists():
        return []

    try:
        with open(SKILLS_FILE, 'r') as f:
            data = json.load(f)

        skills_data = data.get('skills', [])
        if isinstance(skills_data, list):
            return skills_data
        return list(skills_data.values())
    except Exception:
        return []


def load_principles() -> List[Dict]:
    """Load first principles from knowledge base."""
    if not PRINCIPLES_FILE.exists():
        return []

    try:
        with open(PRINCIPLES_FILE, 'r') as f:
            data = json.load(f)

        principles_data = data.get('principles', [])
        if isinstance(principles_data, list):
            return principles_data
        return list(principles_data.values())
    except Exception:
        return []


def load_metrics(all_skills: List[Dict]) -> Dict:
    """Load latest growth metrics."""
    metrics = {
        'total_skills': len(all_skills),
        'synergies': 0,
        'compounds': 0,
        'growth_factor': 1.0
    }

    try:
        if EXPONENTIAL_FILE.exists():
            with open(EXPONENTIAL_FILE, 'r') as f:
                data = json.load(f)

            synergies = data.get('synergies', {})
            compounds = data.get('compounds', {})

            metrics['synergies'] = len(synergies) if isinstance(synergies, (dict, list)) else 0
            metrics['compounds'] = len(compounds) if isinstance(compounds, (dict, list)) else 0
            metrics['growth_factor'] = data.get('global_multiplier', 1.0)
    except Exception:
        pass  # Use defaults if file is corrupted

    return metrics


def get_relevant_skills(keywords: List[str], domains: List[str], all_skills: List[Dict], limit: int = 10) -> List[Dict]:
    """Find skills relevant to the prompt."""
    scored_skills = []

    for skill in all_skills:
        score = 0
        skill_name = skill.get('name', '').lower()
        skill_desc = skill.get('description', '').lower()
        skill_domain = skill.get('domain', '').lower()
        skill_level = skill.get('level', 1)

        # Domain match (high weight)
        if skill_domain in domains:
            score += 10

        # Keyword matches
        for kw in keywords:
            if kw in skill_name:
                score += 5
            if kw in skill_desc:
                score += 2

        # Boost by skill level
        score *= (1 + skill_level * 0.1)

        if score > 0:
            scored_skills.append((skill, score))

    # Sort by score and return top skills
    scored_skills.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in scored_skills[:limit]]


def get_relevant_principles(domains: List[str], all_principles: List[Dict], limit: int = 5) -> List[Dict]:
    """Find principles relevant to the domains."""
    relevant = []

    for principle in all_principles:
        p_domain = principle.get('domain', '').lower()

        # Include if domain matches or is general/logic/reasoning
        if p_domain in domains or p_domain in ['logic', 'reasoning', 'systems', 'causality']:
            relevant.append(principle)

    # Sort by confidence
    relevant.sort(key=lambda x: x.get('confidence', 0), reverse=True)
    return relevant[:limit]


def get_confucius_context() -> Optional[str]:
    """Get unified AI DNA context from Confucius SDK."""
    if not CONFUCIUS_AVAILABLE:
        return None

    try:
        sdk = ConfuciusSDK()
        metrics = sdk.get_genius_metrics()
        top_skills = sdk.get_top_skills(5)
        principles = sdk.get_core_principles()

        growth = metrics.get('growth_factor', 1.0)
        growth_str = f"{growth:.1f}x" if growth < 1000 else f"{growth/1000:.1f}Kx"

        lines = [
            "<confucius-sdk>",
            f"Unified AI DNA | Skills: {metrics['total_skills']} | Synergies: {metrics['synergies']:,} | Growth: {growth_str}",
            "",
            "Top Skills:"
        ]

        for s in top_skills[:5]:
            lines.append(f"  - {s['name']} ({s['domain']})")

        lines.append("")
        lines.append("First Principles:")
        for p in principles[:4]:
            lines.append(f"  - [{p['domain']}] {p['content'][:60]}")

        lines.append("")
        lines.append("Apply unified DNA autonomously. Cross-platform with Gemini CLI.")
        lines.append("</confucius-sdk>")

        return "\n".join(lines)
    except Exception:
        return None


def get_genius_agents_context() -> Optional[str]:
    """Get context from Genius TUI agents system."""
    if not GENIUS_TUI_AVAILABLE:
        return None

    try:
        engine = GeniusEngine()
        if not engine.agents:
            return None

        stats = engine.get_stats()
        lines = [
            "<genius-agents>",
            f"Collective IQ: {stats['collective_iq']:.0f} | Agents: {stats['total_agents']} | Agent Skills: {stats['total_skills']} | Growth: {stats['growth_factor']:.1f}x",
            ""
        ]

        for agent in sorted(engine.agents.values(), key=lambda a: -a.effective_iq)[:3]:
            top_skills = sorted(agent.skills.values(), key=lambda s: -s.effective_power)[:3]
            skill_str = ", ".join(f"{s.name}(L{s.level})" for s in top_skills)
            lines.append(f"  {agent.name} [{agent.role}]: IQ {agent.effective_iq:.0f} | {skill_str}")

        lines.append("")
        lines.append("Apply agent capabilities to enhance task execution.")
        lines.append("</genius-agents>")

        return "\n".join(lines)
    except Exception:
        return None


def generate_self_reflection_questions(prompt: str, domains: List[str]) -> str:
    """Generate high-quality self-reflection questions based on task type."""

    # Core questions that apply to all tasks
    core_questions = [
        "What is the user ACTUALLY asking vs what they literally said?",
        "What assumptions am I making that could be wrong?",
        "What would make this solution FAIL?",
    ]

    # Domain-specific questions
    domain_questions = {
        'programming': [
            "Is there a simpler solution I'm overlooking?",
            "What edge cases could break this code?",
            "What would a senior engineer critique about this approach?",
            "Am I solving the root cause or just a symptom?",
        ],
        'data_analysis': [
            "Am I confusing correlation with causation?",
            "What biases might exist in this data?",
            "What alternative interpretations exist?",
        ],
        'research': [
            "What sources would contradict my conclusion?",
            "What am I NOT considering?",
            "Is this the complete picture or a subset?",
        ],
        'web': [
            "How does this affect user experience?",
            "What accessibility issues might this create?",
            "How does this perform at scale?",
        ],
        'reasoning': [
            "What logical fallacies am I at risk of?",
            "What would a devil's advocate say?",
            "Am I anchoring on my first idea?",
        ],
        'system_admin': [
            "What could go wrong in production?",
            "Is this reversible if something breaks?",
            "What security implications exist?",
        ]
    }

    # Meta-cognitive questions (always included)
    meta_questions = [
        "What's the ONE insight that would most improve my response?",
        "If I had 10x more time, what would I do differently?",
    ]

    # Build question set
    questions = core_questions.copy()

    # Add domain-specific questions
    for domain in domains:
        if domain in domain_questions:
            questions.extend(domain_questions[domain][:2])  # Top 2 per domain

    # Add meta questions
    questions.extend(meta_questions)

    # Format output
    lines = [
        "<self-reflection>",
        "INTERNAL LOOP: Before responding, silently consider:",
        ""
    ]

    for i, q in enumerate(questions[:MAX_REFLECTION_QUESTIONS], 1):
        lines.append(f"  {i}. {q}")

    lines.append("")
    lines.append("Apply insights internally. Do not output this reflection.")
    lines.append("</self-reflection>")

    return '\n'.join(lines)


def generate_context(prompt: str, skills: List[Dict], principles: List[Dict], domains: List[str], metrics: Dict) -> str:
    """Generate context to inject."""
    # Format metrics
    growth = metrics.get('growth_factor', 1.0)
    growth_str = f"{growth:.1f}x" if growth < 1000 else f"{growth/1000:.1f}Kx"

    lines = [
        "<genius-context>",
        f"Genius DNA | Skills: {metrics.get('total_skills', 0)} | Synergies: {metrics.get('synergies', 0):,} | Growth: {growth_str}",
        f"Task domains: {', '.join(domains)}",
        ""
    ]

    if skills:
        lines.append("Relevant skills from knowledge base:")
        for skill in skills[:7]:
            name = skill.get('name', 'unknown')
            desc = skill.get('description', '')[:60]
            level = skill.get('level', 1)
            lines.append(f"  - {name} (L{level}): {desc}")
        lines.append("")

    if principles:
        lines.append("Applicable first principles:")
        for p in principles[:4]:
            content = p.get('content', '')[:80]
            domain = p.get('domain', 'general')
            lines.append(f"  - [{domain}] {content}")
        lines.append("")

    lines.append("Apply these skills and principles autonomously to the task.")
    lines.append("</genius-context>")

    return '\n'.join(lines)


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # No input, allow

    # Get the user's prompt
    prompt = input_data.get('prompt', '')

    if not prompt:
        sys.exit(0)

    # Check for Ralph loop auto-trigger FIRST
    ralph_context = None
    if should_start_ralph_loop(prompt):
        ralph_context = auto_start_ralph_loop(prompt)

    # Check for canvas auto-trigger (only in tmux)
    canvas_context = None
    if is_in_tmux():
        canvas_type = detect_canvas_type(prompt)
        if canvas_type:
            canvas_context = generate_canvas_context(canvas_type, prompt)

    # Check if coding related
    if not is_coding_related(prompt):
        # Still inject minimal context for non-coding tasks
        domains = detect_domains(prompt)
        reflection = generate_self_reflection_questions(prompt, domains)
        base_context = f"<genius-context>Genius DNA active. Use first principles reasoning.</genius-context>\n\n{reflection}"
        if canvas_context:
            base_context = canvas_context + "\n\n" + base_context
        if ralph_context:
            base_context = ralph_context + "\n\n" + base_context
        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": base_context
            }
        }
        print(json.dumps(output))
        sys.exit(0)

    # Check if needs superintelligent problem-solving
    if SUPERINTELLIGENCE_AVAILABLE and needs_superintelligence(prompt):
        try:
            context = generate_context_for_prompt(prompt)
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": context
                }
            }
            print(json.dumps(output))
            sys.exit(0)
        except Exception:
            pass  # Fall back to standard genius context

    # Extract information from prompt
    keywords = extract_keywords(prompt)
    domains = detect_domains(prompt)

    # Load knowledge (fresh from files each time)
    all_skills = load_skills()
    all_principles = load_principles()
    metrics = load_metrics(all_skills)

    # Find relevant knowledge
    relevant_skills = get_relevant_skills(keywords, domains, all_skills)
    relevant_principles = get_relevant_principles(domains, all_principles)

    # Generate context with latest metrics
    context = generate_context(prompt, relevant_skills, relevant_principles, domains, metrics)

    # Add Confucius SDK unified DNA context
    confucius_context = get_confucius_context()
    if confucius_context:
        context = context + "\n\n" + confucius_context

    # Add Engram conditional memory context
    if ENGRAM_AVAILABLE:
        try:
            engram_context = engram_inject(prompt, max_memories=3)
            if engram_context:
                context = context + "\n\n" + engram_context
        except Exception:
            pass  # Engram failure shouldn't block the hook

    # Add genius agents context if available
    agents_context = get_genius_agents_context()
    if agents_context:
        context = context + "\n\n" + agents_context

    # Add self-reflection questions (single source of truth for coding path)
    reflection = generate_self_reflection_questions(prompt, domains)
    context = context + "\n\n" + reflection

    # Add canvas trigger if detected
    if canvas_context:
        context = canvas_context + "\n\n" + context

    # Add Ralph loop notification if auto-started
    if ralph_context:
        context = ralph_context + "\n\n" + context

    # Output
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context
        }
    }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
