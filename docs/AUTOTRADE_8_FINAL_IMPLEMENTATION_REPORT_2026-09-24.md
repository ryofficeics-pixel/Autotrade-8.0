# AUTOTRADE 8.0 implementation and evidence report

Date: 2026-09-24 UTC. Status: **PARTIAL IMPLEMENTATION; SHADOW ONLY; NO QUALIFIED ALPHA**.
This document does not assert that the requested final system or its profitability is complete.

## 1. Executive Summary

AUTOTRADE 7's existing PAPER strategy remains halted. A standalone, read-only
AUTOTRADE 8 economic layer, funding comparison scanner, forward public capture,
causal zone feature, on-chain event interface, and safety tests were added.
No new family is promoted; no new strategy can place an order. **Best qualified
capital use: CASH.** Completing the full 110-point specification requires forward
data, validated execution economics, independently positive OOS and holdout
results, and integration with the Nautilus portfolio under a separate gate.

## 2. AUTOTRADE 7 baseline

The 2026-09-23 fixed PAPER ledger had 427 normal closes, -12.17927339 USDT
gross price PnL, 12.66494518 USDT fees, -24.84421854 USDT net PnL, and
PF 0.5062. The last **observed**, not current, equity in that audit was
279.91343380 USDT. Both chronological halves lost. The 2026-09-24 cross-sectional
study found modeled +4.6393 bps full-sample net expectancy for momentum-only,
but test (-28.7934 bps), holdout (-111.7509 bps), and stress (-7.6831 bps)
failed. Its breakout and combined variants were gross-negative. PAPER eligible: 0.

## 3. Screenshot/reference analysis

The AUTOTRADE 8 repository initially contained nine Threads screenshots and
no engine code. The OmniQuant images show a **REPLAY** graphic, $31.50 to $9
then a claimed $27,678.90, HOUND/ECHO/TIDE/RAIL/SENTRY labels, a 0.92
"confidence", 90%+ wallets and an asserted route under 2% slippage. None
provides fills, costs, a ledger, audit trail or independent sample. A separate
TensorTrade post advertises RL, and a stock-indicator post shows Stochastic,
Vol S/R Zones V2 and volume. Neither proves crypto alpha.

## 4. Ideas accepted

Independent feeds, executable-depth checks, explicit final risk gates, abstention,
funding interval normalization, deterministic lifecycle, RL as optional future
allocation research, confirmed volume zones as a testable feature, and separate
research/production authority.

## 5. Ideas rejected

Extreme screenshot PnL, 0.92 as a probability, wallet win rate as a buy rule,
2% slippage as acceptable arbitrage friction, indicator stacking as evidence,
an RL policy as an alpha engine, and treating multiple named agents as proof.

## 6. Architecture

Legacy source and ledger stay intact. `autotrade8/` contains pure-Python,
read-only economic primitives and a structural scanner. It does not import
Nautilus, `autotrade.paper`, exchange order adapters, or dashboard controls.
The existing `autotrade/research.py` and `autotrade/wide_crypto_*` keep the
immutable XAU and wide-crypto studies. A future integration needs a verified
normalizer, evidence-qualified promotion, Nautilus-owned durable reservations,
and measured multi-leg PAPER execution. Those links are **not implemented**.

## 7. Opportunity model

One schema covers family/version, validity, two legs, gross/cost/net bps,
capital, horizon, delta, exposure, risk, lifecycle, data quality, evidence and
ordered SENTRY gates. `CostBreakdown` uses bps of **one matched leg's notional**;
fees and spread for both legs are added. NaN, infinity, negative component
costs, invalid capital and impossible quality measures fail construction.

## 8. Cost model

Entry and exit fees, both spreads, four modeled slippage transactions and
emergency unwind buffer are included in the initial scanner. Impact, latency,
funding reversal, borrow, collateral opportunity, partial fills and realized
exit liquidity lack measured inputs. These unknowns are **blockers**, not zeros
that license execution. Static fees/slippage in scanner configuration are
research assumptions, not observed per-venue execution calibration.

