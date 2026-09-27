# 20 — Observability and Metrics

## Principle

Operational health, execution quality, and economic performance are separate. A profitable day can be operationally broken; a stable process can run a losing strategy.

## Operational metrics

- process heartbeat/restart count;
- WebSocket connected time and reconnect count;
- event age, sequence gaps, duplicates, late events;
- clock skew and processing lag;
- API latency/error/rate-limit usage;
- queue depth/backpressure;
- disk/memory/CPU and audit write latency;
- last successful backup/restore verification.

## Execution metrics

- order submit-to-ack latency;
- decision-to-submit latency;
- cancel latency and cancel/fill races;
- fill ratio and partial-fill duration;
- predicted vs realized slippage/fees/funding;
- unknown-order duration;
- reconciliation mismatch count/duration;
- rejected order reasons;
- actual size vs approved size.

## Risk metrics

- current position/portfolio/cluster open risk;
- gross/net exposure and leverage;
- daily and rolling 24-hour loss;
- drawdown from high-water mark;
- consecutive losses;
- risk gate rejection counts;
- HALT/Resume/Probation state and duration;
- distance to catastrophic/project stops.

## Strategy/economic metrics

- gross and net PnL;
- cost decomposition and cost/gross-edge ratio;
- expectancy and confidence interval;
- profit factor, payoff ratio, win rate;
- drawdown, tail loss, exposure time;
- performance by strategy/instrument/regime/confidence bin;
- CASH rate and opportunity/rejection counts;
- counterfactual vs executed outcome;
- predicted vs realized edge/calibration;
- champion vs challenger matched-timeline results.

## Alerts

| Severity | Examples | Action |
|---|---|---|
| Critical | unknown position/order, config tamper, audit failure, catastrophic loss | immediate hard halt + operator alert |
| High | data/private-feed stale, reconciliation mismatch, daily/consecutive halt | halt new exposure + alert |
| Medium | calibration drift, elevated slippage/latency, disk warning | reduce/block affected scope + investigate |
| Low | research job failure, dashboard view error | record and schedule repair |

Alerts must be deduplicated, stateful, and include recovery notification. Repeated alerts cannot be silently suppressed without an audit event.

## Logs and traces

- structured JSON/event logs;
- decision/order/incident correlation IDs;
- no secrets or full credential-bearing requests;
- monotonic and UTC timestamps;
- stable reason codes;
- sampling forbidden for financial/audit events;
- debug sampling allowed only for high-volume non-authoritative diagnostics.

## Service-level objectives for bootstrap

Exact thresholds are set after measured baselines, but the SLO classes are fixed:

- market/account feed freshness;
- gap detection and resync time;
- order acknowledgement/reconciliation time;
- audit persistence availability;
- restart-to-reconciled-unarmed time;
- diagnostic bundle generation; and
- backup/restore success.

No availability SLO permits trading with stale or uncertain truth.

## Reporting cadence

- real-time: health, exposure, orders, hard risk;
- 10-minute: audit/status summary;
- daily: execution calibration, PnL/cost/risk, incidents;
- weekly: strategy evidence/drift, challenger tournament, operations;
- monthly/30-day: aspiration comparison, but with risk and evidence context.

The 30%/30-day aspiration is displayed beside drawdown, exposure, cost, and uncertainty—never as a progress bar that pressures trading.
