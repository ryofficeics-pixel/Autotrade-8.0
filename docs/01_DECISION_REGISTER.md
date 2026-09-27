# 01 — Decision Register

## Accepted decisions

| ID | Decision | Rationale | Status |
|---|---|---|---|
| D-001 | Start a clean repository foundation; retain AUTOTRADE 7/early 8 evidence read-only | Failure evidence must not be erased or silently reused | Accepted |
| D-002 | Trade USDT perpetuals on one selected CEX | Small capital and operational simplicity | Accepted |
| D-003 | Gate.io is not mandatory; Gate.io, OKX, MEXC, and other candidates must pass the same rubric | Avoid venue loyalty and hidden assumptions | Accepted |
| D-004 | Build data, replay, and simulator before alpha/runtime | AUTOTRADE 7 lacked reliable market/execution truth | Accepted |
| D-005 | PAPER only; no LIVE state in the initial lifecycle | Real capital is not authorized | Accepted |
| D-006 | Dynamic Top-N universe, bootstrap maximum five instruments | Allows opportunity selection without uncontrolled breadth | Accepted |
| D-007 | Maximum two open positions | User requirement; portfolio correlation limits still apply | Accepted |
| D-008 | No trade quota; multiple trades/day are permitted | Frequency must emerge from qualified edge | Accepted |
| D-009 | Maximum position loss budget 0.5% equity | User delegated exact value; protects small capital | Accepted |
| D-010 | Daily operational halt at 2% | User accepted replacement of 10% operating limit | Accepted |
| D-011 | Investigate after 3 consecutive losses; halt after 5 | Earlier than proposed 10-loss boundary | Accepted |
| D-012 | 10% session loss is catastrophic account-stop; no override | Prevent override loops from consuming the account | Accepted |
| D-013 | Project/account freeze if equity reaches 50% of high-water reference | User stop criterion; strategy gates act far earlier | Accepted |
| D-014 | Leverage starts at 1x; 3x and 5x are confidence- and evidence-gated ceilings | Leverage is margin efficiency, not risk allowance | Accepted |
| D-015 | DCA, martingale, grid averaging, pyramiding, and stop widening are forbidden | Prevent disguised risk escalation | Accepted |
| D-016 | Runtime/research contains no LLM dependency | User requires deterministic scripts | Accepted |
| D-017 | Learning/evolution is offline challenger creation only | Prevent uncontrolled self-modifying production code | Accepted |
| D-018 | Promotion is manual | User requirement | Accepted |
| D-019 | Dashboard retains useful AUTOTRADE 7 concepts and adds Audit Error and Resume Trading | Preserve observability without preserving losing alpha | Accepted |
| D-020 | Resume Trading is allowed only for reviewable performance/manual halts | Integrity failures cannot be overridden | Accepted |
| D-021 | Initial deployment is Windows laptop; VPS after stable operation | Cost control | Accepted |
| D-022 | Recurring infrastructure budget ceiling Rp150,000/month | User requirement | Accepted |
| D-023 | Initial data sources are exchange-native trades, L2, funding, rules, account/order events, and health | Avoid premature data complexity | Accepted |
| D-024 | Cross-venue strategies are deferred | 300 USDT is too small for fragmented collateral and hedge risk | Accepted |
| D-025 | +30% in 30 days is reported as aspiration only | It cannot drive risk or trading behavior | Accepted |

## Derived safety decisions

| ID | Decision | Status |
|---|---|---|
| D-026 | Correlated positions with absolute rolling correlation above the configured threshold share one 0.5% risk budget | Accepted |
| D-027 | Total portfolio open risk is capped at 1.0% equity | Accepted |
| D-028 | All risk calculations include fees and pessimistic exit slippage | Accepted |
| D-029 | Confidence must be calibrated out-of-sample; raw model score cannot select leverage | Accepted |
| D-030 | Hard failures default to HALTED and require factual recovery, not operator override | Accepted |
| D-031 | Paper execution may start only after Phase 0–2 acceptance and manual arming | Accepted |
| D-032 | A permanent sidecar shadow prediction stream runs during PAPER for counterfactual audit | Accepted |

## Open decisions

These do not block documentation, but they block the relevant implementation phase.

| ID | Question | Blocking phase |
|---|---|---|
| O-001 | Which CEX wins the measured venue rubric? | Venue adapter implementation |
| O-002 | Exact Top-N refresh cadence and liquidity thresholds after data collection | Universe service |
| O-003 | Exact calibrated confidence boundaries for 1x/3x/5x | Leverage above 1x |
| O-004 | Minimum research sample per alpha family after opportunity-rate observation | Strategy promotion |
| O-005 | Laptop retention capacity and raw-data compression format benchmark | Data implementation |
| O-006 | VPS provider and payment route within Rp150,000/month | VPS migration |

## Change rule

Changing an accepted risk or safety decision requires:

1. a new decision ID;
2. rationale and evidence;
3. impact analysis across the traceability matrix;
4. manual approval; and
5. a new configuration version.

Old decisions are superseded, never erased.
