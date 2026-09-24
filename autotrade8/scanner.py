"""Read-only structural research. No portfolio, credentials, or order-submit imports.

All costs and gross edges use bps of ONE matched leg's USDT notional.
The four-entry/exit transactions of a two-leg bundle are summed in that unit.
Funding projections are hypotheses, never calibrated forecasts.
"""

from __future__ import annotations

import hashlib
import math
import statistics
from dataclasses import dataclass

from .funding import conservative_expected_funding_bps_per_hour, funding_persistence_score
from .opportunity import CostBreakdown, Family, Leg, Lifecycle, Opportunity, Side
from .sentry import SentryContext, evaluate


@dataclass(frozen=True)
class Quote:
    venue: str
    instrument: str
    kind: str  # SPOT or PERP
    bid: float
    ask: float
    bid_depth_usd: float
    ask_depth_usd: float
    min_notional_usd: float
    fee_bps_per_side: float
    event_time: float | None
    exchange_receive_time: float | None
    local_receive_time: float
    local_monotonic_time: float
    funding_interval_hours: float | None = None
    next_funding_time: float | None = None
    settled_funding: tuple[float, ...] = ()  # six or more independently settled prints
    mark_price: float | None = None
    index_price: float | None = None

    def __post_init__(self) -> None:
        numeric = (self.bid, self.ask, self.bid_depth_usd, self.ask_depth_usd,
                   self.min_notional_usd, self.fee_bps_per_side, self.local_receive_time,
                   self.local_monotonic_time, *self.settled_funding)
        numeric += tuple(x for x in (self.event_time, self.exchange_receive_time,
                                     self.funding_interval_hours, self.next_funding_time,
                                     self.mark_price, self.index_price) if x is not None)
        if not all(math.isfinite(x) for x in numeric) or self.bid <= 0 or self.ask <= self.bid:
            raise ValueError("invalid BBO or numeric data")
        if self.bid_depth_usd < 0 or self.ask_depth_usd < 0 or self.fee_bps_per_side < 0:
            raise ValueError("negative depth or fee")
        if self.kind not in ("SPOT", "PERP"):
            raise ValueError("invalid instrument kind")
        if self.kind == "PERP" and (self.funding_interval_hours is None
                                     or self.funding_interval_hours <= 0):
            raise ValueError("perpetual needs verified funding interval")

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2

    @property
    def spread_bps(self) -> float:
        return (self.ask - self.bid) / self.mid * 10000


@dataclass(frozen=True)
class ScanConfig:
    matched_notional_usd: float = 75.0
    holding_hours: float = 24.0
    max_age_seconds: float = 2.0
    max_cross_venue_skew_seconds: float = 0.25
    slippage_bps_per_transaction: float = 2.0
    emergency_buffer_bps: float = 10.0
    collateral_buffer_ratio: float = 0.1
    ttl_seconds: float = 2.0


@dataclass(frozen=True)
class ScanResult:
    opportunities: tuple[Opportunity, ...]
    rejections: tuple[str, ...]


def _funding_per_settlement(q: Quote) -> float | None:
    history = q.settled_funding
    if q.kind != "PERP" or len(history) < 6 or q.funding_interval_hours is None:
        return None
    if funding_persistence_score(list(history)).status != "OK":
        return None
    a = statistics.fmean(history[-3:])
    b = statistics.fmean(history[-6:])
    hourly = conservative_expected_funding_bps_per_hour(a, b, q.funding_interval_hours)
    return hourly * q.funding_interval_hours / 10000


