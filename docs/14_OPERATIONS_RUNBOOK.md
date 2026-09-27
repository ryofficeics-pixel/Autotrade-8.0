# 14 — Operations Runbook

## Operating modes

| Mode | Orders | Purpose |
|---|---|---|
| OFFLINE_RESEARCH | none | replay, simulation, experiments |
| OBSERVE | none | live market collection and health |
| PAPER_UNARMED | none | account/data/reconciliation readiness |
| PAPER_ARMED | PAPER only | approved strategy execution |
| PROBATION | PAPER, reduced limits | controlled resume after eligible halt |
| HALTED | no new exposure | incident/risk response |
| FAILED_SAFE | no commands except diagnostics/recovery | integrity cannot be established |

No LIVE mode exists.

## Daily startup checklist

1. Verify expected code/config/strategy hashes.
2. Verify disk space, clock sync, process ownership, and backup status.
3. Connect public and private feeds.
4. Load current instrument rules.
5. Reconcile balances, open orders, fills, positions, and risk reservations.
6. Validate data sequence/staleness and feature warm-up.
7. Confirm active limits: equity, position risk, daily loss, leverage ceiling.
8. Review unresolved incidents/halts.
9. Enter `PAPER_UNARMED`.
10. Arm manually only if all gates are green and strategy is approved.

## Normal monitoring

Automated monitoring covers:

- process heartbeat;
- feed age/sequence gaps;
- clock skew;
- API errors/rate limits;
- order and reconciliation state;
- open/cluster risk;
- daily and rolling loss;
- disk/memory/CPU;
- audit/backup health; and
- calibration/drift warnings.

The system records heartbeats continuously. A 10-minute audit task summarizes rather than substitutes for real-time guards.

## Halt response

1. Stop new intent acceptance.
2. Determine whether exposure is known and protected.
3. Reconcile venue truth.
4. Preserve raw events/logs and create incident bundle.
5. Apply reason-specific recovery.
6. Keep the system HALTED until factual checks pass.
7. Use Resume only if the halt class is eligible.

## Scenario runbooks

### Public market feed disconnected

- block entries immediately;
- do not infer prices;
- monitor private position/order state;
- reconnect with backoff;
- obtain fresh snapshot and sequence continuity;
- complete stability window before readiness.

### Private/account feed disconnected

- hard halt new exposure;
- query account/order REST within rate policy;
- protect known exposure only when state can be established;
- reconcile after reconnect.

### Unknown order after timeout

- do not resubmit;
- query by client order ID and recent fills;
- reserve worst-case exposure;
- resolve to accepted/filled/cancelled or remain HALTED.

### Position mismatch

- hard halt;
- treat venue position as truth;
- prevent exposure increase;
- reconcile fills/orders/account history;
- require manual incident closure.

### Daily 2% halt / five consecutive losses

- stop new entries;
- preserve/protect open positions;
- generate economic and execution diagnostics;
- operator may request controlled Resume after cooldown;
- probation policy applies.

### 10% session or 50% project stop

- non-overridable hard halt;
- no further PAPER trading;
- archive evidence and conduct full root-cause review;
- continuation requires a new decision/config/strategy generation.

### Low disk/audit failure

- stop new exposure before write capacity is exhausted;
- rotate non-authoritative derived outputs first;
- never delete referenced raw evidence or audit records;
- restore write/backup health before re-arm.

## Backup and restore

Back up:

- ledger and manifests;
- strategy/config registry;
- incident/evidence metadata;
- raw partition manifests; and
- required raw data according to retention policy.

Daily backup is encrypted and verified. Conduct periodic restore drills into a separate path and prove that reconciliation/replay can rebuild state.

## Windows laptop bootstrap

- dedicated non-admin OS user;
- wired network preferred; Wi-Fi is fallback;
- disable sleep/hibernation during approved sessions;
- restart policy with explicit unarmed boot;
- UPS is recommended before unattended long sessions;
- localhost dashboard by default; and
- log/data directories monitored for disk use.

## VPS migration gate

Move only after:

- local PAPER soak is stable;
- resource usage is measured;
- backup/restore and restart reconciliation pass;
- required network latency/reliability is known;
- provider fits Rp150,000/month; and
- secrets/firewall/time sync are configured securely.

## Post-incident review

Every material halt records timeline, detection, exposure, financial effect, root cause, failed defenses, corrective action, owner, test added, and decision whether the strategy/component remains approved.
