#!/usr/bin/env python3
"""
Memorize Directory Tree using MCP Memory
Stores directory structure in the existing MCP memory system
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

def scan_directory(path: Path, max_depth: int = 5, current_depth: int = 0):
    """Recursively scan directory structure"""
    ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv',
                   'logs', '.DS_Store', 'dist', 'build', '.claude'}
    track_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.md',
                        '.sh', '.bash', '.yml', '.yaml', '.toml', '.sql',
                        '.html', '.css', '.plist'}

    if current_depth > max_depth:
        return None

    structure = {
        'name': path.name,
        'type': 'directory',
        'path': str(path.relative_to(path.parent.parent)),
        'children': []
    }

    try:
        items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))

        for item in items:
            if item.name in ignore_dirs or item.name.startswith('.'):
                continue

            if item.is_dir():
                child = scan_directory(item, max_depth, current_depth + 1)
                if child:
                    structure['children'].append(child)
            elif item.is_file() and item.suffix in track_extensions:
                structure['children'].append({
                    'name': item.name,
                    'type': 'file',
                    'extension': item.suffix,
                    'size': item.stat().st_size
                })
    except PermissionError:
        pass

    return structure

def main():
    cwd = Path.cwd()

    # Skip system directories
    if cwd == Path.home() or str(cwd).startswith('/System') or str(cwd).startswith('/usr'):
        return

    print(f"📂 Scanning {cwd.name}...")
    tree = scan_directory(cwd)

    if tree:
        # Save to project-specific memory file
        memory_dir = Path.home() / '.claude' / 'projects' / '-' / 'memory'
        memory_dir.mkdir(parents=True, exist_ok=True)

        tree_file = memory_dir / 'directory_tree.json'
        with open(tree_file, 'w') as f:
            json.dump({
                'project': cwd.name,
                'path': str(cwd),
                'scanned_at': datetime.now().isoformat(),
                'structure': tree
            }, f, indent=2)

        print(f"✅ Directory tree saved to {tree_file}")

if __name__ == '__main__':
    main()
