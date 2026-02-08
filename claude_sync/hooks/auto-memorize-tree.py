#!/usr/bin/env python3
"""
Auto-Memorize Directory Tree Hook
Automatically scans and stores directory tree in supermemory on session start
"""

import subprocess
import sys
from pathlib import Path

def main():
    # Get current working directory from hook context
    cwd = Path.cwd()

    # Only memorize if we're in a project directory (not home, not system dirs)
    if cwd == Path.home() or str(cwd).startswith('/System') or str(cwd).startswith('/usr'):
        sys.exit(0)  # Skip

    # Run the memorizer script
    memorizer_script = Path.home() / '.claude' / 'memorize_with_mcp.py'

    if memorizer_script.exists():
        try:
            subprocess.run(
                ['python3', str(memorizer_script)],
                timeout=30,
                capture_output=True,
                cwd=cwd
            )
        except:
            pass  # Silent fail - don't block session start

    sys.exit(0)

if __name__ == '__main__':
    main()