## 9. Capital allocator

The supplied Phase 1 prototype was incorporated with a `CASH` default,
score components, one-bundle limit, reservation lifecycle, and switching
hysteresis. It ignores opportunities exceeding available capital. Its ledger
is **in-memory research state only**. It cannot represent the Nautilus account
after restart or venue balance fragmentation; it must not be connected to PAPER
until durable, reconciled reservation ownership is built.

## 10. SENTRY

Checks quality, skew, liquidity, lifecycle/evidence, positive net edge,
cost/edge ratio, risk halt, minimum absolute PnL, capital, venue health, delta,
leg minimum and expiry. First binding reason is explicit. New opportunities
are `OBSERVING`, evidence score 0, execution quality 0, and BLOCKED.

## 11. Funding Carry

An initial spot-long/perp-short shadow projection uses at least six **settled**
funding prints, compares 3- and 6-print means, reads the actual settlement
schedule, and sums two-leg costs. It does not extrapolate a single current
funding print into annual profit. Forecast stability and realized convergence
have not been demonstrated. Current evidence: **INSUFFICIENT_EVIDENCE**.

## 12. Cross-Exchange Funding

Compares conservatively estimated settled rates with each venue's verified
funding interval and next settlement count. It refuses missing timestamps,
stale events, sparse best-level depth and undersized accounts. Currently no
usable synchronized real snapshot was collected here; **INSUFFICIENT_EVIDENCE**.

## 13. Cross-Exchange Basis

Current BBO divergence is deliberately **not** assigned an expected convergence
return. The scanner records `CONVERGENCE_NOT_VALIDATED` until rolling, forward
executable BBO history and a sealed OOS convergence model exist. No strategy
claim or basis order path exists.

## 14. Cross-Sectional Breakout

AUTOTRADE 7 already implemented dynamic universe, causal relative ranks,
breakout, execution profiles, CPCV and holdout on an immutable 90-day Gate
dataset. Its combined breakout research lost before modeled costs. Reuse the
failure and dataset; do not reset the holdout by renaming it V1. A new
independent directional family is **not** promotion-eligible.

## 15. Volume Zone Context

`autotrade8.zones` confirms high-volume swing zones only when the right-hand
bars have closed, with distinct zone creation and confirmation timestamps.
It is an isolated feature, not wired into directional entries. Same-dataset
ablation and incremental OOS value: **NOT TESTED**. Stochastic: **NOT ADDED**.

## 16. On-chain Event architecture

HOUND event/provenance, ECHO wallet sample, TIDE attention, RAIL slippage/exit
depth and GUARD contract/liquidity safety are explicit fields. Missing social
data is `SOCIAL_DATA_UNAVAILABLE`; missing safety is
`CONTRACT_SAFETY_UNVERIFIED`. The event decision always remains
`SHADOW_BLOCKED` until independent evidence and full safety checks exist.
There is no feed, contract analyzer, or exchange route yet.

## 17. TensorTrade/RL decision

No RL dependency added. TensorTrade's documented compatibility set includes
NumPy <2 and additional TensorFlow/Ray requirements; adding them to this
Nautilus runtime before deterministic alpha would consume effort without an
identified reward signal. `META_ALLOCATOR_RL_V1`: **NOT_STARTED**.

## 18. Data

`autotrade8.public_capture` writes raw, append-only, public Gate/Binance
responses with local wall and monotonic receive clocks and response SHA-256.
Unverified exchange event times stay null. It collects no credentials and
cannot submit orders. A single attempted forward capture at
2026-09-24T12:26:09Z recorded **8/8 endpoints UNAVAILABLE** because direct
market-API access timed out in this environment. No price, BBO, funding, or
synthetic book was substituted. A read-only shadow CLI processed this actual
failed capture and reported `PUBLIC_FEEDS_UNAVAILABLE`, 0 normalized
opportunities, 0 qualified families and CASH, with account equity unknown.
The raw capture is local untracked research data and has not been frozen or
verified as an immutable dataset.

