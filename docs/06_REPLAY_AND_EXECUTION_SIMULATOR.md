# 06 — Replay and Execution Simulator

## Purpose

Replay proves determinism. The simulator estimates what orders could realistically have filled. These are separate responsibilities.

## Deterministic replay

Given identical:

- raw event partitions;
- ordering policy;
- schema/feature/strategy/risk/config versions;
- clock inputs; and
- seeds,

the replay must produce byte-equivalent decision and state-transition records.

No runtime call to wall clock, network, or unseeded randomness is allowed inside replayed domain logic.

## Fill model hierarchy

| Level | Model | Permitted use |
|---|---|---|
| L0 | next price / candle | exploratory sanity checks only; never promotion evidence |
| L1 | bid/ask crossing + fees | early directional screening |
| L2 | L2 depth walk + latency + partial fill | minimum strategy validation |
| L3 | queue-aware probabilistic passive fills calibrated from PAPER | maker/passive strategies |
| L4 | stress/adverse-selection scenarios | risk and promotion gate |

AUTOTRADE 7-style optimistic REST/last-price fills are not eligible evidence.

## Modeled costs

Every round trip decomposes:

```text
net_pnl = price_pnl
        - entry_fee - exit_fee
        - spread_cost
        - slippage_and_impact
        - latency_adverse_move
        - funding_cost
        - forced_unwind_cost
        - model_uncertainty_buffer
```

Benefits such as maker rebate or favorable funding are credited only when the exact simulated/observed event makes them realizable. Costs use conservative estimates when uncertain.

## Latency model

Model at minimum:

- market event to decision;
- decision to risk approval;
- order serialization/network;
- venue acknowledgement;
- cancel/replace latency; and
- private fill notification delay.

Use empirical distributions from PAPER telemetry. Validation runs median, p90, p99, and outage-tail scenarios.

## Market-order model

- consume visible depth level by level;
- reject impossible quantities;
- apply tick/step rounding before matching;
- model depth change during latency pessimistically;
- cap fill by available simulated liquidity; and
- record average price and unfilled remainder.

## Limit-order model

- never assume touch equals fill;
- estimate queue ahead from book state when possible;
- require traded volume through the level plus cancellation assumptions;
- model partial fill and cancel race;
- apply adverse-selection analysis after fill; and
- disallow maker claims without PAPER calibration.

## Funding model

Funding is discrete at settlement boundaries. The simulator must use the venue's historical settlement timestamps/rules and the position held at the relevant instant. Simple hourly pro-rating is not promotion-grade.

## Stress scenarios

At minimum:

- fees +25% and +50%;
- spread 2x/3x;
- slippage p90/p99;
- latency p90/p99 plus reconnect delay;
- partial fill and one-sided fill;
- sudden minimum/tick rule change;
- funding sign flip;
- stop gap-through;
- WebSocket disconnect during exposure;
- cancel acknowledgement lost;
- book gap/resync; and
- correlated two-position loss.

## Calibration

PAPER provides paired observations:

- predicted fill probability vs actual;
- predicted vs realized slippage;
- predicted vs realized latency;
- predicted vs charged fees/funding; and
- local state vs venue state.

Calibration error is tracked by instrument, order type, size/depth ratio, volatility regime, and time of day.

## Acceptance

Replay/simulator is accepted only when:

- determinism tests pass;
- accounting reconciles to the cent/tick according to venue precision;
- impossible fills are rejected;
- cost components are individually observable;
- PAPER calibration is within declared tolerances; and
- strategy conclusions remain stable under pessimistic scenarios.
