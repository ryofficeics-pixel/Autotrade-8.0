# 09 — Risk, Capital, and Leverage

## Risk objective

Risk policy constrains how wrong the system may be. It does not certify that a strategy has edge.

## Bootstrap limits

| Control | Limit |
|---|---:|
| Reference PAPER equity | 300 USDT |
| Maximum simultaneous positions | 2 |
| Independent position risk | 0.5% current equity |
| Portfolio open risk | 1.0% current equity |
| Correlated cluster risk | 0.5% current equity |
| Daily operational loss halt | 2.0% session-start equity |
| Catastrophic session stop | 10.0% session-start equity |
| Consecutive loss investigation | 3 |
| Consecutive loss halt | 5 |
| Project/account freeze | equity <= 50% of approved high-water reference |
| Initial leverage ceiling | 1x |
| Eligible future ceilings | 3x, then 5x after separate approval |

At 300 USDT, 0.5% is 1.50 USDT and 2% is 6.00 USDT. These values recalculate from current reconciled equity.

## Loss-budget sizing

For a proposed position:

```text
risk_budget_usd = equity * risk_fraction
unit_loss_usd   = abs(entry - protective_exit)
                + pessimistic_exit_slippage
                + round_trip_fees
                + funding_allowance
quantity        = floor_to_step(risk_budget_usd / unit_loss_usd)
```

Quantity is then capped by:

- available margin;
- leverage ceiling;
- instrument minimum/maximum;
- size-to-depth limit;
- concentration limit;
- portfolio/cluster risk; and
- liquidation-distance buffer.

If rounded quantity is below minimum notional, the trade is rejected. Risk limits are never rounded upward.

## Open risk

Open risk uses the worse of:

- stop-based loss including pessimistic costs;
- scenario loss from volatility/gap stress;
- liquidation/maintenance-margin stress; and
- model-estimated tail loss where independently validated.

Unprotected or unknown-stop exposure is treated as its full notional downside for gating purposes until resolved.

## Portfolio correlation

Two positions may open only when:

- combined open risk <= 1%;
- sector/base-asset/common-market concentration passes;
- recent downside correlation is below the configured independent threshold; and
- stress beta to BTC/market does not make them one effective bet.

If considered correlated, both positions share a combined 0.5% risk budget.

## Leverage policy

Leverage is a notional-to-equity ceiling, not a confidence reward.

### 1x

Default and only authorized ceiling until sufficient PAPER calibration exists.

### 3x eligibility

Requires manual approval plus:

- positive sealed holdout and PAPER expectancy after costs;
- calibrated confidence/lower-bound edge across relevant regimes;
- stable slippage and latency model;
- acceptable liquidation buffer under stress;
- no active drawdown/probation/degraded health; and
- unchanged per-position and portfolio risk budgets.

### 5x eligibility

Requires a separate later decision after 3x evidence. It is not automatically unlocked by high model confidence.

The maximum total gross notional across the portfolio is the active leverage ceiling times reconciled equity. Two positions do not each receive the full account leverage ceiling independently.

## Confidence-to-ceiling policy

Before calibration, all bands map to 1x. After approval, a policy may map the **lower confidence bound of net edge** to a maximum ceiling:

| Evidence state | Maximum ceiling |
|---|---:|
| insufficient, unsupported regime, or degraded calibration | 0x / CASH |
| qualified but ordinary | 1x |
| high calibrated support + 3x approval | up to 3x |
| exceptional calibrated support + 5x approval | up to 5x |

Actual sizing remains loss-budget-based. A 5x ceiling can still result in 0.4x actual exposure.

## Daily loss accounting

Daily loss includes:

- realized trading PnL;
- fees and funding;
- pessimistic mark-to-exit loss on open positions; and
- unresolved execution/reconciliation reserves.

The session boundary is a configured UTC boundary and cannot erase rolling 24-hour risk. Both session and rolling loss are monitored.

## Drawdown ladder

| Equity drawdown from high-water mark | Response |
|---|---|
| 2% | warning and diagnostics |
| 5% | reduce risk ceiling to 0.25%; leverage cap 1x |
| 10% | quarantine active strategy; manual review |
| 20% | freeze all strategy PAPER activity; root-cause review |
| 50% | project/account failure stop; no Resume override |

These are loss containment levels, not an allowed path to lose 50%.

## Prohibited behavior

- no DCA or averaging down;
- no martingale or size increase after loss;
- no grid inventory accumulation;
- no adding to winners unless a future separately validated pyramiding policy exists (bootstrap: forbidden);
- no stop widening;
- no hidden synthetic leverage across positions; and
- no operator override of quantity/order checks.
