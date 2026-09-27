# Contributing

## Workflow

1. Select requirement and decision IDs from `docs/TRACEABILITY_MATRIX.md`.
2. Confirm the relevant architecture/contract document is complete.
3. Make the smallest reversible change.
4. Add unit, contract, failure, and replay tests as applicable.
5. Run formatting, static checks, tests, secret scan, and documentation-link checks.
6. Record known limitations and migration/rollback behavior.

## Pull request content

- Purpose and scope.
- Requirements/decisions implemented.
- Files and state transitions changed.
- Test evidence.
- Security, economic, and operational impact.
- Data/schema/config migration.
- Rollback instructions.

## Prohibited contributions

- LIVE trading path or credential.
- Profit guarantee or fabricated performance claim.
- Unregistered strategy/parameter change.
- Risk-limit bypass.
- Forced trade/return quota.
- DCA, martingale, grid averaging, pyramiding, or stop widening.
- Direct dashboard-to-exchange order call.
- Runtime model retraining/self-modification.
- Unpinned opaque dependency.
- Secrets, private account data, or unredacted diagnostic bundle.

## Research contributions

Research changes must include a preregistered hypothesis, immutable dataset manifest, trial count/search space, chronological split, cost model, baselines, negative trials, and reproducible evidence bundle. A positive backtest is not sufficient.

## Commit standard

Use focused commits. Do not mix generated data, screenshots, binary artifacts, and source changes unless the commit explains why they are one evidence unit.
