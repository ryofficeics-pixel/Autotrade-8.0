# 16 — Implementation Roadmap

## Rule

Phases advance by evidence, not calendar pressure. A phase may end with “no viable alpha” while still succeeding technically.

## Phase 0 — Foundation and archive

Deliverables:

- approved documentation set;
- legacy/source manifest and hashes;
- repository structure and contribution rules;
- CI for docs/links/basic security;
- decision and requirement registry.

Exit: [Phase 0 acceptance](13_TESTING_AND_ACCEPTANCE.md#phase-0--documentation).

## Phase 1 — Market truth

Deliverables:

- venue benchmark probes;
- selected CEX decision;
- canonical schemas;
- public/private collectors;
- raw append-only store;
- sequence/staleness/clock health;
- instrument rule registry;
- observe-only dashboard health.

No strategy or order code is needed to complete this phase.

## Phase 2 — Replay and economic truth

Deliverables:

- deterministic replay engine;
- feature causality framework;
- fee/spread/slippage/latency/funding model;
- order/fill state simulator;
- accounting ledger;
- stress/fault scenarios;
- reproducible report artifacts.

## Phase 3 — Risk and PAPER execution shell

Deliverables:

- risk governor and sizing;
- order authority and selected venue PAPER adapter;
- idempotency/reconciliation/restart recovery;
- HALT/PROBATION/override state machine;
- security controls and diagnostics;
- no-strategy smoke policy that always returns CASH.

## Phase 4 — Alpha research tournament

Deliverables:

- hypothesis registry;
- experiment/evidence registry;
- simple baselines and nulls;
- initial families: abstention/cost, funding observation, directional breakout challenger, constrained mean reversion;
- walk-forward/CPCV/holdout/stress/ablation;
- champion/challenger comparison.

Outcome may be zero eligible strategies.

## Phase 5 — PAPER operation

Deliverables:

- manual promotion and arming;
- maximum two positions, 1x initial ceiling;
- live counterfactual shadow stream;
- predicted vs realized execution calibration;
- dashboard and runbooks;
- soak, restart, disconnect, and override drills.

## Phase 6 — Controlled evolution

Deliverables:

- scheduled offline challenger generation;
- bounded optimizer/search integration;
- drift and calibration monitoring;
- immutable negative-result registry;
- manual promote/rollback/quarantine workflow.

## Phase 7 — Optional leverage review

3x review is allowed only after sufficient PAPER evidence and stable execution calibration. 5x is a separate later review. Neither is required for project success.

## Deferred roadmap

- VPS migration after local stability;
- cross-venue funding/basis after capital and operational review;
- additional exchange adapters;
- on-chain/social data;
- RL experiments; and
- any LIVE discussion.

## Cost discipline

- free exchange-native data first;
- local storage/compute first;
- no premium data or AI API;
- modular monolith rather than infrastructure sprawl;
- VPS <= Rp150,000/month when migration gate passes;
- measure before buying capacity.

## First implementation sequence

1. Repository skeleton and schemas.
2. Venue benchmark/read-only collector.
3. Raw store and integrity monitor.
4. Deterministic replay.
5. Accounting/cost simulator.
6. Risk governor.
7. PAPER adapter/order state/reconciliation.
8. Dashboard/incident controls.
9. Research tournament.
10. First manual PAPER promotion, if any candidate actually qualifies.
