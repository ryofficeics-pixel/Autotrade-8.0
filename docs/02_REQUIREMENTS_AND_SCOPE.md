# 02 — Requirements and Scope

## Functional requirements

### Market and universe

- FR-001: Support one CEX adapter at bootstrap.
- FR-002: Support USDT-settled perpetual instruments only.
- FR-003: Build a dynamic candidate universe from exchange instrument metadata.
- FR-004: Filter candidates by status, age, depth, spread, volume, minimum notional, and data continuity.
- FR-005: Limit the bootstrap active universe to five instruments.

### Decisions and strategies

- FR-010: Produce `ENTER`, `EXIT`, `HOLD`, or `CASH` decisions.
- FR-011: Every decision includes strategy version, feature version, data watermark, expected edge distribution, cost distribution, expiry, and rejection reasons.
- FR-012: Log all eligible/rejected candidates, not only executed trades.
- FR-013: Keep strategy logic separate from risk, sizing, and execution.
- FR-014: Run counterfactual shadow decisions beside PAPER execution.

### Risk and capital

- FR-020: Enforce maximum two simultaneous positions.
- FR-021: Enforce 0.5% equity maximum pessimistic loss per independent position.
- FR-022: Enforce 1.0% equity maximum portfolio open risk.
- FR-023: Treat highly correlated positions as one risk cluster.
- FR-024: Enforce a 2% daily operational halt and 10% catastrophic stop.
- FR-025: Investigate at three consecutive losses and halt at five.
- FR-026: Start leverage at 1x; prevent 3x/5x until calibrated gates pass.
- FR-027: Reject DCA, martingale, grid averaging, pyramiding, and stop widening.

### Execution

- FR-030: Use exactly one order authority.
- FR-031: Validate instrument rules immediately before submission.
- FR-032: Use idempotent client order IDs tied to decision IDs.
- FR-033: Reconcile local, order, fill, position, balance, and risk state after every event and restart.
- FR-034: Block new exposure on unresolved mismatch.
- FR-035: Support PAPER only in the initial lifecycle.

### Evolution

- FR-040: Run deterministic offline candidate generation from frozen datasets.
- FR-041: Store every experiment, including failures.
- FR-042: Prevent challengers from mutating the running champion.
- FR-043: Require manual promotion and signed manifests.
- FR-044: Roll back/quarantine automatically on declared evidence or operational breaches; never promote automatically.

### Dashboard and audit

- FR-050: Show market-data, account, strategy, risk, and execution health separately.
- FR-051: Show CASH/BLOCK/ALLOW reason codes.
- FR-052: Provide `AUDIT_ERROR` diagnostic bundle creation.
- FR-053: Provide controlled `RESUME_TRADING` for eligible halts.
- FR-054: Display immutable history for halts, overrides, orders, fills, and config changes.

## Non-functional requirements

- NFR-001 Determinism: identical events and configuration produce identical decisions.
- NFR-002 Fail-closed: uncertainty blocks new exposure.
- NFR-003 Auditability: every derived outcome is traceable to raw events and code/config hashes.
- NFR-004 Restart safety: a crash/restart cannot duplicate an order or lose position truth.
- NFR-005 Resource efficiency: initial system runs on the user's Windows PC and later within the stated VPS budget.
- NFR-006 Security: secrets never enter source control, logs, reports, browser payloads, or research artifacts.
- NFR-007 Testability: clocks, randomness, network, and venue responses are injectable.
- NFR-008 Portability: venue-specific behavior is behind an adapter contract.
- NFR-009 Observability: health and financial/economic performance are separated.
- NFR-010 Reproducibility: reports include data, code, config, environment, and seed identities.

## Out of scope for bootstrap

- LIVE trading.
- Cross-venue execution.
- Spot borrowing and margin lending.
- Options, XAU, equities, DEX, Solana, LP, and wallet-copying.
- Social/media sentiment and on-chain feeds.
- Reinforcement-learning execution or policy selection.
- LLM agents.
- Mobile-native app.
- Automated cash deposits, withdrawals, or exchange transfers.

## Constraints

- Small starting capital makes fee, spread, and minimum-order errors material.
- Multiple daily trades are desirable only when net opportunities exist.
- The design may use open-source libraries, but no library supplies economic edge by itself.
- The target is unattended operation, but manual arming/promotion and incident review remain deliberate controls.

## Definition of done for documentation foundation

- Every functional requirement maps to an owning component and an acceptance test.
- Safety limits are unambiguous.
- State transitions and override limits are explicit.
- No document promises profitability.
- No document authorizes LIVE mode.
- Cross-document links and terminology are consistent.
