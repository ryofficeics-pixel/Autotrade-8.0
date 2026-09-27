# 15 — Venue Selection

## Decision status

No venue is selected yet. Gate.io, OKX, MEXC, and other CEX candidates must be measured under one rubric. Marketing claims and connector availability are insufficient.

## Mandatory disqualifiers

A venue is rejected if any is true:

- inaccessible or operationally unsuitable for the user;
- no usable PAPER/demo environment or safe local PAPER substitute;
- no stable authenticated/public API for required functions;
- cannot obtain sufficient trade/book/funding/instrument/account data;
- order/client-ID/reconciliation semantics are inadequate;
- withdrawal permission cannot be excluded from the trading key;
- instrument rules/fees are too ambiguous to model;
- minimum notional makes 300 USDT risk sizing impractical;
- recurrent connection/rate-limit behavior fails soak test; or
- terms/restrictions make intended use inappropriate.

## Weighted rubric

| Category | Weight | Evidence |
|---|---:|---|
| API/WebSocket correctness and sequence semantics | 20 | measured capture/reconnect test |
| PAPER/demo fidelity and private event coverage | 15 | order/fill/reconciliation test |
| Liquidity, spread, and depth for Top-N | 15 | recorded L2/trades across regimes |
| Fees/funding/minimum order economics | 15 | official schedule + observed charges |
| Order semantics/idempotency/reconciliation | 10 | adapter contract tests |
| Reliability/rate limits/maintenance behavior | 10 | multi-day soak |
| Security controls/API permission granularity | 5 | key settings and tests |
| Indonesian access and user operations | 5 | practical verification |
| Connector/SDK quality and maintenance | 3 | code/release review |
| Support/documentation clarity | 2 | documented issue resolution |

Passing score is not enough if a mandatory disqualifier is present.

## Benchmark procedure

1. Freeze the candidate list and date.
2. Record official API, fee, instrument, and demo documentation.
3. Implement read-only probes first.
4. Capture identical liquid instruments for at least a representative multi-day window.
5. Measure disconnects, gaps, staleness, skew, update rate, depth, and spread.
6. Test instrument-rule updates and rate-limit headers.
7. Run PAPER order lifecycle cases with minimum-safe quantities.
8. Compare predicted vs observed fee/fill/funding behavior.
9. Score the rubric with evidence links.
10. Record the venue decision in a new ADR/decision entry.

## Adapter contract

Selected venue adapter must normalize:

- canonical instrument identity;
- instrument rules/status;
- trades/L2/mark/index/funding;
- order types/time-in-force/reduce-only;
- client order identity;
- acknowledgements/rejects/cancels/fills;
- balances/positions/margin;
- rate limits/maintenance; and
- error categories and retry safety.

Venue-specific values never leak into strategy logic.

## Economic test for 300 USDT

For each candidate venue, verify:

- smallest executable position at intended stop distance;
- round-trip taker and maker economics;
- typical/p90 spread and depth impact;
- minimum fee/quantity effects;
- funding settlement behavior; and
- whether two-position and 0.5% risk rules remain feasible.

If minimum sizing breaks the risk budget, the instrument/venue is ineligible regardless of signal quality.

## Framework/connector note

NautilusTrader and Hummingbot may accelerate adapter work, but the final choice depends on observed venue behavior. A connector is not proof of correctness, and AUTOTRADE 8.0 will still enforce its own canonical contracts, risk governor, and single order authority.
