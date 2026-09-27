# 19 — Configuration and Event Contracts

## Configuration principles

- Configuration is typed, versioned, validated, immutable per arm epoch, and hash-addressed.
- Unknown fields fail validation in safety-critical sections.
- Defaults are explicit; no environment-dependent silent default.
- Secrets are references/injected values, never configuration content.
- Runtime cannot change risk/strategy configuration; changes require unarm, validate, new version, and re-arm.

## Configuration domains

```yaml
system:
  mode: PAPER
  timezone: UTC
  max_positions: 2

venue:
  adapter: TO_BE_SELECTED
  account_environment: PAPER
  instruments_max: 5

risk:
  position_risk_fraction: 0.005
  portfolio_risk_fraction: 0.010
  correlated_cluster_risk_fraction: 0.005
  daily_halt_fraction: 0.020
  catastrophic_session_fraction: 0.100
  consecutive_loss_investigate: 3
  consecutive_loss_halt: 5
  initial_leverage_ceiling: 1.0

runtime:
  live_enabled: false
  llm_enabled: false
  online_learning_enabled: false
```

This is a contract illustration, not an implementation file. `live_enabled` must remain false and ideally be absent from runtime code rather than treated as a switch.

## Canonical event header

```yaml
event_id: uuid-or-deterministic-id
event_type: MarketTrade|BookDelta|DecisionCreated|RiskBlocked|OrderAccepted|...
schema_version: 1
event_time_ns: 0
receive_time_ns: 0
monotonic_time_ns: 0
source: venue/component
correlation_id: decision-or-incident-id
causation_id: prior-event-id
arm_epoch: null-or-runtime-epoch
payload_hash: sha256
payload: {}
```

## Decision contract

```yaml
decision_id: uuid
action: CASH|ENTER|EXIT|HOLD
strategy_id: family/name
strategy_version: immutable-version
parameter_version: immutable-version
feature_version: immutable-version
data_watermark: exact-source-boundary
created_at: event-time
valid_until: event-time
instrument: canonical-id
side: LONG|SHORT|null
expected_gross_edge_bps: distribution-summary
expected_cost_bps: distribution-summary
expected_net_edge_bps: distribution-summary
confidence_calibration_id: id-or-null
support_state: SUPPORTED|WEAK|UNSUPPORTED
reasons: []
```

## Risk approval contract

```yaml
risk_approval_id: uuid
decision_id: uuid
result: ALLOW|BLOCK|HALT
equity_snapshot: decimal
risk_budget_usd: decimal
quantity: decimal
notional_usd: decimal
actual_leverage: decimal
leverage_ceiling: decimal
position_open_risk_usd: decimal
portfolio_open_risk_usd: decimal
cluster_id: string
gates: []
expires_at: event-time
config_hash: sha256
```

## Order intent contract

```yaml
intent_id: uuid
decision_id: uuid
risk_approval_id: uuid
client_order_id: deterministic-id
instrument: canonical-id
side: BUY|SELL
quantity: decimal
order_type: declared-enum
limit_price: decimal-or-null
reduce_only: boolean
time_in_force: declared-enum
expires_at: event-time
arm_epoch: uuid
```

## Reason codes

Reason codes are stable machine-readable enums plus human context. Minimum families:

- `DATA_*`
- `UNIVERSE_*`
- `ALPHA_*`
- `COST_*`
- `RISK_*`
- `CAPITAL_*`
- `VENUE_*`
- `EXECUTION_*`
- `RECONCILIATION_*`
- `SECURITY_*`
- `MANUAL_*`

Do not encode dynamic values into the enum; store them in structured context.

## Schema evolution

- additive optional fields require compatible version policy;
- changing meaning/unit/requiredness requires a new schema version;
- readers reject unsupported safety-critical versions;
- migration is deterministic and tested against golden fixtures; and
- raw payloads remain untouched.
