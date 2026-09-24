from __future__ import annotations

from dataclasses import dataclass, field

from .opportunity import (
    STRUCTURAL,
    GateResult,
    Lifecycle,
    Opportunity,
    SentryResult,
    VenueHealth,
)

GATE_ORDER = (
    "DATA", "LIQUIDITY", "ALPHA", "EDGE", "COST", "EDGE_COST",
    "RISK", "CAPITAL", "VENUE", "EXPOSURE", "EXECUTION_PLAN",
)


@dataclass(frozen=True)
class SentryConfig:
    min_data_quality: float = 0.8
    max_timestamp_skew_ms: float = 250.0
    min_liquidity: float = 0.5
    min_evidence: float = 0.5
    min_edge_cost_ratio: float = 3.0
    max_loss_pct_equity: float = 0.01
    min_expected_net_pnl_usd: float = 0.50
    min_leg_notional_usd: float = 5.0
    max_structural_delta_pct: float = 0.02
    required_lifecycle: tuple[Lifecycle, ...] = (Lifecycle.PAPER_ACTIVE,)


@dataclass
class SentryContext:
    now: float
    equity: float
    available_capital: float
    venue_health: dict[str, VenueHealth] = field(default_factory=dict)
    halt_reason: str | None = None


def _ok() -> GateResult:
    return GateResult(True)


def _fail(reason: str) -> GateResult:
    return GateResult(False, reason)


def _data(o: Opportunity, c: SentryContext, cfg: SentryConfig) -> GateResult:
    if c.now < o.discovered_at or c.now >= o.valid_until:
        return _fail("OPPORTUNITY_EXPIRED_OR_FUTURE")
    if o.data_quality < cfg.min_data_quality:
        return _fail("DATA_QUALITY_LOW")
    if o.cross_venue_timestamp_skew_ms > cfg.max_timestamp_skew_ms:
        return _fail("CROSS_VENUE_TIMESTAMP_SKEW")
    return _ok()


def _liquidity(o: Opportunity, c: SentryContext, cfg: SentryConfig) -> GateResult:
    return _ok() if o.liquidity_score >= cfg.min_liquidity else _fail("LIQUIDITY_TOO_LOW")


def _alpha(o: Opportunity, c: SentryContext, cfg: SentryConfig) -> GateResult:
    if o.lifecycle not in cfg.required_lifecycle:
        return _fail(f"ALPHA_NOT_PROMOTED:{o.lifecycle.value}")
    if o.evidence_score < cfg.min_evidence:
        return _fail("EVIDENCE_SCORE_LOW")
    return _ok()


def _edge(o: Opportunity, c: SentryContext, cfg: SentryConfig) -> GateResult:
    return _ok() if o.expected_net_edge_bps > 0 else _fail("NET_EDGE_NOT_POSITIVE")


def _cost(o: Opportunity, c: SentryContext, cfg: SentryConfig) -> GateResult:
    return _ok() if o.expected_cost_bps > 0 else _fail("COST_MODEL_INVALID")


def _edge_cost(o: Opportunity, c: SentryContext, cfg: SentryConfig) -> GateResult:
    if o.edge_cost_ratio < cfg.min_edge_cost_ratio:
        return _fail(f"EDGE_COST_RATIO_BELOW_{cfg.min_edge_cost_ratio:g}")
    return _ok()


def _risk(o: Opportunity, c: SentryContext, cfg: SentryConfig) -> GateResult:
    if c.halt_reason:
        return _fail(f"HALTED:{c.halt_reason}")
    if o.estimated_max_loss > cfg.max_loss_pct_equity * c.equity:
        return _fail("MAX_LOSS_EXCEEDS_LIMIT")
    return _ok()


def _capital(o: Opportunity, c: SentryContext, cfg: SentryConfig) -> GateResult:
    if o.expected_net_pnl < cfg.min_expected_net_pnl_usd:
        return _fail("CAPITAL_TOO_SMALL")
    if o.required_capital > c.available_capital:
        return _fail("INSUFFICIENT_AVAILABLE_CAPITAL")
    return _ok()


def _venue(o: Opportunity, c: SentryContext, cfg: SentryConfig) -> GateResult:
    for v in o.venues:
        h = c.venue_health.get(v, VenueHealth.DISCONNECTED)
        if h is not VenueHealth.HEALTHY:
            return _fail(f"VENUE_{h.value}:{v}")
    return _ok()


def _exposure(o: Opportunity, c: SentryContext, cfg: SentryConfig) -> GateResult:
    if o.family not in STRUCTURAL:
        return _ok()
    if o.gross_exposure_usd <= 0:
        return _fail("EXPOSURE_UNDEFINED")  # fail closed: delta % cannot be computed
    if abs(o.directional_delta_usd) / o.gross_exposure_usd > cfg.max_structural_delta_pct:
        return _fail("DELTA_EXCEEDS_LIMIT")
    return _ok()


def _plan(o: Opportunity, c: SentryContext, cfg: SentryConfig) -> GateResult:
    if not o.legs:
        return _fail("NO_LEGS")
    if o.family in STRUCTURAL and len(o.legs) < 2:
        return _fail("STRUCTURAL_NEEDS_TWO_LEGS")
    if any(leg.qty <= 0 or leg.price <= 0 for leg in o.legs):
        return _fail("INVALID_LEG")
    if any(leg.notional < cfg.min_leg_notional_usd for leg in o.legs):
        return _fail("LEG_BELOW_MIN_NOTIONAL")
    if o.expected_holding_seconds <= 0:
        return _fail("INVALID_HOLDING_HORIZON")
    if c.now >= o.valid_until:
        return _fail("OPPORTUNITY_EXPIRED")
    return _ok()


_GATES = {
    "DATA": _data, "LIQUIDITY": _liquidity, "ALPHA": _alpha, "EDGE": _edge,
    "COST": _cost, "EDGE_COST": _edge_cost, "RISK": _risk, "CAPITAL": _capital,
    "VENUE": _venue, "EXPOSURE": _exposure, "EXECUTION_PLAN": _plan,
}


def evaluate(o: Opportunity, ctx: SentryContext, cfg: SentryConfig | None = None) -> SentryResult:
    """Run every gate (no short-circuit) and report the first binding failure."""
    cfg = cfg or SentryConfig()
    gates = {name: _GATES[name](o, ctx, cfg) for name in GATE_ORDER}
    fails = tuple(f"{n}:{g.reason}" for n, g in gates.items() if not g.passed)
    first = next((g.reason for g in gates.values() if not g.passed), None)
    result = SentryResult("BLOCKED" if fails else "CLEARED", gates, first, fails)
    o.sentry = result
    return result
