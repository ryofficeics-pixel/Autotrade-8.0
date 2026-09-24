from __future__ import annotations

import statistics
from dataclasses import dataclass

MIN_PERSISTENCE_SAMPLES = 6


def hourly_rate(rate: float, interval_hours: float) -> float:
    """Normalize a per-settlement funding rate (fraction) to per-hour."""
    if interval_hours <= 0:
        raise ValueError("interval_hours must be > 0")
    return rate / interval_hours


def indicative_annualized_rate(rate: float, interval_hours: float) -> float:
    """INDICATIVE_ANNUALIZED_RATE: single print extrapolated. Not an expectation."""
    return hourly_rate(rate, interval_hours) * 24.0 * 365.0


def cross_exchange_funding_edge_bps(
    rate_a: float, interval_a_h: float, rate_b: float, interval_b_h: float, hold_hours: float
) -> tuple[float, str]:
    """Gross funding differential (bps) over hold, orientation chosen automatically.

    Positive funding = longs pay shorts. Short the higher-hourly-funding venue,
    long the lower. Returns (edge_bps >= 0, 'SHORT_A' | 'SHORT_B').
    """
    diff = hourly_rate(rate_a, interval_a_h) - hourly_rate(rate_b, interval_b_h)
    side = "SHORT_A" if diff >= 0 else "SHORT_B"
    return abs(diff) * hold_hours * 1e4, side


@dataclass(frozen=True)
class Persistence:
    score: float | None  # None => INSUFFICIENT_EVIDENCE
    sign_persistence: float | None
    stability: float | None
    n: int
    status: str


def funding_persistence_score(history: list[float]) -> Persistence:
    """FUNDING_PERSISTENCE_SCORE v1 (deterministic).

    sign_persistence = share of prints with the sign of the mean
    stability        = |mean| / (|mean| + stdev)
    score            = sign_persistence * stability
    """
    n = len(history)
    if n < MIN_PERSISTENCE_SAMPLES:
        return Persistence(None, None, None, n, "INSUFFICIENT_EVIDENCE")
    mean = statistics.fmean(history)
    if mean == 0:
        return Persistence(0.0, 0.0, 0.0, n, "OK")
    sign = 1 if mean > 0 else -1
    sp = sum(1 for x in history if x * sign > 0) / n
    sd = statistics.pstdev(history)
    stab = abs(mean) / (abs(mean) + sd)
    return Persistence(sp * stab, sp, stab, n, "OK")


def conservative_expected_funding_bps_per_hour(
    mean_3: float, mean_6: float, interval_hours: float
) -> float:
    """Smaller-magnitude of the 3- and 6-settlement means, same sign only, else 0."""
    if mean_3 * mean_6 <= 0:
        return 0.0
    m = mean_3 if abs(mean_3) < abs(mean_6) else mean_6
    return hourly_rate(m, interval_hours) * 1e4


def expected_net_carry_bps(
    expected_funding_bps: float,
    expected_basis_convergence_bps: float,
    entry_cost_bps: float,
    holding_cost_bps: float,
    exit_cost_bps: float,
    risk_buffer_bps: float,
) -> float:
    return (
        expected_funding_bps + expected_basis_convergence_bps
        - entry_cost_bps - holding_cost_bps - exit_cost_bps - risk_buffer_bps
    )