## 19. Execution

No new execution path. Legacy Nautilus PAPER simulator and its failed-strategy
halt remain authoritative. Four-leg fill realism, venue balances, min lots,
latency and reconciliation for structural strategies are outstanding.

## 20. Hedge safety

The Phase 1 research state machine includes PROPOSED, RESERVED, SUBMITTING,
PARTIALLY_HEDGED, HEDGED, ACTIVE, UNWINDING, CLOSED, EMERGENCY and FAILED.
Unexpected one-leg delta triggers an immediate `RETRY_HEDGE` instruction in
the pure model, with slippage checks and timeouts. No Nautilus handler executes
that instruction; **do not describe multi-leg PAPER execution as safe yet**.

## 21. Risk

Global legacy halt remains sticky; leverage is 1x; no DCA, martingale,
automatic promotion or LIVE route was added. The new config marks every
engine `execution_enabled = false`. Missing prices, event clocks, cost inputs,
model evidence or contract safety lead to no trade.

## 22. Walk-forward

Legacy cross-sectional and XAU research have chronological folds documented
in their own reports. No new funding/basis fold exists because no sufficiently
long synchronized dataset exists. **NOT RUN** for new families.

## 23. CPCV

Legacy wide-crypto CPCV exists. No funding/basis/event CPCV: **NOT RUN**.

## 24. Holdout

Legacy cross-sectional holdout failed; no new family has a sealed holdout.
**INSUFFICIENT_EVIDENCE**.

## 25. Overfitting audit

Legacy wide-crypto audit documents the failure. New families have no
independent samples, so PBO/DSR/reality-check numbers would be fabricated.

## 26. Ablation

Momentum/breakout legacy variants exist. Incremental volume-zone, Stochastic,
wallet, social, RAIL and GUARD ablations: **NOT RUN**.

## 27. Tournament

| Family | Gross | Net | PF | Holdout | Stress | Decision |
|---|---:|---:|---:|---|---|---|
| Funding Carry | N/A | N/A | N/A | None | None | OBSERVING |
| Cross-Exchange Funding | N/A | N/A | N/A | None | None | OBSERVING |
| Cross-Exchange Basis | N/A | N/A | N/A | None | None | BLOCKED |
| CS Momentum Only legacy | +23.2581 bps | +4.6393 bps model | 1.0147 | -111.7509 bps | -7.6831 bps | FAILED |
| CTA Breakout Only legacy | -24.5316 bps | Negative | N/A | Failed | N/A | FAILED |
| CS Breakout combined legacy | -53.6559 bps | Negative | N/A | Failed | N/A | FAILED |
| Volume Zone variant | N/A | N/A | N/A | None | None | FEATURE ONLY |
| On-chain Event | N/A | N/A | N/A | None | None | SHADOW BLOCKED |
| REST Momentum legacy | -12.1793 USDT | -24.8442 USDT | 0.5062 | Negative | Negative | RETIRED |
| KAMA Raw legacy | +0.1584 USDT | -16.5412 USDT | 0.0108 | Negative | Negative | QUARANTINED |

Figures are from different timelines/units and **must not be compared by rank**.
No current family qualifies. KAMA filtered: one negative accepted close, observing.
Entry V3: zero accepted candidates, non-executable. XAU fair value and combined:
no promotion-quality edge.

## 28. PAPER eligibility

Zero. Positive gross/net, independent samples, stable parameter neighborhood,
positive validation/test/sealed holdout, stress, credible cost/fill model,
manual approval and durable Nautilus reconciliation are all required first.

## 29. Dashboard

Existing operations console and read-only Research tournament remain. No
AUTOTRADE 8 opportunity/capital/hedge board was connected. No claim of a
rendered or Playwright-tested new board is made. A new board before validated
feed normalization would misleadingly show fictitious opportunities.

## 30. Tests

