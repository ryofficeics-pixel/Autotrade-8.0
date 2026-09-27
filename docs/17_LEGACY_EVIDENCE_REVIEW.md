# 17 — Legacy Evidence and Source Review

## Purpose

Preserve useful lessons without inheriting unproven code or marketing claims.

## AUTOTRADE 7 failure baseline

Prior audited evidence reported:

- 427 normal closes;
- net PnL approximately -24.8442 USDT;
- profit factor approximately 0.5062; and
- gross price PnL negative before fees.

Conclusion: the main failure was missing/negative alpha, not merely fees, dashboard, or accounting. Threshold tuning cannot repair a mechanism that loses before costs.

Known evidence gaps included five-second REST-style pricing/optimistic fills and missing synchronized L2/trades, latency, queue position, partial fills, realistic funding, and adverse-selection modeling.

## Social-media screenshots

The screenshots claim a named multi-agent system transformed a very small balance through a sequence of agents and a risk gate. They present concepts such as:

- abstaining for long periods;
- separate discovery/social/wallet/execution-route signals;
- a final SENTRY gate;
- confidence-based execution; and
- compounding.

Useful concept: separation of independent evidence streams and a final veto.

Rejected claims/assumptions:

- screenshots are not audited trading records;
- “90% win-rate wallets,” sub-2% slippage, and 0.92 confidence have no disclosed methodology;
- the reported balance multiplication is economically implausible as a design target;
- social/wallet data is outside bootstrap scope; and
- agent naming does not establish independence or alpha.

The screenshots are hypothesis inspiration only.

## TensorTrade screenshot

TensorTrade is presented as an RL trading framework. A framework can organize an environment/agent/reward pipeline but cannot repair biased data or an unrealistic simulator. RL is deferred until deterministic market/execution truth exists and simple baselines are beaten.

## Indicator screenshot

The stochastic + volume support/resistance + volume combination is a discretionary equity-screening claim, not evidence for USDT perpetuals. Volume-zone context may be tested as a feature, but it cannot be imported as a strategy without preregistration, causal data, ablation, and out-of-sample validation.

## Phase 1 ZIP review

The repository ZIP contains a prototype economic/risk/research kernel with positive concepts:

- explicit cost breakdown;
- CASH allocation;
- SENTRY gates;
- capital states;
- hedge supervision;
- funding/basis/breakout/volume-zone modules;
- lifecycle and validation utilities; and
- unit tests.

It is not an implementation baseline because:

- key thresholds and scores are placeholders;
- expected edge/evidence are supplied or simplified rather than calibrated from decision-time data;
- unit tests prove arithmetic/branch behavior, not economic validity;
- no production-grade data capture, venue adapter, reconciliation, persistence, or restart recovery exists;
- short-horizon capital-efficiency scoring can reward turnover;
- cross-venue modules conflict with the bootstrap scope/capital; and
- synthetic tests cannot substitute for sealed real-market evidence.

Therefore the ZIP is archived reference material. Concepts may be reimplemented only from approved contracts and tests.

## Source manifest

At documentation time, the repository contains:

- nine PNG screenshots;
- `autotrade8_phase1.zip`; and
- this documentation set.

The repository ZIP and separately uploaded ZIP are different versions. Never assume identical content from filename alone; exact hashes and sizes are recorded in [the source manifest](21_SOURCE_MANIFEST.md).

## What survives

- CASH/no-trade as first-class action;
- explicit cost and uncertainty decomposition;
- fail-closed SENTRY gate;
- manual lifecycle/promotion;
- deterministic replay/chronological validation intent;
- append-only evidence and decision reasons; and
- dashboard observability concepts.

## What is discarded

- every prior alpha and tuned threshold as production logic;
- any inferred profit claim;
- forced frequency/return target;
- optimistic fill assumptions;
- uncalibrated confidence/evidence scores;
- cross-venue execution in bootstrap; and
- automatic evolution of the running strategy.
