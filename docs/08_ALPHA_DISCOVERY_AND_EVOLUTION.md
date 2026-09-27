# 08 — Alpha Discovery and Evolution

## Objective

Create a script-only system that learns from new evidence without allowing runtime behavior to mutate itself.

“Self-learning” means a controlled experiment factory. It does not mean a running bot may rewrite parameters after losses.

## Two-loop design

### Runtime loop — frozen

- Reads approved champion manifest.
- Computes causal features.
- Produces decisions and uncertainty.
- Never trains, tunes, or edits its manifest.
- Records predictions, candidates, rejections, counterfactuals, and outcomes.

### Research loop — evolving

- Consumes immutable historical/PAPER evidence snapshots.
- Detects drift and error clusters.
- Generates bounded challenger hypotheses/parameters.
- Runs chronological validation and stress tests.
- Stores every result.
- Requests manual promotion; cannot deploy itself.

## Experiment cycle

1. **Observe**: collect decision/outcome errors and regime context.
2. **Diagnose**: identify falsifiable failure modes, not vague underperformance.
3. **Propose**: create challenger manifest inside a predeclared search space.
4. **Replay**: run deterministic evaluation and realistic execution simulation.
5. **Validate**: walk-forward, CPCV where appropriate, null tests, ablation, stress.
6. **Compare**: challenger vs CASH, baselines, and champion on matched timelines.
7. **Register**: save artifact and all negative evidence.
8. **Approve/reject**: human decision only.

## Candidate families

Bootstrap priority:

1. execution/cost filters and abstention quality;
2. exchange-native funding/carry observation;
3. simple cross-sectional directional breakout challenger;
4. simple mean-reversion challenger only where stationarity evidence exists.

Deferred:

- cross-venue funding/basis;
- on-chain and social event modules;
- wallet-copying;
- reinforcement learning;
- unbounded feature discovery.

## Allowed adaptive techniques

- bounded grid/random/Bayesian parameter search;
- calibration models for probability/expected move;
- drift detectors that reduce confidence or quarantine;
- rolling retraining on declared schedules;
- ensemble weighting selected offline; and
- streaming models in shadow research only.

## Forbidden adaptation

- changing stops or risk after entry;
- increasing size after losses;
- optimizing against the latest losing streak and deploying immediately;
- direct online learning in PAPER champion;
- automatic feature creation with unbounded search;
- automatic promotion;
- deleting failed trials; and
- using PAPER fills as labels without accounting for selection/censoring.

## Champion/challenger rules

- One active champion per alpha family.
- Any number of offline/shadow challengers within compute budget.
- Same-timeline comparison is mandatory.
- Challenger must improve the declared primary metric without materially worsening tail risk, calibration, cost sensitivity, or operational complexity.
- Strategy version changes even for a one-parameter change.
- Rollback means selecting a previous signed artifact, never editing history.

## Confidence

Confidence is not a subjective 0–1 score. It must be calibrated against realized outcomes on untouched data.

The system stores:

- predicted outcome distribution;
- expected net edge distribution;
- calibration bin and sample size;
- epistemic/data uncertainty;
- regime support; and
- expiry.

Leverage bands may reference calibrated lower confidence bounds, never raw model probability. Until calibration evidence supports thresholds, the leverage ceiling remains 1x.

## Drift response

Drift never triggers automatic aggressive adaptation.

| Drift | Response |
|---|---|
| Feature distribution shift | lower confidence / block unsupported regime |
| Calibration deterioration | reduce to CASH/quarantine |
| Cost-model error | reduce notional or block |
| Strategy expectancy decay | quarantine and research new version |
| Data-quality shift | block exposure |

## Candidate open-source components

| Candidate | Potential use | Constraint |
|---|---|---|
| [NautilusTrader](https://github.com/nautechsystems/nautilus_trader) | shared event-driven research/simulation/execution semantics | pin and audit; one order authority only |
| [Hummingbot](https://github.com/hummingbot/hummingbot) | connector/market-structure reference | no parallel execution engine |
| [Optuna](https://github.com/optuna/optuna) | bounded offline search | trial count and selection bias must be logged |
| [River](https://github.com/online-ml/river) | streaming model/drift research | shadow only until separately validated |
| [TensorTrade](https://github.com/tensortrade-org/tensortrade) | RL experimentation | deferred; simulator dependence is too dangerous now |

No repository is “the money-making part.” Economic edge must be independently demonstrated.
