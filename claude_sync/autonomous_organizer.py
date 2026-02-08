#!/usr/bin/env python3
"""
Autonomous Claude Code Organizer
Continuously maintains optimal organization of ~/.claude directory

Like autonomous_monitor.py but for code organization.
Runs every 6 hours to keep the system efficient.
"""

import os
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
import time
import gzip

# Configuration
CLAUDE_DIR = Path.home() / ".claude"
LOG_FILE = CLAUDE_DIR / "logs" / "autonomous_organizer.log"
STATE_FILE = CLAUDE_DIR / "state" / "organizer_state.json"
PID_FILE = CLAUDE_DIR / "logs" / "organizer.pid"

# Organization rules
RULES = {
    # Auto-cleanup old debug files (keep last 30 days)
    "debug_retention_days": 30,

    # Compress old session history (older than 7 days)
    "session_history_compress_days": 7,

    # Archive old logs (older than 60 days)
    "log_archive_days": 60,

    # Remove duplicate backups (keep only latest)
    "consolidate_backups": True,

    # Consolidate duplicate documentation
    "consolidate_docs": True,

    # Check interval (6 hours)
    "check_interval_hours": 6,
}


def log(message, level="INFO"):
    """Write to log file with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

    # Also print to stdout for monitoring
    print(log_entry.strip())


def load_state():
    """Load organizer state"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "last_run": None,
        "total_space_saved": 0,
        "files_cleaned": 0,
        "files_compressed": 0,
        "files_consolidated": 0
    }


def save_state(state):
    """Save organizer state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def get_file_hash(filepath):
    """Calculate MD5 hash of file"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def cleanup_old_debug_files():
    """Remove debug files older than retention period"""
    debug_dir = CLAUDE_DIR / "debug"
    if not debug_dir.exists():
        return 0, 0

    cutoff_date = datetime.now() - timedelta(days=RULES["debug_retention_days"])
    files_removed = 0
    space_saved = 0

    for file in debug_dir.glob("*.txt"):
        if file.stat().st_mtime < cutoff_date.timestamp():
            size = file.stat().st_size
            file.unlink()
            files_removed += 1
            space_saved += size
            log(f"Removed old debug file: {file.name} ({size / 1024 / 1024:.2f} MB)")

    return files_removed, space_saved


