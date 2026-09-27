# 12 — Dashboard, Audit, and Override

## Role

The dashboard is an observable control surface, not the source of truth. It reads projections and submits authenticated commands to the control plane.

## Required pages

### Overview

- system state and arm epoch;
- equity, available margin, realized/unrealized PnL;
- daily/rolling loss and drawdown ladder;
- open positions/orders and total/cluster risk;
- selected venue and connection/account health;
- active strategy/config/data versions;
- last reconciliation and audit persistence status.

### Market and universe

- eligible Top-N and rejection reasons;
- spread/depth/volume/staleness;
- data gaps and book status;
- current regime/support status.

### Decisions

- every `CASH`, `BLOCK`, `ENTER`, `EXIT`, `HOLD`;
- expected gross edge and full cost breakdown;
- confidence/calibration/support;
- SENTRY gates and first/all rejection reasons;
- counterfactual outcome after expiry.

### Orders and positions

- complete order state timeline;
- requested vs filled quantity/price;
- predicted vs realized slippage/latency/fee;
- reconciliation status;
- protective exit state.

### Research/evidence

- champion/challenger lifecycle;
- experiment counts and negative results;
- validation/test/holdout summaries;
- drift/calibration alerts;
- manual promotion history.

### Audit and incidents

- errors grouped by fingerprint;
- halt timeline;
- configuration/deployment changes;
- resume attempts and outcomes;
- diagnostic bundles.

## Health separation

Do not show one misleading green/red light. Display independently:

- market data;
- account/private feed;
- strategy;
- risk;
- execution;
- reconciliation;
- storage/audit; and
- dashboard itself.

Trading readiness is the strict AND of required health states.

## `AUDIT_ERROR`

The button creates an immutable diagnostic bundle containing:

- incident ID and timestamps;
- redacted logs around the event;
- health/state transitions;
- active code/config/strategy hashes;
- data sequence/gap summary;
- recent decisions/orders/fills/reconciliation;
- resource usage; and
- reproduction/replay pointers.

It does not call an LLM, change configuration, restart automatically, cancel orders, or resume trading.

## `RESUME_TRADING`

### Eligible halt reasons

- daily 2% operational loss halt;
- five-consecutive-loss halt;
- manual operator halt; and
- resolved soft operational error explicitly marked resumable.

### Never overridable

- 10% catastrophic session loss;
- 50% project/account stop;
- stale/corrupt/missing required data;
- unresolved order/position/balance mismatch;
- unhedged/unknown exposure;
- credential/config/manifest integrity failure;
- unavailable audit persistence;
- quarantined/retired strategy; and
- failed risk calculation.

### Resume workflow

1. Authenticate operator again.
2. Show halt cause, current equity/risk, open exposure, and failed gates.
3. Require typed reason and explicit acknowledgement.
4. Generate an Audit Error bundle.
5. Re-run health, reconciliation, risk, and manifest checks.
6. Create immutable `ResumeRequested` event.
7. Risk governor returns `ResumeDenied` or starts `PROBATION`.

### Probation

For performance-halt override:

- minimum one-hour cooling period;
- maximum one open position;
- 0.25% risk per position;
- 1x leverage ceiling;
- no new entry while any position is open;
- lasts at least four healthy hours and until the next session reset;
- any loss, data/execution fault, or reconciliation warning returns to HALTED.

Normal limits return only after factual probation completion; the button cannot shorten it.

## Command audit fields

- command ID/type;
- operator/session identity;
- client and server timestamp;
- arm epoch;
- reason text;
- precondition results;
- before/after state;
- code/config/strategy hashes; and
- result/denial reason.

## UX prohibitions

- no “force trade” button;
- no direct quantity/leverage edit on trade screen;
- no hidden auto-refresh that resubmits commands;
- no PnL celebration/gamification;
- no reset-loss-counter action; and
- no display that implies model confidence equals probability of profit unless calibrated and labeled.
