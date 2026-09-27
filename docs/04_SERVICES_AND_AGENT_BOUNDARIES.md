# 04 — Services and Agent Boundaries

## Meaning of “agent”

An agent is a deterministic bounded service with a contract, permissions, and failure policy. It is not an LLM, a personality, or an independent trader.

The social-media HOUND/ECHO/TIDE/RAIL/SENTRY names are useful as a separation-of-concerns metaphor, but the claimed profit is unaudited marketing. AUTOTRADE 8.0 uses explicit engineering names.

## Service catalogue

| Service | Inputs | Outputs | Permission | Failure result |
|---|---|---|---|---|
| Market Collector | exchange WS/REST | raw events | network read | data degraded/stale |
| Data Sentry | raw events, clocks, sequences | health gates | block entries | fail closed |
| Universe Selector | canonical market stats/rules | eligible Top-N | recommend | keep last valid universe briefly, then block |
| Feature Engine | causal normalized events | versioned features | compute only | strategy unavailable |
| Alpha Evaluator | feature snapshot + frozen manifest | opportunity distribution | recommend | CASH |
| Cost Model | book state, fees, latency distributions | cost distribution | compute only | unknown cost => block |
| Allocator | comparable cleared opportunities | CASH/selected intent | recommend | CASH |
| Risk Sentry | intent, equity, exposure, health | ALLOW/BLOCK/HALT | gate only | HALT/BLOCK |
| Order Authority | allowed intent | order state transitions | PAPER order credential | block and reconcile |
| Venue Adapter | canonical order request | venue messages | protocol translation | degraded/halt |
| Reconciler | venue/local state | matched/mismatch state | block/halt | HALT |
| Evidence Recorder | every decision/event | immutable records | append only | halt if critical audit lost |
| Experiment Runner | frozen datasets/search plan | challenger artifacts | offline only | experiment failed |
| Validator | challenger + sealed evidence | validation report | offline only | reject |
| Promotion Registry | report + human decision | signed lifecycle event | manual transition | remain unchanged |
| Dashboard Backend | projections + commands | UI/API | no direct order path | UI degraded only |

## Permission matrix

| Capability | Collector | Research | Strategy | Risk | Execution | Dashboard | Operator |
|---|---:|---:|---:|---:|---:|---:|---:|
| Read public market data | Yes | Via store | Via canonical stream | Yes | Yes | Projection | Yes |
| Read account state | No | Sanitized only | No | Canonical only | Yes | Projection | Yes |
| Read secrets | No | No | No | No | Runtime injection only | No | No plaintext |
| Generate candidate | No | Yes | Frozen evaluation | No | No | No | Request only |
| Change strategy | No | Challenger only | No | No | No | No | Manual promotion |
| Change risk limit | No | No | No | Config load only | No | No | Signed config workflow |
| Submit PAPER order | No | No | No | No | Yes | No | No direct access |
| Halt | Data fault | No | Request | Yes | Yes | Command request | Yes |
| Resume | No | No | No | Validate request | Re-arm only | Request | Authenticated |

## No bypass rule

The order authority accepts an intent only if it carries:

- decision ID;
- strategy and parameter versions;
- data watermark;
- risk approval ID;
- sizing result;
- expiry;
- idempotency key; and
- current arm epoch.

Missing or stale fields reject the intent. Dashboard, scripts, tests, and operator tools may not submit raw venue orders.

## Failure isolation

- Dashboard failure does not stop data collection or position protection.
- Research failure cannot affect PAPER runtime.
- Strategy exception returns CASH and records an error.
- Data or reconciliation failure blocks exposure regardless of strategy confidence.
- Audit persistence failure blocks new orders because unrecorded trading is unacceptable.

## Agent communication

Events are typed, versioned, and immutable. Commands are distinct from facts:

- Fact: `MarketDataStale`, `OrderAccepted`, `PositionObserved`.
- Decision: `OpportunityProposed`, `RiskBlocked`.
- Command: `SubmitOrder`, `CancelOrder`, `ArmPaper`.

A command never masquerades as an observed fact. Every consumer is idempotent.
