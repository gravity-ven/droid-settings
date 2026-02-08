#!/usr/bin/env python3
"""
MANUS Browser Automation - Full Implementation
Uses Chrome DevTools MCP integration
"""

import sys
import json
from pathlib import Path

# Add manus agent to path
sys.path.insert(0, str(Path(__file__).parent))
from manus_computer_use import ManusComputerUseAgent, Action, ActionStatus

class BrowserAutomation:
    """
    High-level browser automation using MANUS agent

    Built-in tasks:
    - Web scraping
    - Form filling
    - Navigation testing
    - Screenshot capture
    - Data extraction
    """

    def __init__(self):
        self.agent = ManusComputerUseAgent(max_attempts=5)

    def navigate_and_screenshot(self, url: str, output_path: str = None) -> dict:
        """
        Navigate to URL and take screenshot

        Args:
            url: Target URL
            output_path: Optional path to save screenshot

        Returns:
            Execution results
        """
        actions = [
            Action(
                name="open_new_page",
                tool="mcp__chrome-devtools__new_page",
                params={'url': url, 'background': False},
                description=f"Open {url} in new page",
                max_attempts=3
            ),
            Action(
                name="wait_for_load",
                tool="mcp__chrome-devtools__wait_for",
                params={'text': '', 'timeout': 10000},
                description="Wait for page load",
                max_attempts=2
            ),
            Action(
                name="take_screenshot",
                tool="mcp__chrome-devtools__take_screenshot",
                params={'fullPage': True, 'format': 'png', 'filePath': output_path} if output_path else {'fullPage': True},
                description="Capture full page screenshot",
                max_attempts=3
            )
        ]

        return self.agent.execute_plan(actions, self._mock_executor)

    def fill_form(self, form_data: dict) -> dict:
        """
        Fill out a form with provided data

        Args:
            form_data: Dict of {uid: value} pairs

        Returns:
            Execution results
        """
        # Take snapshot first to get UIDs
        actions = [
            Action(
                name="take_snapshot",
                tool="mcp__chrome-devtools__take_snapshot",
                params={},
                description="Capture page snapshot to identify form fields",
                max_attempts=3
            )
        ]

        # Add fill actions for each field
        for uid, value in form_data.items():
            actions.append(
                Action(
                    name=f"fill_{uid}",
                    tool="mcp__chrome-devtools__fill",
                    params={'uid': uid, 'value': value, 'includeSnapshot': False},
                    description=f"Fill field {uid} with {value}",
                    max_attempts=5
                )
            )

        return self.agent.execute_plan(actions, self._mock_executor)

    def scrape_data(self, url: str, selectors: dict) -> dict:
        """
        Navigate to URL and extract data using JavaScript

        Args:
            url: Target URL
            selectors: Dict of {name: selector} pairs

        Returns:
            Execution results with extracted data
        """
        actions = [
            Action(
                name="navigate",
                tool="mcp__chrome-devtools__navigate_page",
                params={'url': url, 'type': 'url'},
                description=f"Navigate to {url}",
                max_attempts=3
            )
        ]

        # Add extraction for each selector
        for name, selector in selectors.items():
            js_function = f"""() => {{
                const element = document.querySelector('{selector}');
                return element ? element.textContent.trim() : null;
            }}"""

            actions.append(
                Action(
                    name=f"extract_{name}",
                    tool="mcp__chrome-devtools__evaluate_script",
                    params={'function': js_function},
                    description=f"Extract {name} using selector: {selector}",
                    max_attempts=5
                )
            )

        return self.agent.execute_plan(actions, self._mock_executor)

    def test_navigation(self, urls: list) -> dict:
        """
        Test navigation to multiple URLs

        Args:
            urls: List of URLs to test

        Returns:
            Execution results
        """
        actions = []

        for i, url in enumerate(urls):
            actions.extend([
                Action(
                    name=f"navigate_{i}",
                    tool="mcp__chrome-devtools__navigate_page",
                    params={'url': url, 'type': 'url'},
                    description=f"Navigate to {url}",
                    max_attempts=3
                ),
                Action(
                    name=f"verify_{i}",
                    tool="mcp__chrome-devtools__take_snapshot",
                    params={'verbose': False},
                    description=f"Verify page loaded",
                    max_attempts=2
                )
            ])

        return self.agent.execute_plan(actions, self._mock_executor)

    def _mock_executor(self, action: Action) -> dict:
        """
        Mock executor for demonstration
        In production, this would call actual Chrome DevTools MCP tools
        """
        print(f"  Tool: {action.tool}")
        print(f"  Params: {json.dumps(action.params, indent=4)}")

        # Simulate success/failure based on attempt number
        # First 2 attempts might fail, then succeed
        if action.current_attempt >= 2:
            return {
                'success': True,
                'data': {'result': f'Mock result for {action.name}'}
            }
        else:
            return {
                'success': False,
                'error': f'Mock failure (attempt {action.current_attempt})'
            }


def main():
    """Demo the browser automation"""
    print("\n" + "="*70)
    print("MANUS BROWSER AUTOMATION - DEMO")
    print("="*70 + "\n")

    automation = BrowserAutomation()

    # Demo 1: Navigate and screenshot
    print("\n📸 Demo 1: Navigate and Screenshot")
    print("-" * 70)
    automation.navigate_and_screenshot(
        url="https://example.com",
        output_path="/tmp/example_screenshot.png"
    )

    # Demo 2: Form filling
    print("\n📝 Demo 2: Form Filling")
    print("-" * 70)
    automation.fill_form({
        'uid_1': 'John Doe',
        'uid_2': 'john@example.com',
        'uid_3': 'My message here'
    })

    # Demo 3: Data scraping
    print("\n🔍 Demo 3: Data Scraping")
    print("-" * 70)
    automation.scrape_data(
        url="https://news.ycombinator.com",
        selectors={
            'title': 'title',
            'first_story': '.titleline > a',
            'top_comment': '.comment'
        }
    )

    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
