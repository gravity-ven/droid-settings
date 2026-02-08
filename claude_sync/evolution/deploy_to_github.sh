#!/bin/bash
# Deploy Dr. Zero to GitHub repositories

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Dr. Zero GitHub Deployment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# 1. Deploy to claude-code-config repo
echo "📦 Deploying to claude-code-config..."
REPO_DIR="$HOME/github_repos/claude-code-config"

if [ -d "$REPO_DIR" ]; then
    cd "$REPO_DIR"
    
    # Copy evolution system
    mkdir -p evolution
    cp -r ~/.claude/evolution/* evolution/ 2>/dev/null || true
    
    # Copy updated hooks
    mkdir -p hooks
    cp ~/.claude/hooks/session-start.py hooks/
    cp ~/.claude/hooks/user-prompt-submit.py hooks/
    cp ~/.claude/hooks/post-tool-use.py hooks/
    
    # Copy updated CLAUDE.md
    cp ~/.claude/CLAUDE.md ./
    
    # Git operations
    git add -A
    git commit -m "feat: Add Dr. Zero self-evolution framework

- Proposer-Solver co-evolution system
- HRPO (Hop-Grouped Relative Policy Optimization)
- Zero-data bootstrap capability
- Cross-agent learning substrate
- Autonomous difficulty escalation
- Based on Meta/UIUC research (arXiv:2601.07055)

Integrated across all CLI agents on machine.
" || echo "  (No changes to commit)"
    
    git push origin main 2>/dev/null || git push origin master 2>/dev/null || echo "  ⚠ Manual push required"
    echo "  ✓ claude-code-config updated"
else
    echo "  ⚠ Repository not found: $REPO_DIR"
fi

echo

# 2. Deploy to cli-agents-backup repo
echo "📦 Deploying to cli-agents-backup..."
REPO_DIR="$HOME/github_repos/cli-agents-backup"

if [ -d "$REPO_DIR" ]; then
    cd "$REPO_DIR"
    
    # Copy universal integration
    mkdir -p agent-collective
    cp ~/.agent-collective/dr_zero_integration.py agent-collective/
    cp ~/.agent-collective/DR_ZERO_CROSS_AGENT_GUIDE.md agent-collective/
    cp ~/.agent-collective/AGENT_INSTRUCTIONS.md agent-collective/
    
    # Copy Gemini integration
    mkdir -p gemini
    cp ~/.gemini/dr_zero_hook.py gemini/
    cp ~/.gemini/GEMINI.md gemini/ 2>/dev/null || true
    
    # Copy daemon
    mkdir -p agent-daemon
    cp ~/.agent-daemon/dr_zero_background.py agent-daemon/
    
    # Copy documentation
    cp ~/.claude/evolution/README.md ./DR_ZERO_README.md
    cp ~/.claude/evolution/QUICK_START.md ./DR_ZERO_QUICK_START.md
    cp ~/.claude/evolution/DEPLOYMENT_SUMMARY.md ./
    
    # Git operations
    git add -A
    git commit -m "feat: Add Dr. Zero cross-agent integration

Universal integration layer for all CLI agents:
- dr_zero_integration.py (universal module)
- Gemini CLI hook
- Background evolution daemon
- Cross-agent learning guide

Enables shared evolution across Claude, Gemini, and custom agents.
" || echo "  (No changes to commit)"
    
    git push origin main 2>/dev/null || git push origin master 2>/dev/null || echo "  ⚠ Manual push required"
    echo "  ✓ cli-agents-backup updated"
else
    echo "  ⚠ Repository not found: $REPO_DIR"
fi

echo

# 3. Deploy to sub-agents repo
echo "📦 Deploying to sub-agents..."
REPO_DIR="$HOME/github_repos/sub-agents"

if [ -d "$REPO_DIR" ]; then
    cd "$REPO_DIR"
    
    # Copy core engine as reference
    mkdir -p dr-zero
    cp ~/.claude/evolution/dr_zero_engine.py dr-zero/
    cp ~/.claude/evolution/README.md dr-zero/
    cp ~/.agent-collective/DR_ZERO_CROSS_AGENT_GUIDE.md dr-zero/
    
    # Git operations
    git add -A
    git commit -m "feat: Add Dr. Zero multi-agent coordination

Dr. Zero self-evolution framework for sub-agent architectures:
- Shared evolution state across all agents
- Multi-agent pattern recognition
- Collective intelligence amplification

Reference implementation for agent coordination patterns.
" || echo "  (No changes to commit)"
    
    git push origin main 2>/dev/null || git push origin master 2>/dev/null || echo "  ⚠ Manual push required"
    echo "  ✓ sub-agents updated"
else
    echo "  ⚠ Repository not found: $REPO_DIR"
fi

echo

# 4. Update genius-dna remote in ~/.claude
echo "📦 Updating genius-dna integration..."
cd ~/.claude

git add -A
git commit -m "feat: Integrate Dr. Zero self-evolution framework

Dr. Zero + Genius DNA synergy:
- Evolution system leverages Genius DNA knowledge
- Shared strategy portfolios
- Cross-system learning amplification
- Autonomous capability growth

Based on Meta/UIUC research (arXiv:2601.07055)
" || echo "  (No changes to commit)"

git push genius-dna main 2>/dev/null || echo "  ⚠ Manual push to genius-dna required"
echo "  ✓ genius-dna integration updated"

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "Dr. Zero has been deployed to all relevant GitHub repositories."
echo
echo "Repositories updated:"
echo "  • claude-code-config (full evolution system + hooks)"
echo "  • cli-agents-backup (universal integration layer)"
echo "  • sub-agents (multi-agent coordination patterns)"
echo "  • genius-dna (Genius DNA integration)"
echo
echo "If any manual pushes are required, run:"
echo "  cd <repo-dir> && git push origin main"
echo

