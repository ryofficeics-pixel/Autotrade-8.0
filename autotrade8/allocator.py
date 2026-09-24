from __future__ import annotations

from dataclasses import dataclass, field

from .costs import risk_adjusted_capital_efficiency
from .opportunity import Opportunity
from .sentry import SentryContext, evaluate

SCORE_VERSION = "OPP_SCORE_V1"


class CapitalError(Exception):
    pass


class CapitalLedger:
    """AVAILABLE -> RESERVED -> DEPLOYED -> RELEASE_PENDING -> AVAILABLE."""

    def __init__(self, equity: float) -> None:
        if equity < 0:
            raise ValueError("equity must be >= 0")
        self.equity = equity
        self._reserved: dict[str, float] = {}
        self._deployed: dict[str, float] = {}
        self._pending: dict[str, float] = {}

    @property
    def reserved(self) -> float:
        return sum(self._reserved.values())

    @property
    def deployed(self) -> float:
        return sum(self._deployed.values())

    @property
    def release_pending(self) -> float:
        return sum(self._pending.values())

    @property
    def available(self) -> float:
        return self.equity - self.reserved - self.deployed - self.release_pending

    def state_of(self, oid: str) -> str:
        for name, d in (("RESERVED", self._reserved), ("DEPLOYED", self._deployed),
                        ("RELEASE_PENDING", self._pending)):
            if oid in d:
                return name
        return "AVAILABLE"

    def active_ids(self) -> set[str]:
        return set(self._reserved) | set(self._deployed) | set(self._pending)

    def reserve(self, oid: str, amount: float) -> None:
        if amount <= 0:
            raise CapitalError("amount must be > 0")
        if oid in self.active_ids():
            raise CapitalError(f"{oid} already holds capital")
        if amount > self.available + 1e-9:
            raise CapitalError("insufficient available capital")
        self._reserved[oid] = amount

    def cancel(self, oid: str) -> None:
        if oid not in self._reserved:
            raise CapitalError("not RESERVED")
        del self._reserved[oid]

    def deploy(self, oid: str) -> None:
        if oid not in self._reserved:
            raise CapitalError("not RESERVED")
        self._deployed[oid] = self._reserved.pop(oid)

    def begin_release(self, oid: str) -> None:
        if oid not in self._deployed:
            raise CapitalError("not DEPLOYED")
        self._pending[oid] = self._deployed.pop(oid)

    def complete_release(self, oid: str, realized_pnl: float = 0.0) -> None:
        if oid not in self._pending:
            raise CapitalError("not RELEASE_PENDING")
        del self._pending[oid]
        self.equity += realized_pnl


@dataclass(frozen=True)
class ScoreBreakdown:
    version: str
    capital_efficiency_bps_day: float
    liquidity: float
    evidence: float
    score: float


def opportunity_score(o: Opportunity) -> ScoreBreakdown:
    """OPP_SCORE_V1 = RACE_V1 (bps/capital-day) x liquidity x evidence. Components exposed."""
    ce = risk_adjusted_capital_efficiency(o)
    s = ce * max(o.liquidity_score, 0.0) * max(o.evidence_score, 0.0)
    return ScoreBreakdown(SCORE_VERSION, ce, o.liquidity_score, o.evidence_score, s)


@dataclass(frozen=True)
class AllocatorConfig:
    cash_hurdle_score: float = 1.0  # bps/capital-day placeholder (~3.65%/yr); tune from evidence
    max_active_bundles: int = 1
    min_switch_usd: float = 0.50
    switch_margin_ratio: float = 0.25  # replacement edge must exceed 25% of remaining value


@dataclass(frozen=True)
class ActivePosition:
    opportunity_id: str
    remaining_value_usd: float
    exit_cost_usd: float


@dataclass
class Decision:
    target: Opportunity | None  # None => CASH
    action: str  # ALLOCATE | HOLD | SWITCH | CASH
    reason: str
    ranked: list[tuple[Opportunity, ScoreBreakdown]] = field(default_factory=list)
    replacement_edge_usd: float | None = None


def replacement_edge_usd(
    new_net_pnl: float, remaining_value: float, current_exit_cost: float, switch_risk: float
) -> float:
    """new_net_pnl is already net of the new entry cost (no double counting)."""
    return new_net_pnl - remaining_value - current_exit_cost - switch_risk


class CapitalAllocator:
    def __init__(self, ledger: CapitalLedger, cfg: AllocatorConfig | None = None) -> None:
        self.ledger = ledger
        self.cfg = cfg or AllocatorConfig()

    def rank(self, opps: list[Opportunity], ctx: SentryContext) -> list[tuple[Opportunity, ScoreBreakdown]]:
        """Recheck all gates at decision time; a cached CLEARED state can expire."""
        if ctx.available_capital > self.ledger.available + 1e-9:
            raise CapitalError("context capital exceeds available research capital")
        cleared = [o for o in opps if evaluate(o, ctx).state == "CLEARED"]
        scored = [(o, opportunity_score(o)) for o in cleared
                  if o.required_capital <= self.ledger.available]
        return sorted(scored, key=lambda t: t[1].score, reverse=True)

    def decide(
        self, opps: list[Opportunity], ctx: SentryContext,
        active: ActivePosition | None = None,
        switch_risk_usd: float = 0.0,
    ) -> Decision:
        ranked = self.rank(opps, ctx)
        qualified = [(o, s) for o, s in ranked if s.score > self.cfg.cash_hurdle_score]
        if active is None:
            if not qualified:
                return Decision(None, "CASH", "NO_QUALIFIED_EDGE", ranked)
            return Decision(qualified[0][0], "ALLOCATE", "BEST_QUALIFIED", ranked)
        cands = [(o, s) for o, s in qualified if o.opportunity_id != active.opportunity_id]
        if not cands:
            return Decision(None, "HOLD", "NO_SUPERIOR_CANDIDATE", ranked)
        best = cands[0][0]
        edge = replacement_edge_usd(
            best.expected_net_pnl, active.remaining_value_usd, active.exit_cost_usd, switch_risk_usd
        )
        threshold = max(self.cfg.min_switch_usd,
                        self.cfg.switch_margin_ratio * abs(active.remaining_value_usd))
        if edge > threshold:
            return Decision(best, "SWITCH", "REPLACEMENT_EDGE_EXCEEDS_HURDLE", ranked, edge)
        return Decision(None, "HOLD", "HYSTERESIS", ranked, edge)

    def commit(self, d: Decision, ctx: SentryContext) -> None:
        """Reserve capital for an ALLOCATE decision (SWITCH must release first)."""
        if d.action not in ("ALLOCATE", "SWITCH") or d.target is None:
            return
        if len(self.ledger.active_ids()) >= self.cfg.max_active_bundles:
            raise CapitalError("max active bundles reached")
        if evaluate(d.target, ctx).state != "CLEARED":
            raise CapitalError("SENTRY no longer clears opportunity")
        self.ledger.reserve(d.target.opportunity_id, d.target.required_capital)
