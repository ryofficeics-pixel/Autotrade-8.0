# Market truth foundation — implementation note

## Scope and traceability

- `src/autotrade8/market.py` implements a canonical L2 event schema and an
  in-memory, single-instrument integrity monitor. Supports FR-001/002 data
  contracts, NFR-001, NFR-002 and NFR-007 under D-004, D-005 and D-023.
- `tests/test_market.py` exercises snapshot, delta, gap, duplicate, crossed/empty
  book, reconnect, stale feed, clock skew, invalid numbers and recovery paths.
- `src/autotrade8/app.py` provides a loopback-only, read-only replay inspector.
  Its default sample is explicitly synthetic and deliberately ends in a gap.
- Exact contiguous integer sequence semantics are a **normalizer contract**;
  venue-specific sequence ranges or overlap rules must be validated separately.
  The monitor alone is not an account health gate or permission to place orders.

## Usage

Run with `PYTHONPATH=src python -m unittest discover -s tests -v` from repo root.
Launch the browser inspector with `PYTHONPATH=src python -m autotrade8.app` and
open `http://127.0.0.1:8768`. Supply a canonical L2 NDJSON file using
`--input path/to/fixture.ndjson`; use `--summary` for JSON output. Each line
must contain the exact `BookEvent` fields in `app.py`, with `bids`/`asks` as
`[["price", "quantity"], ...]` decimal strings. Sample data is not market data.
The app replays a bounded fixture at its recorded arrival times and does not
collect a live feed, accept browser uploads or store any events.
Inject clocks in nanoseconds and choose the thresholds from the measured venue
capture distribution. Feed a complete snapshot on every reconnect or gap.
`BookHealth.entry_allowed` describes only the L2 book; a runtime entry must also
pass account, persistence, instrument-rule, risk, reconciliation and manual arm
gates. No order execution code or live state is present.

## Pending decisions and evidence

- O-001: select venue after documented multi-day comparisons. No adapter yet.
- O-002: choose universe thresholds from observations. No Top-N yet.
- O-005: benchmark raw-data compression/retention on the actual laptop before
  choosing or implementing persistent raw storage. This monitor is in-memory.
- Phase 1 soak, raw persistence, provenance and schema migration tests are pending;
  this implementation does not satisfy Phase 1 acceptance or show economic edge.

## Migration, rollback and risk impact

This is a new, side-effect-free package with schema version 1. There is no state
or data migration and no trading exposure. Rollback removes `src/`, `tests/` and
this note. Invalid events block the monitored book; the consumer must record
the rejection independently and request a fresh snapshot. Neither a reconnect
nor a manual override can synthesize missing exchange facts.
