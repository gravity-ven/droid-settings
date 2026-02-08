#!/usr/bin/env python3
"""
Memorize Directory Tree in Supermemory
Scans project directory and stores structure in central memory
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime

class DirectoryMemorizer:
    def __init__(self, root_path: str = None):
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.supermemory_url = "http://localhost:3456"

        # Directories to ignore
        self.ignore_dirs = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv',
            'logs', '.claude', '.DS_Store', 'dist', 'build'
        }

        # File extensions to track
        self.track_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.json', '.md',
            '.sh', '.bash', '.yml', '.yaml', '.toml', '.sql',
            '.html', '.css', '.plist'
        }

    def scan_directory(self, path: Path, max_depth: int = 5, current_depth: int = 0) -> dict:
        """Recursively scan directory structure"""
        if current_depth > max_depth:
            return None

        structure = {
            'name': path.name,
            'type': 'directory',
            'path': str(path.relative_to(self.root_path)),
            'children': []
        }

        try:
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))

            for item in items:
                if item.name in self.ignore_dirs or item.name.startswith('.'):
                    continue

                if item.is_dir():
                    child = self.scan_directory(item, max_depth, current_depth + 1)
                    if child:
                        structure['children'].append(child)

                elif item.is_file():
                    if item.suffix in self.track_extensions:
                        structure['children'].append({
                            'name': item.name,
                            'type': 'file',
                            'path': str(item.relative_to(self.root_path)),
                            'extension': item.suffix,
                            'size': item.stat().st_size
                        })
        except PermissionError:
            pass

        return structure

    def save_to_supermemory(self, tree: dict) -> bool:
        """Save directory tree to supermemory"""
        try:
            # Create memory content
            content = f"""
Directory Tree for {self.root_path.name}
Last Scanned: {datetime.now().isoformat()}

Structure:
{json.dumps(tree, indent=2)}

Total Files: {self.count_files(tree)}
Total Directories: {self.count_dirs(tree)}
"""

            # Save to supermemory via API
            response = requests.post(
                f"{self.supermemory_url}/api/memory/save",
                json={
                    "content": content,
                    "tags": ["directory-tree", self.root_path.name, "project-structure"]
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code in [200, 201]:
                print(f"✅ Directory tree saved to supermemory")
                print(f"   Project: {self.root_path.name}")
                print(f"   Files: {self.count_files(tree)}")
                print(f"   Directories: {self.count_dirs(tree)}")
                return True
            else:
                print(f"❌ Failed to save: HTTP {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error saving to supermemory: {e}")
            return False

    def count_files(self, tree: dict) -> int:
        """Count total files in tree"""
        count = 0
        if tree.get('type') == 'file':
            return 1
        for child in tree.get('children', []):
            count += self.count_files(child)
        return count

    def count_dirs(self, tree: dict) -> int:
        """Count total directories in tree"""
        count = 0
        if tree.get('type') == 'directory':
            count = 1
        for child in tree.get('children', []):
            if child.get('type') == 'directory':
                count += self.count_dirs(child)
        return count

    def run(self):
        """Main execution"""
        print(f"📂 Scanning directory: {self.root_path}")
        print()

        tree = self.scan_directory(self.root_path)

        if tree:
            self.save_to_supermemory(tree)
        else:
            print("❌ Failed to scan directory")

if __name__ == '__main__':
    import sys

    # Use provided path or current directory
    path = sys.argv[1] if len(sys.argv) > 1 else None

    memorizer = DirectoryMemorizer(path)
    memorizer.run()
