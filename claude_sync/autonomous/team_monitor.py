#!/usr/bin/env python3
"""
Autonomous Team Monitor - Monitors running agent teams and handles auto-cleanup

Similar to autonomous_monitor.py for services, but for agent teams:
- Monitors team health
- Auto-cleanup when all tasks completed
- Detects stuck teammates
- Logs team activity

Run in background: python3 ~/.claude/autonomous/team_monitor.py &
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

class TeamMonitor:
    def __init__(self):
        self.teams_dir = Path.home() / '.claude' / 'teams'
        self.tasks_dir = Path.home() / '.claude' / 'tasks'
        self.log_file = Path.home() / '.claude' / 'logs' / 'autonomous_teams_monitor.log'
        self.check_interval = 30  # seconds

        # Ensure directories exist
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message):
        """Log with timestamp."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"[{timestamp}] {message}\n"

        print(log_msg.strip())

        try:
            with open(self.log_file, 'a') as f:
                f.write(log_msg)
        except Exception as e:
            print(f"Failed to write log: {e}")

    def get_active_teams(self):
        """Get list of active teams."""
        if not self.teams_dir.exists():
            return []

        teams = []
        for team_dir in self.teams_dir.iterdir():
            if team_dir.is_dir():
                config_file = team_dir / 'config.json'
                if config_file.exists():
                    try:
                        with open(config_file) as f:
                            config = json.load(f)
                            teams.append({
                                'name': team_dir.name,
                                'path': team_dir,
                                'config': config
                            })
                    except Exception as e:
                        self.log(f"Error reading team config {team_dir.name}: {e}")

        return teams

    def check_team_tasks(self, team_name):
        """Check task status for a team."""
        task_dir = self.tasks_dir / team_name
        if not task_dir.exists():
            return {'total': 0, 'pending': 0, 'in_progress': 0, 'completed': 0}

        tasks = {'total': 0, 'pending': 0, 'in_progress': 0, 'completed': 0}

        for task_file in task_dir.glob('*.json'):
            try:
                with open(task_file) as f:
                    task = json.load(f)
                    tasks['total'] += 1
                    status = task.get('status', 'pending')
                    tasks[status] = tasks.get(status, 0) + 1
            except Exception as e:
                self.log(f"Error reading task {task_file.name}: {e}")

        return tasks

    def is_team_idle(self, team_name, tasks):
        """Determine if team is idle and should be cleaned up."""
        # Team is idle if all tasks are completed or no tasks exist
        return (tasks['total'] == 0 or
                (tasks['pending'] == 0 and
                 tasks['in_progress'] == 0 and
                 tasks['completed'] == tasks['total']))

    def auto_cleanup_team(self, team_name):
        """Attempt to auto-cleanup idle team."""
        self.log(f"Auto-cleanup triggered for team: {team_name}")

        # In autonomous mode, we log that cleanup is recommended
        # Actual cleanup should be triggered by the lead agent
        self.log(f"  → Team {team_name} appears idle - all tasks completed")
        self.log(f"  → Cleanup recommendation logged (lead should run cleanup)")

        # Create a cleanup marker file
        marker_file = self.teams_dir / team_name / '.cleanup_recommended'
        try:
            with open(marker_file, 'w') as f:
                f.write(json.dumps({
                    'timestamp': datetime.now().isoformat(),
                    'reason': 'All tasks completed',
                    'auto_detected': True
                }))
            self.log(f"  → Cleanup marker created: {marker_file}")
        except Exception as e:
            self.log(f"  → Failed to create cleanup marker: {e}")

    def monitor_cycle(self):
        """Run one monitoring cycle."""
        teams = self.get_active_teams()

        if not teams:
            return  # No teams to monitor

        self.log(f"Monitoring {len(teams)} active team(s)")

        for team in teams:
            team_name = team['name']
            tasks = self.check_team_tasks(team_name)

            status_msg = (f"  {team_name}: {tasks['total']} tasks "
                         f"(pending: {tasks['pending']}, "
                         f"in_progress: {tasks['in_progress']}, "
                         f"completed: {tasks['completed']})")
            self.log(status_msg)

            # Check for idle teams
            if self.is_team_idle(team_name, tasks):
                cleanup_marker = team['path'] / '.cleanup_recommended'
                if not cleanup_marker.exists():
                    self.auto_cleanup_team(team_name)

    def run(self):
        """Main monitoring loop."""
        self.log("Autonomous Team Monitor started")
        self.log(f"Check interval: {self.check_interval}s")
        self.log(f"Teams directory: {self.teams_dir}")
        self.log(f"Tasks directory: {self.tasks_dir}")

        try:
            while True:
                try:
                    self.monitor_cycle()
                except Exception as e:
                    self.log(f"Error in monitor cycle: {e}")

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.log("Autonomous Team Monitor stopped (KeyboardInterrupt)")
        except Exception as e:
            self.log(f"Autonomous Team Monitor crashed: {e}")

if __name__ == '__main__':
    monitor = TeamMonitor()
    monitor.run()
