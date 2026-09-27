# AUTOTRADE 8.0 Repository Instructions

These rules apply to every human or AI coding agent working in this repository.

## Read first

Before changing code, read:

1. `docs/00_SYSTEM_CHARTER.md`
2. `docs/01_DECISION_REGISTER.md`
3. `docs/02_REQUIREMENTS_AND_SCOPE.md`
4. the domain document for the component being changed;
5. `docs/TRACEABILITY_MATRIX.md`.

## Hard rules

- PAPER only. Do not create a LIVE state, switch, credential, endpoint, or hidden escape hatch.
- Exactly one order authority.
- CASH/no-trade is always valid.
- No DCA, martingale, grid averaging, pyramiding, stop widening, recovery mode, or forced trade frequency.
- Position risk <= 0.5% equity; portfolio risk <= 1%; correlated positions share 0.5%.
- Daily operational halt 2%; 10% catastrophic stop; 50% project/account freeze.
- Initial leverage ceiling 1x. Do not unlock 3x/5x without a separately approved decision and evidence artifact.
- Maximum two positions.
- No LLM or runtime self-modification.
- Learning creates immutable offline challengers; promotion is manual.
- Missing/uncertain data, account state, cost, or risk fails closed.
- Resume Trading cannot bypass hard integrity faults.

## Implementation discipline

- Work from requirements and contracts, not screenshots or prototype code.
- Treat `autotrade8_phase1.zip` as evidence/reference only; do not copy it wholesale.
- Keep domain logic independent of venue SDK, web UI, and storage implementation.
- Inject clock, network, filesystem, and randomness.
- Use typed/versioned immutable events.
- Make consumers idempotent.
- Record decision reasons and all rejected candidates.
- Never silently repair or overwrite audit/evidence history.
- Do not claim economic validity from unit tests or green CI.

## Change requirements

Every non-trivial change must include:

- requirement/decision IDs;
- tests including failure paths;
- migration/rollback impact;
- security/risk impact;
- updated docs when behavior changes; and
- no secret or credential material.

## Stop conditions

Stop and request a decision if:

- documents conflict;
- a safety-critical requirement is ambiguous;
- venue behavior cannot be reconciled with the canonical contract;
- a dependency would become a second execution authority;
- a requested optimization weakens a hard risk invariant; or
- implementation would require LIVE credentials/capital.
