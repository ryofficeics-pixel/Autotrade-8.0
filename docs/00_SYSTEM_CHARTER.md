# 00 — System Charter

## Mission

AUTOTRADE 8.0 allocates a small PAPER account only when a reproducible, executable, risk-adjusted opportunity is stronger than holding cash after pessimistic costs.

The primary question is:

> What is the highest-quality use of capital now, including CASH, after fees, spread, slippage, latency, funding, uncertainty, and failure risk?

## Truth hierarchy

When sources disagree, the system follows this order:

1. Reconciled venue/account state.
2. Raw exchange events with valid sequence and timestamps.
3. Deterministic derived state.
4. Frozen strategy and risk configuration.
5. Dashboard projections and summaries.

The dashboard, a model prediction, a screenshot, and an operator assumption can never override venue/account truth.

## Economic objective

The system optimizes long-run survival and net expectancy, not activity.

Priority order:

1. Prevent unknown or unbounded exposure.
2. Preserve auditability and market/account truth.
3. Avoid trades without net edge.
4. Control drawdown and tail loss.
5. Improve net risk-adjusted return.
6. Improve capital utilization only after all earlier priorities hold.

## Explicit non-goals

- Guaranteed or uninterrupted profit.
- Forced 20–30 trades/day or any other quota.
- Recovery of past losses.
- Maximizing win rate, turnover, or gross PnL.
- Automatic LIVE deployment.
- LLM-driven trading.
- Autonomous mutation of running strategies or risk limits.
- Copying social-media claims, wallets, or indicators without causal evidence.

## Operating assumptions

- Starting equity is 300 USDT in PAPER.
- The first production-shaped system supports one CEX and USDT perpetuals.
- Venue choice remains adapter-based and evidence-driven.
- At most two positions may be open.
- Multiple trades/day are allowed but never required.
- Cross-venue strategies, on-chain signals, social signals, and RL are deferred.
- Laptop operation comes first; a low-cost VPS follows only after stability.
- Recurring infrastructure budget is capped at Rp150,000/month unless explicitly revised.

## Invariants

The following must always be true:

1. There is exactly one order authority.
2. No action occurs without a unique decision ID and configuration version.
3. No new exposure is allowed when market data, account state, or configuration integrity is uncertain.
4. Position sizing is derived from loss budget; leverage never defines acceptable loss.
5. CASH is always a valid outcome.
6. Research data never includes information unavailable at decision time.
7. Running PAPER artifacts are immutable; evolution produces a separate challenger.
8. Strategy promotion requires a human approval record.
9. Resume override cannot bypass hard integrity failures.
10. Every order, rejection, halt, override, and reconciliation event is append-only.

## Meaning of success

The user aspiration is +30% in 30 days. It is not an engineering acceptance criterion because pursuing it directly creates pressure to overfit and over-risk.

Engineering success means:

- deterministic data and replay;
- realistic, measured execution error;
- positive out-of-sample expectancy after conservative costs;
- acceptable drawdown and tail behavior;
- stable operation and complete auditability; and
- the discipline to remain in CASH when no edge qualifies.

## Authority

This charter dominates lower-level documents. Conflicts must be resolved by updating the decision register; code must not guess.
