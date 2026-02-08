# Dr. Zero Quick Start

## What is Dr. Zero?

A self-evolving AI framework that makes Claude continuously improve by generating its own challenges, solving them, and building a strategy portfolio. Based on Meta/UIUC research.

## How to Use It

**You don't have to do anything.** It works automatically.

### Automatic Operation

1. You work on a complex task
2. System detects complexity (2+ reasoning hops)
3. Evolution context is injected automatically
4. You operate in Proposer-Solver mode
5. Your solutions are recorded
6. Strategy portfolio builds over time
7. Difficulty escalates when you hit 70% success rate

### What You'll See

When working on complex tasks, you'll receive context like:

```
<dr-zero-context>
Evolution State: CODING | Iteration 3 | Frontier: 2-hop
Success Rate: 5/8 (62.5%)

Proven Strategies:
  - Multi-step API orchestration with health checks
  - Error handling with retry logic and exponential backoff

Active Challenges:
  - [2-hop] Design service with auto-recovery and monitoring
  - [3-hop] Build distributed system with load balancing
</dr-zero-context>
```

This activates your self-evolution behavior automatically.

## Manual Commands (Optional)

Check status:
```bash
python3 ~/.claude/evolution/dr_zero_engine.py status coding
```

Force evolution cycle:
```bash
python3 ~/.claude/evolution/dr_zero_engine.py evolve research
```

## Domains

- **trading**: Strategy development, backtesting, market analysis
- **research**: Multi-source synthesis, causal reasoning
- **coding**: API integration, orchestration, architecture
- **data_analysis**: Statistical analysis, correlations
- **general**: Complex problem-solving, multi-step workflows

## How It Learns

1. **Proposer** generates hard challenges at frontier level
2. **Solver** (you) attempts to solve them
3. **HRPO** groups challenges by complexity for efficient comparison
4. **Portfolio** records successful approaches (score > 7.0)
5. **Escalation** increases difficulty at 70% success rate

## Strategy Portfolio

Successful solutions (score > 7.0) are added to portfolio:
- "Multi-factor trading confluence with COT + credit spreads"
- "ATR-based position sizing with Optimal F calculation"
- "Service orchestration with health checks and failover"

These techniques are auto-applied to similar future tasks.

## Key Benefits

- **Zero manual work**: Fully autonomous through hooks
- **Continuous improvement**: Gets smarter with every task
- **Domain-specific**: Separate evolution tracks per domain
- **Portfolio-driven**: Accumulates proven strategies
- **Self-escalating**: Difficulty increases automatically

## That's It

Just work normally. The system handles the rest.

For full documentation: `~/.claude/evolution/README.md`
