#!/bin/bash
PLIST="$HOME/Library/LaunchAgents/com.claude.organizer.plist"
launchctl unload "$PLIST"
echo "✅ Autonomous organizer stopped"
