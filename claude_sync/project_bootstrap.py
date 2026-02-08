#!/usr/bin/env python3
"""Project Bootstrap for Claude Code Self-Teaching

Creates minimal per-project infrastructure *idempotently*:
  docs/learnings.md
  docs/failures.md
  tools/templates/
  meta/instruction-history.md

Usage:
  python ~/.claude/project_bootstrap.py /path/to/project
  python ~/.claude/project_bootstrap.py .

Notes:
- Does not overwrite existing files.
- Does not modify project CLAUDE.md (global ~/.claude/CLAUDE.md is used).
"""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def write_if_missing(p: Path, content: str) -> None:
    if p.exists():
        return
    ensure_dir(p.parent)
    p.write_text(content, encoding="utf-8")


LEARNINGS = """# Learnings (project)

- 
"""

FAILURES = """# Failures (project)

## Template
- What happened:
- Root cause:
- Fix:
- Prevention / guardrail:

"""

INSTR_HISTORY = """# Instruction History (project)

- 
"""


def bootstrap(project: Path, *, create: bool = False) -> None:
    project = project.expanduser().resolve()

    # Safety: don't accidentally try to create placeholder or system paths.
    # Block attempts to bootstrap system directories
    blocked_paths = {Path('/'), Path('/Users'), Path('/usr'), Path('/System'), Path('/Library')}
    if project in blocked_paths:
        # Fall back safely instead of hard-failing when invoked from system dirs.
        safe_project = Path.home()
        print(
            f"WARNING: Refusing to bootstrap system directory: {project}. "
            f"Using home directory instead: {safe_project}.",
            file=sys.stderr,
        )
        project = safe_project

    if not project.exists():
        if not create:
            raise SystemExit(
                f"Project path does not exist: {project}\n"
                "Pass an existing folder, or rerun with --create to create it."
            )
        ensure_dir(project)

    if not project.is_dir():
        raise SystemExit(f"Project path is not a directory: {project}")

    write_if_missing(project / "docs" / "learnings.md", LEARNINGS)
    write_if_missing(project / "docs" / "failures.md", FAILURES)
    ensure_dir(project / "tools" / "templates")
    write_if_missing(project / "meta" / "instruction-history.md", INSTR_HISTORY)

    print(f"Bootstrapped: {project}")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: project_bootstrap.py [--create] /path/to/project")
        return 2

    create = False
    args = argv[1:]
    if args and args[0] == "--create":
        create = True
        args = args[1:]

    if not args:
        print("Usage: project_bootstrap.py [--create] /path/to/project")
        return 2

    # Validate that we have a non-empty path argument
    if not args[0] or args[0].strip() == "":
        print("ERROR: Empty path provided. Cannot bootstrap empty path.")
        print("Usage: project_bootstrap.py [--create] /path/to/project")
        return 2

    bootstrap(Path(args[0]), create=create)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
