#!/bin/bash
PLIST="$HOME/Library/LaunchAgents/com.claude.organizer.plist"
launchctl load "$PLIST"
echo "✅ Autonomous organizer started"
