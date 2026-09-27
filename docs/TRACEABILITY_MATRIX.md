# Requirements Traceability Matrix

This matrix maps requirements to design owner and minimum acceptance evidence.

| Requirement | Design owner | Acceptance evidence |
|---|---|---|
| FR-001–005 market/universe | Data plane + venue adapter | venue rubric, instrument rules, Top-N rejection tests |
| FR-010–014 decisions | Strategy/allocator | deterministic decision snapshots, CASH/rejection/counterfactual tests |
| FR-020–027 risk | Risk Sentry | sizing, portfolio, halt, leverage, prohibited-behavior property tests |
| FR-030–035 execution | Order authority/reconciler | idempotency, partial fill, restart, mismatch, PAPER-only tests |
| FR-040–044 evolution | Experiment engine/registry | immutable trials, sealed validation, manual promotion tests |
| FR-050–054 dashboard/audit | Dashboard control plane | projection, error bundle, resume eligibility/denial tests |
| NFR-001 determinism | Replay + domain | golden replay equality |
| NFR-002 fail-closed | All gates | fault injection produces BLOCK/HALT |
| NFR-003 auditability | Ledger/provenance | decision-to-raw trace reconstruction |
| NFR-004 restart safety | Reconciler/order authority | crash matrix and open-position restart drill |
| NFR-005 efficiency | Runtime/operations | measured laptop/VPS resource budget |
| NFR-006 security | Security boundary | secret, auth, tamper, backup tests |
| NFR-007 testability | Architecture | injectable clock/network/randomness tests |
| NFR-008 portability | Venue adapter | canonical contract test suite across mock adapters |
| NFR-009 observability | Dashboard/metrics | independent health planes and alerts |
| NFR-010 reproducibility | Evidence registry | rerun report with matching hashes/results |
| Configuration/event contracts | Config loader/event bus | schema validation, compatibility, immutable arm-epoch tests |
| Observability | Metrics/logging/alerts | alert fault injection, redaction, correlation trace tests |

## Decision-to-document map

| Decisions | Primary document |
|---|---|
| D-001, D-004 | [Roadmap](16_IMPLEMENTATION_ROADMAP.md), [Legacy review](17_LEGACY_EVIDENCE_REVIEW.md) |
| D-002, D-003, D-006, D-023 | [Venue selection](15_VENUE_SELECTION.md), [Data](05_DATA_AND_PROVENANCE.md) |
| D-005, D-018, D-031, D-032 | [Research](07_RESEARCH_AND_VALIDATION.md), [Execution](10_EXECUTION_RECONCILIATION_AND_STATE.md) |
| D-007–D-15, D-26–D-30 | [Risk](09_RISK_CAPITAL_AND_LEVERAGE.md) |
| D-016, D-017 | [Evolution](08_ALPHA_DISCOVERY_AND_EVOLUTION.md) |
| D-019, D-020 | [Dashboard/override](12_DASHBOARD_AUDIT_AND_OVERRIDE.md) |
| D-021, D-022 | [Operations](14_OPERATIONS_RUNBOOK.md) |
| D-024 | [Scope](02_REQUIREMENTS_AND_SCOPE.md), [Roadmap](16_IMPLEMENTATION_ROADMAP.md) |
| D-025 | [Charter](00_SYSTEM_CHARTER.md), [Risk](09_RISK_CAPITAL_AND_LEVERAGE.md) |

## Completion rule

An implementation task is incomplete if it cannot identify:

1. the requirement(s) it satisfies;
2. the accepted decision(s) it implements;
3. the test evidence proving it; and
4. the documentation changed when behavior differs.
