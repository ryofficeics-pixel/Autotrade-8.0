# 05 — Data and Provenance

## Objective

The data layer must reconstruct exactly what the system could know at every decision. If that cannot be proven, no strategy result is trustworthy.

## Required feeds

### Public market data

- instrument definitions and status;
- tick size, quantity step, minimum quantity/notional, price bands;
- trades;
- L2 snapshots and deltas with sequence identifiers where available;
- best bid/ask;
- mark, index, and last price;
- funding rate, next funding timestamp, and settled funding history;
- open interest and volume when exchange-native and timestamped;
- venue maintenance/status messages.

### Private PAPER data

- balances and available margin;
- orders, acknowledgements, rejects, cancels, and expiries;
- fills and fees;
- positions and unrealized PnL;
- funding debits/credits if PAPER provides them;
- account/risk tier changes.

## Event envelope

Every raw and canonical event includes:

| Field | Meaning |
|---|---|
| `event_id` | deterministic or UUID identity |
| `source` | venue/feed/channel |
| `schema_version` | parser contract |
| `instrument_id` | canonical instrument identity if applicable |
| `exchange_ts_ns` | exchange event time when supplied |
| `receive_monotonic_ns` | local monotonic arrival time |
| `receive_utc_ns` | local UTC arrival time |
| `sequence` | exchange sequence/update ID if supplied |
| `connection_epoch` | reconnect generation |
| `raw_hash` | hash of original payload bytes |
| `ingest_status` | valid/gap/duplicate/late/invalid |
| `payload` | immutable raw or canonical data |

## Storage layers

1. **Raw append-only**: original payload bytes plus envelope; never rewritten.
2. **Canonical events**: normalized units and instrument IDs; reproducible from raw.
3. **Decision snapshots**: exact causal view used for each decision.
4. **Research datasets**: immutable manifests referencing raw partitions and transform hashes.
5. **Derived reports**: disposable and reproducible.

## Provenance manifest

Each dataset/report records:

- source partitions and hashes;
- gap/staleness summary;
- canonical schema version;
- transform code commit;
- feature version;
- start/end event time;
- instruments and venue;
- timezone/clock quality;
- exclusion rules;
- random seeds;
- generated timestamp; and
- creator/process identity.

## Order-book integrity

For sequenced books:

1. obtain snapshot;
2. buffer deltas;
3. apply only continuous deltas after snapshot watermark;
4. detect gap, duplicate, out-of-order, or crossed book;
5. invalidate the book and resynchronize on failure; and
6. prevent entries during invalid/warming state.

For feeds without enforceable sequence semantics, the venue receives a worse data-quality grade and stricter staleness policy.

## Causal feature rule

Features at time `t` may use only events whose availability timestamp is no later than `t`. Exchange event time alone is insufficient: late arrivals cannot be moved backward in research.

Research must simulate receive-time ordering and feature warm-up. Revised candles, retroactive classifications, and final-bar values are prohibited unless they were available at decision time.

## Data-quality gates

New exposure is blocked when any required condition fails:

- connection unhealthy;
- staleness above per-feed threshold;
- sequence gap unresolved;
- timestamp skew above threshold;
- book crossed or empty;
- instrument rules missing/stale;
- funding timestamp/rate inconsistent;
- private account feed stale; or
- raw/audit persistence unavailable.

Thresholds are venue- and feed-specific configuration, tested from measured distributions—not guessed globally.

## Retention and cost

- Compress raw events by partition.
- Partition by venue/date/channel/instrument while avoiding tiny files.
- Keep metadata and decision snapshots longer than replaceable dashboards.
- Never delete raw partitions referenced by an active evidence package.
- Enforce disk-watermark alerts; low disk blocks new data-heavy research before it threatens runtime/audit persistence.

## Privacy and secrets

Raw public events are non-secret. Private account events are confidential and must be redacted before research export. API keys, signatures, nonces, headers, and full credential-bearing URLs are never stored.
