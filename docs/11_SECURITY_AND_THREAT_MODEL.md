# 11 — Security and Threat Model

## Assets

- exchange API credentials;
- account/order/position data;
- approved strategy and risk manifests;
- raw and derived market data;
- audit ledger and evidence bundles;
- operator identity/session;
- source code and dependency supply chain.

## Trust boundaries

1. Exchange/public internet.
2. Local/VPS operating system.
3. Market-data process.
4. Execution process holding PAPER credentials.
5. Dashboard/browser.
6. Offline research environment.
7. GitHub/source and dependency registries.

## Threats and controls

| Threat | Impact | Required control |
|---|---|---|
| API key leaked | unauthorized actions/data exposure | runtime secret injection, no logs/git/UI, scoped key, IP allowlist if available |
| Dashboard command forgery | unauthorized arm/resume | authentication, CSRF protection, short session, command signing/audit |
| Malicious dependency | credential theft/order manipulation | lockfiles, hash/signature verification, dependency review, minimal runtime deps |
| Tampered strategy/config | hidden risk change | signed/hash-pinned manifests and startup verification |
| WebSocket spoof/replay/gap | false market state | TLS, sequence checks, timestamp/connection epochs, staleness gates |
| Duplicate process/order | doubled exposure | single-writer lease, idempotent IDs, reconciliation |
| Log injection/secret leakage | corrupted audit/confidentiality | structured logs, escaping, redaction tests |
| Clock manipulation | stale data accepted | monotonic health clock, exchange/local skew monitoring |
| Disk exhaustion | lost audit/data | quotas, watermarks, rotation, halt before critical failure |
| Local malware/operator error | account compromise | least privilege, separate OS user, updates, restricted firewall |
| Supply-chain artifact replacement | unreviewed code executes | pinned commit/release, checksum/signature, SBOM |
| Resume abuse | repeated risk bypass | eligible-reason allowlist, cooldown, probation, immutable counter |

## Credential policy

- Bootstrap uses PAPER credentials only.
- If public data does not require credentials, collector gets none.
- Execution credential permissions are minimum necessary; no withdrawal permission.
- Secrets are loaded from OS-protected storage/environment at process start.
- Secrets are never passed as CLI arguments.
- Rotation invalidates old credentials and produces an audit event.
- Diagnostic bundles redact secrets and authentication material by test, not assumption.

## Process isolation

- Research never receives execution credentials.
- Dashboard never receives exchange credentials.
- Only order authority can access the PAPER trading key.
- Collector and dashboard compromise must not create orders.
- Runtime data directories use least-privilege filesystem permissions.

## Network policy

- Outbound allowlist to selected exchange and required time/DNS services where practical.
- Dashboard binds to localhost by default.
- Remote access requires authenticated encrypted tunnel/reverse proxy; never expose raw development server.
- No inbound port is required for trading.

## Dependency policy

Before adding a third-party package:

- verify official source and license;
- pin exact version and hashes;
- inspect maintenance/security posture;
- document network/file/process access;
- scan known vulnerabilities;
- test failure behavior; and
- define removal/replacement path.

Framework popularity is not security evidence.

## Audit integrity

Ledger records are append-only and hash-chained by partition. Daily manifests are signed/hashed and backed up. Dashboard edits create new events; they never rewrite old rows.

## Incident classes

| Severity | Example | Response |
|---|---|---|
| SEV-1 | credential exposure, unknown position, tampered binary/config | hard halt, isolate, rotate, reconcile, manual review |
| SEV-2 | data corruption/gap, repeated order mismatch | halt new exposure, preserve evidence, repair/resync |
| SEV-3 | dashboard/reporting fault | runtime continues if independently healthy; repair UI |
| SEV-4 | research job failure | record failure; no runtime impact |

## Security acceptance

- secret-scanning test passes;
- no withdrawal-capable credential exists;
- unauthorized dashboard command tests fail safely;
- tampered manifest prevents arming;
- duplicate-instance test preserves single order authority;
- diagnostic export contains no secrets; and
- backup restore/reconciliation drill succeeds.
