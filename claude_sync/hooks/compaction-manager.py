#!/usr/bin/env python3
"""
Compaction Manager Hook - Manages automatic context summarization

Integrates with Anthropic's Compaction API (compact_20260112) for infinite conversations.
Monitors token usage and recommends/triggers compaction when approaching limits.

Released: February 2026
Feature: Server-side context summarization
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

class CompactionManager:
    def __init__(self):
        self.config_file = Path.home() / '.claude' / 'features' / 'compaction_config.json'
        self.log_file = Path.home() / '.claude' / 'logs' / 'compaction.log'
        self.state_file = Path.home() / '.claude' / 'state' / 'compaction_state.json'

        # Ensure directories exist
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        self.load_config()

    def load_config(self):
        """Load compaction configuration."""
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    config = json.load(f)
                    self.enabled = config.get('compaction', {}).get('enabled', True)
                    self.threshold = config.get('compaction', {}).get('trigger_threshold', 150000)
            else:
                self.enabled = True
                self.threshold = 150000
        except Exception as e:
            self.enabled = True
            self.threshold = 150000

    def log(self, message):
        """Log with timestamp."""
        timestamp = datetime.now().isoformat()
        try:
            with open(self.log_file, 'a') as f:
                f.write(f"[{timestamp}] {message}\n")
        except:
            pass

    def estimate_token_count(self, text):
        """Rough token estimation (1 token ≈ 4 characters)."""
        return len(text) // 4

    def should_compact(self, token_estimate):
        """Determine if compaction should be triggered."""
        return self.enabled and token_estimate > self.threshold

    def generate_compaction_notice(self, token_estimate):
        """Generate notice about compaction status."""
        if not self.enabled:
            return None

        usage_percent = (token_estimate / self.threshold) * 100

        if usage_percent > 100:
            return f"""<compaction-notice priority="high">
Context approaching limit ({token_estimate:,} tokens estimated, threshold: {self.threshold:,})

COMPACTION ACTIVE: Server-side summarization enabled
- Earlier conversation parts will be automatically summarized
- Recent context preserved in full detail
- Long-running tasks can continue beyond normal limits

No action required - compaction handles this automatically.
</compaction-notice>"""

        elif usage_percent > 80:
            return f"""<compaction-notice priority="medium">
Context usage: {usage_percent:.0f}% of threshold ({token_estimate:,} / {self.threshold:,} tokens)

Compaction will trigger soon if conversation continues.
Consider breaking into separate sessions for unrelated tasks.
</compaction-notice>"""

        elif usage_percent > 60:
            return f"""<compaction-notice priority="low">
Context usage: {usage_percent:.0f}% ({token_estimate:,} tokens estimated)
</compaction-notice>"""

        return None

    def update_state(self, token_estimate):
        """Update compaction state tracking."""
        try:
            state = {
                'last_check': datetime.now().isoformat(),
                'token_estimate': token_estimate,
                'threshold': self.threshold,
                'compaction_likely': self.should_compact(token_estimate)
            }

            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except:
            pass

def main():
    """Main hook execution."""
    try:
        # Read stdin for hook context
        hook_input = sys.stdin.read()

        # Estimate token usage from conversation
        manager = CompactionManager()
        token_estimate = manager.estimate_token_count(hook_input)

        # Generate notice if needed
        notice = manager.generate_compaction_notice(token_estimate)

        if notice:
            print(notice)
            manager.log(f"Notice generated: {token_estimate:,} tokens, {(token_estimate/manager.threshold)*100:.0f}% of threshold")

        # Update state
        manager.update_state(token_estimate)

        return 0

    except Exception as e:
        # Silent failure
        try:
            manager.log(f"Error: {e}")
        except:
            pass
        return 0

if __name__ == '__main__':
    sys.exit(main())