def _settlements(q: Quote, now: float, hold_hours: float) -> int:
    if q.next_funding_time is None or q.funding_interval_hours is None:
        return 0
    end = now + hold_hours * 3600
    if q.next_funding_time < now or q.next_funding_time > end:
        return 0
    return 1 + int((end - q.next_funding_time) // (q.funding_interval_hours * 3600))


class OpportunityScanner:
    """Produces research opportunities; SENTRY blocks all unpromoted families.

    The scanner has no execution method. The shadow ledger does not mirror the
    Nautilus portfolio and cannot reserve real PAPER capital.
    """

    def __init__(self, config: ScanConfig | None = None) -> None:
        self.config = config or ScanConfig()
        if self.config.matched_notional_usd <= 0 or self.config.holding_hours <= 0:
            raise ValueError("invalid scanner size or horizon")

    def _valid(self, quotes: tuple[Quote, Quote], now: float) -> str | None:
        a, b = quotes
        cfg = self.config
        if a.instrument.split("_")[0] != b.instrument.split("_")[0]:
            return "INSTRUMENT_MISMATCH"
        if any(now < q.local_receive_time or now - q.local_receive_time > cfg.max_age_seconds
               for q in quotes):
            return "STALE_OR_FUTURE_QUOTE"
        if any(q.event_time is None for q in quotes):
            return "EXCHANGE_EVENT_TIME_MISSING"
        if any(now < (q.event_time or 0) or now - (q.event_time or 0) > cfg.max_age_seconds
               for q in quotes):
            return "STALE_OR_FUTURE_EXCHANGE_EVENT"
        if abs((a.event_time or 0) - (b.event_time or 0)) > cfg.max_cross_venue_skew_seconds:
            return "CROSS_VENUE_TIMESTAMP_SKEW"
        if any(q.bid_depth_usd < cfg.matched_notional_usd
               or q.ask_depth_usd < cfg.matched_notional_usd for q in quotes):
            return "DEPTH_UNAVAILABLE_OR_INSUFFICIENT"
        if any(q.min_notional_usd > cfg.matched_notional_usd for q in quotes):
            return "CAPITAL_TOO_SMALL"
        return None

    def _build(self, family: Family, a: Quote, b: Quote, now: float,
               gross_bps: float, sides: tuple[Side, Side]) -> Opportunity:
        cfg = self.config
        costs = CostBreakdown(
            entry_fees=a.fee_bps_per_side + b.fee_bps_per_side,
            exit_fees=a.fee_bps_per_side + b.fee_bps_per_side,
            entry_spread=(a.spread_bps + b.spread_bps) / 2,
            exit_spread=(a.spread_bps + b.spread_bps) / 2,
            entry_slippage=2 * cfg.slippage_bps_per_transaction,
            exit_slippage=2 * cfg.slippage_bps_per_transaction,
            emergency_forced_unwind=cfg.emergency_buffer_bps,
        )
        size = cfg.matched_notional_usd
        legs = (Leg(a.venue, a.instrument, sides[0], size / a.mid, a.mid),
                Leg(b.venue, b.instrument, sides[1], size / b.mid, b.mid))
        identity = f"{family.value}|{a.venue}|{a.instrument}|{b.venue}|{b.instrument}|{now}"
        return Opportunity(
            opportunity_id=hashlib.sha256(identity.encode()).hexdigest()[:24],
            family=family, strategy_version="SHADOW_V1", parameter_version="SCAN_V1",
            discovered_at=now, valid_until=now + cfg.ttl_seconds, legs=legs,
            gross_expected_edge_bps=gross_bps, costs=costs, notional_usd=size,
            required_capital=size * (2 + cfg.collateral_buffer_ratio),
            expected_holding_seconds=cfg.holding_hours * 3600,
            directional_delta_usd=legs[0].signed_notional + legs[1].signed_notional,
            gross_exposure_usd=2 * size, liquidity_score=0.75,
            execution_quality=0.0, data_quality=1.0, evidence_score=0.0,
            estimated_max_loss=size * 0.05,
            lifecycle=Lifecycle.OBSERVING,
            cross_venue_timestamp_skew_ms=abs((a.event_time or 0) - (b.event_time or 0)) * 1000,
            risks={"basis": 1.0, "venue": 1.0, "execution": 1.0, "funding": 1.0},
        )

    def scan(self, quotes: list[Quote], ctx: SentryContext) -> ScanResult:
        opportunities: list[Opportunity] = []
        rejections: list[str] = []
        for i, a in enumerate(quotes):
            for b in quotes[i + 1:]:
                if a.instrument.split("_")[0] != b.instrument.split("_")[0]:
                    continue
                reason = self._valid((a, b), ctx.now)
                if reason:
                    rejections.append(f"{a.venue}:{a.kind}/{b.venue}:{b.kind}:{reason}")
                    continue
                if a.kind == "SPOT" and b.kind == "PERP" and a.venue == b.venue:
                    funding = _funding_per_settlement(b)
                    count = _settlements(b, ctx.now, self.config.holding_hours)
                    if funding is None or count == 0 or funding <= 0:
                        rejections.append("FUNDING_CARRY:INSUFFICIENT_POSITIVE_SETTLED_FUNDING")
                        continue
                    gross = funding * count * 10000
                    opportunities.append(self._build(Family.FUNDING_CARRY, a, b, ctx.now,
                                                     gross, (Side.LONG, Side.SHORT)))
                elif a.kind == "PERP" and b.kind == "PERP" and a.venue != b.venue:
                    rate_a, rate_b = _funding_per_settlement(a), _funding_per_settlement(b)
                    na = _settlements(a, ctx.now, self.config.holding_hours)
                    nb = _settlements(b, ctx.now, self.config.holding_hours)
                    if rate_a is not None and rate_b is not None and na and nb:
                        advantage = rate_a * na - rate_b * nb
                        sides = (Side.SHORT, Side.LONG) if advantage >= 0 else (
                            Side.LONG, Side.SHORT)
                        opportunities.append(self._build(
                            Family.CROSS_EXCHANGE_FUNDING, a, b, ctx.now,
                            abs(advantage) * 10000, sides))
                    else:
                        rejections.append("CROSS_EXCHANGE_FUNDING:FUNDING_HISTORY_OR_SCHEDULE_MISSING")
                    # A price difference alone is not a convergence forecast. No
                    # positive basis edge is invented from the current BBO.
                    rejections.append("CROSS_EXCHANGE_BASIS:CONVERGENCE_NOT_VALIDATED")
        for opp in opportunities:
            evaluate(opp, ctx)
        return ScanResult(tuple(opportunities), tuple(rejections))
