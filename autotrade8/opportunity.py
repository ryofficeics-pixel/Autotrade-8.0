from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite


class Family(str, Enum):
    CASH = "CASH"
    FUNDING_CARRY = "FUNDING_CARRY_V1"
    CROSS_EXCHANGE_FUNDING = "CROSS_EXCHANGE_FUNDING_V1"
    CROSS_EXCHANGE_BASIS = "CROSS_EXCHANGE_BASIS_V1"
    CROSS_SECTIONAL_BREAKOUT = "CROSS_SECTIONAL_BREAKOUT_V1"
    ONCHAIN_EVENT = "ONCHAIN_EVENT_MOMENTUM_V1"


STRUCTURAL = frozenset(
    {Family.FUNDING_CARRY, Family.CROSS_EXCHANGE_FUNDING, Family.CROSS_EXCHANGE_BASIS}
)


class Lifecycle(str, Enum):
    EXPERIMENTAL = "EXPERIMENTAL"
    OBSERVING = "OBSERVING"
    VALIDATED = "VALIDATED"
    PAPER_ELIGIBLE = "PAPER_ELIGIBLE"
    PAPER_ACTIVE = "PAPER_ACTIVE"
    QUARANTINED = "QUARANTINED"
    RETIRED = "RETIRED"


class Side(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class VenueHealth(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    STALE = "STALE"
    DISCONNECTED = "DISCONNECTED"
    RATE_LIMITED = "RATE_LIMITED"
    MAINTENANCE = "MAINTENANCE"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class Leg:
    venue: str
    instrument: str
    side: Side
    qty: float
    price: float

    @property
    def notional(self) -> float:
        return abs(self.qty * self.price)

    @property
    def signed_notional(self) -> float:
        return self.notional if self.side is Side.LONG else -self.notional


@dataclass(frozen=True)
class CostBreakdown:
    """All values in bps of traded notional."""

    entry_fees: float = 0.0
    entry_spread: float = 0.0
    entry_slippage: float = 0.0
    entry_impact: float = 0.0
    entry_latency: float = 0.0
    entry_partial_fill: float = 0.0
    hold_funding_cost: float = 0.0
    hold_borrow: float = 0.0
    hold_basis_drift: float = 0.0
    hold_margin: float = 0.0
    hold_collateral_opportunity: float = 0.0
    exit_fees: float = 0.0
    exit_spread: float = 0.0
    exit_slippage: float = 0.0
    exit_impact: float = 0.0
    emergency_hedge_failure: float = 0.0
    emergency_forced_unwind: float = 0.0
    emergency_adverse_selection: float = 0.0
    risk_buffer: float = 0.0

    @property
    def entry_bps(self) -> float:
        return (
            self.entry_fees + self.entry_spread + self.entry_slippage
            + self.entry_impact + self.entry_latency + self.entry_partial_fill
        )

    @property
    def hold_bps(self) -> float:
        return (
            self.hold_funding_cost + self.hold_borrow + self.hold_basis_drift
            + self.hold_margin + self.hold_collateral_opportunity
        )

    @property
    def exit_bps(self) -> float:
        return self.exit_fees + self.exit_spread + self.exit_slippage + self.exit_impact

    @property
    def emergency_bps(self) -> float:
        return (
            self.emergency_hedge_failure + self.emergency_forced_unwind
            + self.emergency_adverse_selection
        )

    @property
    def total_bps(self) -> float:
        return self.entry_bps + self.hold_bps + self.exit_bps + self.emergency_bps + self.risk_buffer


@dataclass(frozen=True)
class GateResult:
    passed: bool
    reason: str | None = None


@dataclass(frozen=True)
class SentryResult:
    state: str  # CLEARED | BLOCKED
    gates: dict[str, GateResult]
    first_rejection_reason: str | None
    all_failures: tuple[str, ...] = ()


@dataclass
class Opportunity:
    opportunity_id: str
    family: Family
    strategy_version: str
    parameter_version: str
    discovered_at: float
    valid_until: float
    legs: tuple[Leg, ...]
    gross_expected_edge_bps: float
    costs: CostBreakdown
    notional_usd: float  # notional the bps figures are measured on
    required_capital: float
    expected_holding_seconds: float
    directional_delta_usd: float = 0.0
    gross_exposure_usd: float = 0.0
    liquidity_score: float = 0.0
    execution_quality: float = 0.0
    data_quality: float = 0.0
    evidence_score: float = 0.0
    risks: dict[str, float] = field(default_factory=dict)
    estimated_max_loss: float = 0.0
    lifecycle: Lifecycle = Lifecycle.EXPERIMENTAL
    cross_venue_timestamp_skew_ms: float = 0.0
    sentry: SentryResult | None = None

    def __post_init__(self) -> None:
        amounts = (
            self.discovered_at, self.valid_until, self.gross_expected_edge_bps,
            self.notional_usd, self.required_capital, self.expected_holding_seconds,
            self.directional_delta_usd, self.gross_exposure_usd, self.liquidity_score,
            self.execution_quality, self.data_quality, self.evidence_score,
            self.estimated_max_loss, self.cross_venue_timestamp_skew_ms,
            *vars(self.costs).values(), *self.risks.values(),
        )
        if not all(isfinite(value) for value in amounts):
            raise ValueError("opportunity contains non-finite economics")
        if self.family is Family.CASH:
            raise ValueError("CASH is allocated by abstaining, not by submitting legs")
        if not self.opportunity_id or self.valid_until <= self.discovered_at:
            raise ValueError("invalid opportunity identity or validity window")
        if self.notional_usd <= 0 or self.required_capital <= 0 or self.expected_holding_seconds <= 0:
            raise ValueError("notional, capital, and holding horizon must be positive")
        if any(value < 0 for value in vars(self.costs).values()):
            raise ValueError("negative cost components are forbidden")
        if self.estimated_max_loss < 0 or self.cross_venue_timestamp_skew_ms < 0:
            raise ValueError("invalid risk or clock skew")
        if any(not 0 <= value <= 1 for value in (
            self.liquidity_score, self.execution_quality, self.data_quality, self.evidence_score
        )):
            raise ValueError("quality measures must lie between 0 and 1")

    @property
    def instruments(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(leg.instrument for leg in self.legs))

    @property
    def venues(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(leg.venue for leg in self.legs))

    @property
    def expected_cost_bps(self) -> float:
        return self.costs.total_bps

    @property
    def expected_net_edge_bps(self) -> float:
        return self.gross_expected_edge_bps - self.costs.total_bps

    @property
    def edge_cost_ratio(self) -> float:
        c = self.costs.total_bps
        if c <= 0:
            return float("inf") if self.gross_expected_edge_bps > 0 else 0.0
        return self.gross_expected_edge_bps / c

    @property
    def expected_net_pnl(self) -> float:
        return self.expected_net_edge_bps / 1e4 * self.notional_usd

    @property
    def executable(self) -> bool:
        return self.sentry is not None and self.sentry.state == "CLEARED"

    @property
    def first_rejection_reason(self) -> str | None:
        return None if self.sentry is None else self.sentry.first_rejection_reason
