# Security Policy

## Scope

Security issues include credential exposure, unauthorized command/order paths, risk-control bypass, state/reconciliation corruption, dependency compromise, audit tampering, and leakage of private account data.

## Reporting

Do not open a public issue containing credentials, exploit details, private account data, or a working risk bypass. Use GitHub private vulnerability reporting/security advisory for the repository owner when available.

Include:

- affected commit/version;
- reproduction steps with redacted data;
- expected vs actual result;
- potential financial/security impact; and
- suggested containment if known.

## Immediate containment

For a suspected runtime incident:

1. enter hard HALTED state;
2. preserve evidence;
3. reconcile venue account truth;
4. isolate affected process/host;
5. rotate exposed PAPER credentials;
6. verify manifests and dependencies; and
7. do not Resume until the incident is resolved.

The complete design is in `docs/11_SECURITY_AND_THREAT_MODEL.md`.

## Supported mode

Only the documented PAPER mode is supported. No LIVE credential or capital is authorized.
