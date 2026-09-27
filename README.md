# AUTOTRADE 8.0

AUTOTRADE 8.0 is a research-first, evidence-gated USDT perpetual trading system for a 300 USDT PAPER account.

It is not a promise of continuous profit. Its job is to preserve capital by default, prove or reject trading hypotheses after realistic costs, and expose capital only when the evidence, market data, execution state, and risk budget all agree.

## Current status

- Documentation foundation plus an in-memory L2 integrity monitor and tests;
  see [implementation note](docs/22_MARKET_TRUTH_IMPLEMENTATION.md).
- No implementation in this repository is approved for trading runtime use.
- No LIVE mode exists in the approved design.
- Existing screenshots are inspiration/hypothesis sources, not evidence.
- `autotrade8_phase1.zip` is an archived prototype, not the implementation baseline.

## Non-negotiable operating policy

| Item | Policy |
|---|---|
| Capital | 300 USDT PAPER |
| Market | USDT perpetuals on one selected CEX |
| Default decision | CASH / NO TRADE |
| Open positions | Maximum 2 |
| Position risk | Maximum 0.5% of current equity |
| Portfolio open risk | Maximum 1.0%; correlated positions share one 0.5% budget |
| Daily operational halt | 2% realized + pessimistic open loss |
| Leverage | Starts at 1x; 3x/5x are gated ceilings, never targets |
| DCA / martingale / grid averaging | Forbidden |
| Daily trade quota | Forbidden; multiple trades/day are allowed only when qualified |
| Promotion | Manual only |
| LLM dependency | None; research and runtime are deterministic scripts |
| Runtime mutation | Forbidden; learning creates offline challengers only |

The +30% in 30 days objective is an aspiration used for reporting. It cannot change trade frequency, leverage, risk limits, or promotion criteria.

## Documentation map

1. [System charter](docs/00_SYSTEM_CHARTER.md)
2. [Decision register](docs/01_DECISION_REGISTER.md)
3. [Requirements and scope](docs/02_REQUIREMENTS_AND_SCOPE.md)
4. [Architecture](docs/03_ARCHITECTURE.md)
5. [Services and agent boundaries](docs/04_SERVICES_AND_AGENT_BOUNDARIES.md)
6. [Data and provenance](docs/05_DATA_AND_PROVENANCE.md)
7. [Replay and execution simulator](docs/06_REPLAY_AND_EXECUTION_SIMULATOR.md)
8. [Research and validation](docs/07_RESEARCH_AND_VALIDATION.md)
9. [Alpha discovery and evolution](docs/08_ALPHA_DISCOVERY_AND_EVOLUTION.md)
10. [Risk, capital, and leverage](docs/09_RISK_CAPITAL_AND_LEVERAGE.md)
11. [Execution, reconciliation, and state](docs/10_EXECUTION_RECONCILIATION_AND_STATE.md)
12. [Security and threat model](docs/11_SECURITY_AND_THREAT_MODEL.md)
13. [Dashboard, audit, and override](docs/12_DASHBOARD_AUDIT_AND_OVERRIDE.md)
14. [Testing and acceptance](docs/13_TESTING_AND_ACCEPTANCE.md)
15. [Operations runbook](docs/14_OPERATIONS_RUNBOOK.md)
16. [Venue selection](docs/15_VENUE_SELECTION.md)
17. [Implementation roadmap](docs/16_IMPLEMENTATION_ROADMAP.md)
18. [Legacy evidence review](docs/17_LEGACY_EVIDENCE_REVIEW.md)
19. [Glossary](docs/18_GLOSSARY.md)
20. [Configuration and event contracts](docs/19_CONFIGURATION_AND_EVENT_CONTRACTS.md)
21. [Observability and metrics](docs/20_OBSERVABILITY_AND_METRICS.md)
22. [Source manifest](docs/21_SOURCE_MANIFEST.md)
23. [Traceability matrix](docs/TRACEABILITY_MATRIX.md)

Repository-wide implementation rules are in [AGENTS.md](AGENTS.md), contribution rules in [CONTRIBUTING.md](CONTRIBUTING.md), and vulnerability handling in [SECURITY.md](SECURITY.md).

## Run the current observe-only app

With Python 3.11+ from the repository root:

```bash
PYTHONPATH=src python -m autotrade8.app
```

Open `http://127.0.0.1:8768`. The built-in input is a labeled **synthetic**
book with a sequence gap. For a canonical local NDJSON file use
`PYTHONPATH=src python -m autotrade8.app --input path/to/file.ndjson`.
Windows PowerShell equivalent: `$env:PYTHONPATH="src"; python -m autotrade8.app`.
This is a replay inspector, not a venue collector or trading bot.

### Windows sign-in autostart

Double-click `AUTOTRADE8_AUTOSTART.bat` once. It creates a **current-user**
Startup shortcut and runs the dashboard now. At each Windows sign-in the same
launcher starts the dashboard and retries after an unexpected exit (10 seconds).
Keep the repository at the same path; moving it breaks the shortcut. Python
3.11+ must be installed. To remove sign-in autostart, run
`AUTOTRADE8_AUTOSTART.bat uninstall` from Command Prompt. Closing the console
stops the current process; uninstalling does not close an existing console.
It always starts unarmed, with synthetic replay and no venue connection.

## Build rule

No code phase may begin until the documents for that phase have no unresolved safety-critical decisions. Every implementation pull request must identify the requirements and acceptance tests it satisfies.