Eleven new dependency-free safety tests pass, covering carry accounting,
different settlement intervals, stale/skewed/missing data, min depth, cash
reservation, stale SENTRY reevaluation at allocation/commit, unpromoted alpha,
immediate one-leg hedge response, unavailable-feed abstention, causal zone
visibility and event safety. `compileall` and `git diff --check` pass.
The inherited suite, Ruff, mypy, pip check and Playwright could not run here:
pytest, NautilusTrader, Ruff, mypy and Playwright are absent; package registry
and market endpoints timed out. Do not attribute previous Windows results to
this checkout.

## 31. Failure injection

Tests exercise stale/future event, missing exchange timestamp, venue skew,
missing depth/history, duplicate capital reservation, one-leg fill and absent
on-chain safety. Restart while hedged, corrupted checkpoint, live partial-fill
reconciliation, delayed fills, and funding reversal need a PAPER harness.

## 32. Bugs found

The provided Phase 1 package accepted NaN/non-finite opportunities, allowed
negative cost components, ranked opportunities larger than available capital,
and waited for a timeout before reacting to a first unhedged fill. Event-time
freshness was not checked. Original Phase 1 tests described the delayed response
as expected; that expectation was incorrect for the stated hedge policy.

## 33. Bugs fixed

Strict numeric and lifecycle validation, cash-capital filtering, event-time
freshness, immediate hedge instruction, and focused independent regression
tests were added. These fixes do not provide an actual two-venue executor.

## 34. Remaining blockers

1. Real public-market capture must work on the target Windows host/VPS and
   synchronize validated venue event timestamps, order-book depth and fees.
2. Funding/basis require complete interval-aware settlement data, executable
   VWAP, exit liquidity, basis convergence and forward PAPER calibration.
3. No new strategy has positive independent OOS and sealed-holdout evidence.
4. Nautilus-owned durable capital reservations and multi-leg reconciliation
   are missing; the new package has no PAPER route.
5. On-chain safety and licensed social feeds are unavailable.
6. The new dashboard and full Python/browser validation are not complete.

## 35. Changed files

Added `autotrade8/{opportunity,costs,allocator,sentry,funding,hedge,scanner,
zones,event,public_capture,shadow_cli}.py`, config, and `tests/test_autotrade8_stdlib.py`.
Updated README, architecture and risk documentation. The exact committed file
list is `git show --stat` for the delivery SHA.

## 36. Commits

Legacy AUTOTRADE 7 baseline: `4cecafcb78e525d73b34b3666014499155b79364`.
Screenshot-only AUTOTRADE 8 baseline: `750f6b26c4c82f564accd1919a1ccaba990cacb0`.
Implementation SHA is supplied with delivery; report cannot include its own
final hash without changing that hash.

## 37. Runtime state

This environment has no running AUTOTRADE 7 process or current portfolio
checkpoint. **Actual current equity and account state: UNKNOWN.** Last audited
PAPER state (not a new measurement): HALTED, flat, unarmed, 279.91343380 USDT,
`STRATEGY_EVIDENCE_FAILED`. New code mode: SHADOW. PAPER active: NONE.
LIVE: DISABLED.

## 38. Next experiment

Run forward public capture on the user's connected Windows host, validate
exchange-event timestamps and contract multipliers, freeze 30+ days of
cross-venue funding/BBO with explicit hashes, then preregister one carry
hypothesis and test net economics across chronological folds. If edge fails
or minimum absolute PnL is immaterial for ~300 USDT capital, retire it and
keep 100% CASH.

### Primary references

- [Gate futures API](https://www.gate.com/docs/developers/apiv4/en/futures/)
- [Hummingbot funding arbitrage example](https://github.com/hummingbot/hummingbot/blob/master/scripts/v2_funding_rate_arb.py)
- [TensorTrade compatibility](https://github.com/tensortrade-org/tensortrade/blob/master/COMPATIBILITY.md)
- [Epsilon quantitative research](https://github.com/Epsilon-Fund/Epsilon-Quant-Research)