def compress_old_session_history():
    """Compress old session history files"""
    session_dir = CLAUDE_DIR / "memory" / "session" / "history"
    if not session_dir.exists():
        return 0, 0

    cutoff_date = datetime.now() - timedelta(days=RULES["session_history_compress_days"])
    files_compressed = 0
    space_saved = 0

    for file in session_dir.glob("*.json"):
        if file.stat().st_mtime < cutoff_date.timestamp():
            # Skip if already compressed
            if (session_dir / f"{file.name}.gz").exists():
                continue

            original_size = file.stat().st_size

            # Compress
            with open(file, 'rb') as f_in:
                with gzip.open(f"{file}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            compressed_size = Path(f"{file}.gz").stat().st_size

            # Remove original
            file.unlink()

            files_compressed += 1
            space_saved += (original_size - compressed_size)
            log(f"Compressed session: {file.name} (saved {(original_size - compressed_size) / 1024:.2f} KB)")

    return files_compressed, space_saved


def consolidate_backup_files():
    """Keep only the latest backup of each file"""
    backup_files = {}
    files_removed = 0
    space_saved = 0

    # Find all .backup files
    for backup in CLAUDE_DIR.rglob("*.backup"):
        base_name = str(backup).replace(".backup", "")

        if base_name not in backup_files:
            backup_files[base_name] = []

        backup_files[base_name].append({
            "path": backup,
            "mtime": backup.stat().st_mtime
        })

    # Keep only the latest backup for each file
    for base_name, backups in backup_files.items():
        if len(backups) > 1:
            # Sort by modification time
            backups.sort(key=lambda x: x["mtime"], reverse=True)

            # Remove all but the latest
            for backup in backups[1:]:
                size = backup["path"].stat().st_size
                backup["path"].unlink()
                files_removed += 1
                space_saved += size
                log(f"Removed duplicate backup: {backup['path'].name}")

    return files_removed, space_saved


def consolidate_documentation():
    """Consolidate duplicate documentation files into docs/"""
    docs_dir = CLAUDE_DIR / "docs"
    docs_dir.mkdir(exist_ok=True)

    files_moved = 0

    # Find all *SUMMARY*.md and *GUIDE*.md files in root
    for pattern in ["*SUMMARY*.md", "*GUIDE*.md", "*SETUP*.md"]:
        for doc in CLAUDE_DIR.glob(pattern):
            if doc.parent == docs_dir:
                continue  # Already in docs/

            target = docs_dir / doc.name

            # Check if target already exists
            if target.exists():
                # Compare content
                if get_file_hash(doc) == get_file_hash(target):
                    # Duplicate - remove source
                    doc.unlink()
                    log(f"Removed duplicate doc: {doc.name}")
                else:
                    # Different content - rename with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d")
                    target = docs_dir / f"{doc.stem}_{timestamp}{doc.suffix}"
                    shutil.move(str(doc), str(target))
                    log(f"Consolidated doc: {doc.name} -> {target.name}")
            else:
                # Move to docs/
                shutil.move(str(doc), str(target))
                log(f"Moved doc: {doc.name} -> docs/")

            files_moved += 1

    return files_moved


def create_directory_index():
    """Create an index of all important directories and their purpose"""
    index = {
        "created": datetime.now().isoformat(),
        "structure": {
            "hooks/": "Event hooks (UserPromptSubmit, SessionStart, etc.)",
            "agents/": "Custom agent definitions",
            "autonomous/": "Autonomous monitoring systems",
            "docs/": "Consolidated documentation",
            "features/": "Feature configurations",
            "knowledge/": "Genius DNA skill registry",
            "memory/": "Cross-session memory system",
            "logs/": "System logs",
            "state/": "Runtime state files",
            "setup/": "Installation scripts",
            "plugins/": "Claude Code plugins",
            "commands/": "Custom commands",
            "skills/": "Skill definitions",
            "debug/": f"Debug files (auto-cleaned after {RULES['debug_retention_days']} days)",
            "projects/": "Project-specific memory",
            "file-history/": "File change history",
        },
        "key_files": {
            "settings.json": "Main configuration",
            "CLAUDE.md": "Global instructions",
            "genius_loader.py": "Genius DNA loader",
            "autonomous_organizer.py": "This self-organizing system",
            "autonomous_orchestrator.py": "System orchestrator",
        },
        "autonomous_systems": {
            "autonomous_organizer.py": f"Cleans and organizes every {RULES['check_interval_hours']}h",
            "hooks/autonomous-agent-teams.py": "Auto-detects team needs",
            "hooks/compaction-manager.py": "Manages context compaction",
            "autonomous/team_monitor.py": "Monitors agent teams",
        }
    }

    index_file = CLAUDE_DIR / "DIRECTORY_INDEX.json"
    with open(index_file, 'w') as f:
        json.dump(index, f, indent=2)

    log(f"Updated directory index: {index_file}")
    return True


def organize():
    """Main organization function"""
    log("=" * 60)
    log("Starting autonomous organization cycle")

    state = load_state()

    # 1. Cleanup old debug files
    log("Phase 1: Cleaning old debug files...")
    files_removed, space_saved = cleanup_old_debug_files()
    state["files_cleaned"] += files_removed
    state["total_space_saved"] += space_saved
    log(f"  Removed {files_removed} old debug files ({space_saved / 1024 / 1024:.2f} MB)")

    # 2. Compress old session history
    log("Phase 2: Compressing old session history...")
    files_compressed, space_saved_compression = compress_old_session_history()
    state["files_compressed"] += files_compressed
    state["total_space_saved"] += space_saved_compression
    log(f"  Compressed {files_compressed} session files ({space_saved_compression / 1024:.2f} KB)")

    # 3. Consolidate backups
    if RULES["consolidate_backups"]:
        log("Phase 3: Consolidating backup files...")
        backups_removed, backup_space_saved = consolidate_backup_files()
        state["files_cleaned"] += backups_removed
        state["total_space_saved"] += backup_space_saved
        log(f"  Removed {backups_removed} duplicate backups ({backup_space_saved / 1024:.2f} KB)")

    # 4. Consolidate documentation
    if RULES["consolidate_docs"]:
        log("Phase 4: Consolidating documentation...")
        docs_moved = consolidate_documentation()
        state["files_consolidated"] += docs_moved
        log(f"  Consolidated {docs_moved} documentation files")

    # 5. Create directory index
    log("Phase 5: Updating directory index...")
    create_directory_index()

    # Update state
    state["last_run"] = datetime.now().isoformat()
    save_state(state)

    # Summary
    log("Organization cycle complete")
    log(f"  Total space saved (lifetime): {state['total_space_saved'] / 1024 / 1024:.2f} MB")
    log(f"  Files cleaned (lifetime): {state['files_cleaned']}")
    log(f"  Files compressed (lifetime): {state['files_compressed']}")
    log(f"  Files consolidated (lifetime): {state['files_consolidated']}")
    log("=" * 60)


def run_daemon():
    """Run as daemon, organizing at regular intervals"""
    # Write PID file
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    log("Autonomous organizer daemon started")
    log(f"Check interval: {RULES['check_interval_hours']} hours")

    try:
        while True:
            organize()

            # Sleep until next check
            sleep_seconds = RULES["check_interval_hours"] * 3600
            log(f"Sleeping for {RULES['check_interval_hours']} hours...")
            time.sleep(sleep_seconds)

    except KeyboardInterrupt:
        log("Daemon stopped by user")
    except Exception as e:
        log(f"Daemon error: {e}", "ERROR")
    finally:
        # Clean up PID file
        if PID_FILE.exists():
            PID_FILE.unlink()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Run once and exit
        organize()
    else:
        # Run as daemon
        run_daemon()
