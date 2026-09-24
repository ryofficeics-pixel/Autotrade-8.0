from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .opportunity import Side


class BundleState(str, Enum):
    PROPOSED = "PROPOSED"
    RESERVED = "RESERVED"
    SUBMITTING = "SUBMITTING"
    PARTIALLY_HEDGED = "PARTIALLY_HEDGED"
    HEDGED = "HEDGED"
    ACTIVE = "ACTIVE"
    UNWINDING = "UNWINDING"
    CLOSED = "CLOSED"
    EMERGENCY = "EMERGENCY"
    FAILED = "FAILED"


S = BundleState
TRANSITIONS: dict[BundleState, frozenset[BundleState]] = {
    S.PROPOSED: frozenset({S.RESERVED, S.FAILED}),
    S.RESERVED: frozenset({S.SUBMITTING, S.FAILED}),
    S.SUBMITTING: frozenset({S.PARTIALLY_HEDGED, S.HEDGED, S.FAILED, S.EMERGENCY}),
    S.PARTIALLY_HEDGED: frozenset({S.HEDGED, S.UNWINDING, S.EMERGENCY}),
    S.HEDGED: frozenset({S.ACTIVE, S.UNWINDING, S.EMERGENCY}),
    S.ACTIVE: frozenset({S.UNWINDING, S.EMERGENCY}),
    S.UNWINDING: frozenset({S.CLOSED, S.EMERGENCY}),
    S.EMERGENCY: frozenset({S.UNWINDING, S.CLOSED, S.FAILED}),
    S.CLOSED: frozenset(),
    S.FAILED: frozenset(),
}
_TERMINAL = {S.CLOSED, S.FAILED}
_IDLE = {S.PROPOSED, S.RESERVED} | _TERMINAL


class HedgeAction(str, Enum):
    NONE = "NONE"
    RETRY_HEDGE = "RETRY_HEDGE"
    ALTERNATIVE_HEDGE = "ALTERNATIVE_HEDGE"
    UNWIND = "UNWIND"
    HALT_STRATEGY = "HALT_STRATEGY"
    ESCALATE = "ESCALATE"


class IllegalTransition(Exception):
    pass


@dataclass(frozen=True)
class HedgeLimits:
    max_unhedged_seconds: float = 5.0
    max_delta_usd: float = 10.0
    max_delta_percent: float = 0.02
    max_leg_slippage_bps: float = 10.0
    max_partial_fill_duration: float = 10.0
    max_hedge_retries: int = 3


@dataclass
class LegFill:
    venue: str
    side: Side
    target_qty: float
    filled_qty: float = 0.0
    avg_price: float = 0.0
    expected_price: float = 0.0

    @property
    def filled_notional(self) -> float:
        return self.filled_qty * self.avg_price

    @property
    def signed_notional(self) -> float:
        return self.filled_notional if self.side is Side.LONG else -self.filled_notional

    @property
    def slippage_bps(self) -> float:
        """Positive = adverse."""
        if self.filled_qty <= 0 or self.expected_price <= 0:
            return 0.0
        diff = self.avg_price - self.expected_price
        if self.side is Side.SHORT:
            diff = -diff
        return diff / self.expected_price * 1e4


@dataclass
class MultiLegBundle:
    bundle_id: str
    legs: list[LegFill]
    limits: HedgeLimits = field(default_factory=HedgeLimits)
    state: BundleState = BundleState.PROPOSED
    retries: int = 0
    history: list[tuple[float, BundleState]] = field(default_factory=list)
    _unhedged_since: float | None = None
    _partial_since: float | None = None

    def transition(self, new: BundleState, ts: float) -> None:
        if new not in TRANSITIONS[self.state]:
            raise IllegalTransition(f"{self.state.value} -> {new.value}")
        if new in {S.HEDGED, S.ACTIVE} and (
            not self.legs or any(leg.filled_qty < leg.target_qty for leg in self.legs)
            or self.is_unhedged or self.gross_usd <= 0
        ):
            raise IllegalTransition("hedge incomplete or delta exceeds limit")
        self.state = new
        self.history.append((ts, new))
        if new is S.PARTIALLY_HEDGED:
            self._partial_since = ts
        elif new is not S.EMERGENCY:
            self._partial_since = None

    @property
    def delta_usd(self) -> float:
        return sum(leg.signed_notional for leg in self.legs)

    @property
    def gross_usd(self) -> float:
        return sum(leg.filled_notional for leg in self.legs)

    @property
    def delta_pct(self) -> float:
        g = self.gross_usd
        return abs(self.delta_usd) / g if g > 0 else 0.0

    @property
    def is_unhedged(self) -> bool:
        if self.gross_usd <= 0:
            return False
        return (abs(self.delta_usd) > self.limits.max_delta_usd
                or self.delta_pct > self.limits.max_delta_percent)

    def unhedged_seconds(self, now: float) -> float:
        return 0.0 if self._unhedged_since is None else now - self._unhedged_since

    def record_retry(self) -> None:
        self.retries += 1

    def evaluate(self, now: float) -> tuple[HedgeAction, str]:
        """Fail-closed hedge supervisor. Caller executes the returned action."""
        if self.state in _IDLE:
            return HedgeAction.NONE, "IDLE"
        just_detected = False
        if self.is_unhedged:
            if self._unhedged_since is None:
                self._unhedged_since = now
                just_detected = True
        else:
            self._unhedged_since = None
        lim = self.limits
        worst = max((leg.slippage_bps for leg in self.legs), default=0.0)
        if worst > lim.max_leg_slippage_bps and self.state is not S.UNWINDING:
            return HedgeAction.UNWIND, "LEG_SLIPPAGE_EXCEEDED"
        if just_detected and self.state is not S.UNWINDING and self.state is not S.EMERGENCY:
            return HedgeAction.RETRY_HEDGE, "DIRECTIONAL_EXPOSURE_DETECTED"
        dur = self.unhedged_seconds(now)
        if self.is_unhedged and dur > lim.max_unhedged_seconds:
            if self.state is S.EMERGENCY and dur > 2 * lim.max_unhedged_seconds:
                return HedgeAction.ESCALATE, "EMERGENCY_UNRESOLVED"
            if self.state is S.UNWINDING:
                return HedgeAction.HALT_STRATEGY, "UNWIND_INCOMPLETE"
            if self.retries < lim.max_hedge_retries and self.state is not S.EMERGENCY:
                return HedgeAction.RETRY_HEDGE, "UNHEDGED_TIMEOUT"
            return HedgeAction.UNWIND, "HEDGE_RETRIES_EXHAUSTED"
        if (self.state is S.PARTIALLY_HEDGED and self._partial_since is not None
                and now - self._partial_since > lim.max_partial_fill_duration):
            return HedgeAction.UNWIND, "PARTIAL_FILL_TIMEOUT"
        return HedgeAction.NONE, "OK"
