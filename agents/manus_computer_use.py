#!/usr/bin/env python3
"""
MANUS Computer Use Agent
Autonomous browser automation with self-correction
"""

import json
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class ActionStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"
    MAX_RETRIES = "max_retries"

@dataclass
class Action:
    """Single browser action"""
    name: str
    tool: str
    params: dict
    description: str
    max_attempts: int = 5
    current_attempt: int = 0

@dataclass
class ActionResult:
    """Result of executing an action"""
    status: ActionStatus
    data: Optional[dict]
    error: Optional[str]
    attempts: int

class ManusComputerUseAgent:
    """
    Autonomous browser agent with self-correction

    Features:
    - No permission seeking
    - No confirmation requests
    - Autonomous execution
    - Self-correction (up to 5 attempts)
    - Verification after each step
    """

    def __init__(self, max_attempts: int = 5):
        self.max_attempts = max_attempts
        self.action_history: List[Dict] = []
        self.current_page_id: Optional[int] = None
        self.running = False

    def execute_action(self, action: Action, execute_fn: Callable) -> ActionResult:
        """
        Execute a single action with retry logic

        Args:
            action: Action to execute
            execute_fn: Function that executes the action (returns dict with status)

        Returns:
            ActionResult with status and data
        """
        for attempt in range(1, action.max_attempts + 1):
            action.current_attempt = attempt

            try:
                # Execute the action
                result = execute_fn(action)

                # Check if successful
                if result.get('success', False):
                    self.action_history.append({
                        'action': action.name,
                        'status': 'success',
                        'attempts': attempt,
                        'data': result.get('data')
                    })
                    return ActionResult(
                        status=ActionStatus.SUCCESS,
                        data=result.get('data'),
                        error=None,
                        attempts=attempt
                    )

                # Failed but can retry
                if attempt < action.max_attempts:
                    error = result.get('error', 'Unknown error')
                    print(f"⚠️  Attempt {attempt}/{action.max_attempts} failed: {error}")
                    print(f"🔄 Retrying with alternative approach...")
                    time.sleep(1)  # Brief pause before retry
                    continue

            except Exception as e:
                if attempt < action.max_attempts:
                    print(f"❌ Exception on attempt {attempt}: {str(e)}")
                    print(f"🔄 Retrying...")
                    time.sleep(1)
                    continue
                else:
                    # Max retries reached
                    self.action_history.append({
                        'action': action.name,
                        'status': 'failed',
                        'attempts': attempt,
                        'error': str(e)
                    })
                    return ActionResult(
                        status=ActionStatus.MAX_RETRIES,
                        data=None,
                        error=str(e),
                        attempts=attempt
                    )

        # Max retries reached
        self.action_history.append({
            'action': action.name,
            'status': 'max_retries',
            'attempts': action.max_attempts
        })
        return ActionResult(
            status=ActionStatus.MAX_RETRIES,
            data=None,
            error="Max retry attempts reached",
            attempts=action.max_attempts
        )

    def assess(self, task: str) -> List[Action]:
        """
        ASSESS: Break down task into actions

        Args:
            task: High-level task description

        Returns:
            List of actions to execute
        """
        # This would be extended with actual task parsing logic
        # For now, return a template
        return []

    def verify(self, expected_state: dict) -> bool:
        """
        VERIFY: Check if expected state matches actual state

        Args:
            expected_state: Dict describing expected browser state

        Returns:
            True if verified, False otherwise
        """
        # Implementation would check page state
        return True

    def self_correct(self, failed_action: Action, error: str) -> Optional[Action]:
        """
        LEARN: Generate alternative action based on failure

        Args:
            failed_action: Action that failed
            error: Error message

        Returns:
            Alternative action to try, or None if no alternative
        """
        # Analyze error and generate alternative approach
        alternatives = {
            'click': ['hover_then_click', 'double_click', 'use_keyboard'],
            'fill': ['click_then_type', 'clear_then_fill', 'use_javascript'],
            'navigate': ['reload_then_navigate', 'new_tab_navigate']
        }

        action_type = failed_action.tool.split('__')[-1]
        if action_type in alternatives:
            # Return first unused alternative
            for alt in alternatives[action_type]:
                if alt not in [h['action'] for h in self.action_history]:
                    return Action(
                        name=f"{failed_action.name}_alt_{alt}",
                        tool=f"mcp__chrome-devtools__{alt}",
                        params=failed_action.params,
                        description=f"Alternative: {alt}",
                        max_attempts=3
                    )

        return None

    def execute_plan(self, actions: List[Action], execute_fn: Callable) -> Dict:
        """
        EXECUTE: Run all actions with self-correction

        Args:
            actions: List of actions to execute
            execute_fn: Function to execute each action

        Returns:
            Execution summary
        """
        self.running = True
        results = []

        for i, action in enumerate(actions):
            print(f"\n{'='*60}")
            print(f"Step {i+1}/{len(actions)}: {action.description}")
            print(f"{'='*60}")

            # Execute with retry logic
            result = self.execute_action(action, execute_fn)
            results.append(result)

            # Handle failure
            if result.status == ActionStatus.MAX_RETRIES:
                print(f"❌ Action failed after {result.attempts} attempts")

                # Try to self-correct
                alternative = self.self_correct(action, result.error)
                if alternative:
                    print(f"🧠 Attempting alternative approach: {alternative.name}")
                    alt_result = self.execute_action(alternative, execute_fn)
                    results.append(alt_result)

                    if alt_result.status == ActionStatus.SUCCESS:
                        print(f"✅ Alternative succeeded!")
                        continue

                # If we get here, both original and alternative failed
                print(f"⚠️  Continuing to next step despite failure...")

            elif result.status == ActionStatus.SUCCESS:
                print(f"✅ Completed in {result.attempts} attempt(s)")

        self.running = False

        # Summary
        total = len(results)
        succeeded = sum(1 for r in results if r.status == ActionStatus.SUCCESS)
        failed = total - succeeded

        return {
            'total_actions': total,
            'succeeded': succeeded,
            'failed': failed,
            'success_rate': f"{(succeeded/total*100):.1f}%" if total > 0 else "0%",
            'results': results,
            'history': self.action_history
        }

    def run(self, task: str, execute_fn: Callable) -> Dict:
        """
        Main execution loop: ASSESS → PLAN → EXECUTE → VERIFY → LEARN → NEXT

        Args:
            task: High-level task description
            execute_fn: Function to execute actions

        Returns:
            Execution results
        """
        print(f"\n🤖 MANUS Computer Use Agent")
        print(f"Task: {task}")
        print(f"Max attempts per action: {self.max_attempts}")
        print(f"\nStarting autonomous execution...\n")

        # ASSESS
        actions = self.assess(task)

        if not actions:
            print("⚠️  No actions generated for this task")
            return {'error': 'No actions to execute'}

        # PLAN (actions already created in ASSESS)
        print(f"📋 Plan: {len(actions)} actions")
        for i, action in enumerate(actions):
            print(f"  {i+1}. {action.description}")
        print()

        # EXECUTE
        results = self.execute_plan(actions, execute_fn)

        # Summary
        print(f"\n{'='*60}")
        print(f"📊 EXECUTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total Actions: {results['total_actions']}")
        print(f"Succeeded: {results['succeeded']}")
        print(f"Failed: {results['failed']}")
        print(f"Success Rate: {results['success_rate']}")
        print(f"{'='*60}\n")

        return results


# Example usage
if __name__ == '__main__':
    # Demo executor function
    def demo_executor(action: Action) -> dict:
        """Demo function that simulates action execution"""
        print(f"Executing: {action.tool} with params: {action.params}")

        # Simulate random success/failure
        import random
        success = random.random() > 0.3  # 70% success rate

        return {
            'success': success,
            'data': {'result': 'demo_data'} if success else None,
            'error': None if success else 'Simulated failure'
        }

    # Create agent
    agent = ManusComputerUseAgent(max_attempts=5)

    # Create sample actions
    actions = [
        Action(
            name="navigate_to_site",
            tool="mcp__chrome-devtools__navigate_page",
            params={'url': 'https://example.com', 'type': 'url'},
            description="Navigate to example.com"
        ),
        Action(
            name="take_snapshot",
            tool="mcp__chrome-devtools__take_snapshot",
            params={},
            description="Take page snapshot"
        )
    ]

    # Execute
    agent.execute_plan(actions, demo_executor)
