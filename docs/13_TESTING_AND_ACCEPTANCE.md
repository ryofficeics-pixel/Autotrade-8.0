# 13 — Testing and Acceptance

## Test pyramid

1. Domain unit/property tests.
2. Component contract tests.
3. Deterministic replay/golden tests.
4. Venue-adapter protocol tests.
5. End-to-end PAPER sandbox tests.
6. Fault-injection/soak tests.
7. Research/economic validation.

Passing software tests proves correctness of implementation, not profitability.

## Mandatory domain tests

- price/quantity rounding never increases risk;
- minimum notional rejection;
- fee/funding accounting at precision boundaries;
- position and portfolio risk limits;
- correlation cluster budget;
- 1x/3x/5x ceiling behavior;
- stale/invalid data blocks entry;
- order intent expiry;
- duplicate decision/order idempotency;
- partial fill exposure;
- daily/rolling loss calculations;
- consecutive-loss transitions;
- prohibited DCA/martingale/stop-widening invariants;
- CASH outcome; and
- restart reconstruction.

## Property/invariant tests

- available capital cannot be negative.
- reserved + deployed + pending capital cannot exceed reconciled equity/margin policy.
- increasing estimated cost cannot improve net edge.
- decreasing liquidity cannot increase permitted quantity.
- higher leverage ceiling cannot increase loss budget.
- duplicate events do not duplicate fills/PnL.
- state transitions not in the declared graph fail.
- a denied override cannot change arm state.

## Data tests

- L2 snapshot/delta continuity and resync;
- duplicates/out-of-order/late events;
- crossed/empty book;
- clock rollback and skew;
- schema migration compatibility;
- raw-hash/provenance verification;
- missing partition; and
- disk watermark/audit write failure.

## Execution fault injection

- submit timeout then eventual accept;
- duplicate acknowledgement;
- fill before acknowledgement;
- cancel/fill race;
- partial fill then disconnect;
- stale private feed;
- rate limit and maintenance;
- process crash before/after persistence boundary;
- two runtime instances competing for writer lease;
- venue position absent locally and vice versa; and
- restart with open PAPER position.

## Security tests

- secret scan and redaction fixtures;
- unauthorized/expired dashboard session;
- CSRF/replay command;
- tampered strategy/config/dependency artifact;
- malformed/log-injection venue payload;
- diagnostic bundle inspection; and
- backup restore integrity.

## Research tests

- feature causality/lookahead tests;
- label overlap, purge, and embargo;
- deterministic folds and seeds;
- sealed holdout access counting;
- negative-trial preservation;
- null/random baseline;
- ablation;
- parameter neighborhood;
- fee/spread/slippage/latency stress; and
- regime/instrument concentration.

## Phase acceptance gates

### Phase 0 — Documentation

- requirements traceable;
- open safety decisions identified;
- no contradictory numeric limits;
- links valid.

### Phase 1 — Market truth

- continuous capture soak target met;
- gap/staleness detection proven;
- deterministic canonical rebuild;
- raw/audit persistence resilient.

### Phase 2 — Replay/simulator

- replay deterministic;
- accounting exact to declared precision;
- impossible fills rejected;
- cost stress implemented;
- simulator calibrated enough for next phase.

### Phase 3 — Research

- preregistered hypothesis;
- chronological validation complete;
- leakage/null/ablation/stress pass;
- sealed holdout positive after costs;
- evidence reproducible.

### Phase 4 — PAPER readiness

- manual promotion recorded;
- risk and execution fault tests pass;
- restart/reconciliation drill passes;
- dashboard/audit/override controls pass;
- no LIVE credential/path exists.

### Phase 5 — PAPER operation

- predicted/realized execution error within tolerance;
- no unresolved reconciliation event;
- strategy remains inside evidence and risk bounds;
- operational soak includes restarts/disconnects;
- promotion remains manual.

## Release evidence

Every release stores:

- test report;
- dependency lock/SBOM;
- code/config hashes;
- known failures;
- migration/rollback plan; and
- approving operator identity.
