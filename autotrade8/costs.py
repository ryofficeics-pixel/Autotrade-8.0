from __future__ import annotations

from .opportunity import CostBreakdown, Opportunity

MIN_EDGE_COST_RATIO = 3.0
RATIO_NEIGHBORHOOD = (2.5, 3.0, 3.5, 4.0)
CAPITAL_EFFICIENCY_VERSION = "RACE_V1"
_MIN_HOLD_DAYS = 1.0 / 1440.0  # 1 minute floor


def total_expected_cost_bps(costs: CostBreakdown) -> float:
    return costs.total_bps


def expected_net_edge_bps(gross_bps: float, cost_bps: float) -> float:
    return gross_bps - cost_bps


def edge_cost_ratio(gross_bps: float, cost_bps: float) -> float:
    if cost_bps <= 0:
        return float("inf") if gross_bps > 0 else 0.0
    return gross_bps / cost_bps


def min_movement_bps(cost_bps: float, min_ratio: float = MIN_EDGE_COST_RATIO) -> float:
    """Minimum expected realizable move: cost 17 bps @ ratio 3 -> 51 bps."""
    return cost_bps * min_ratio


def ratio_neighborhood(gross_bps: float, cost_bps: float) -> dict[float, bool]:
    """Pass/fail at each neighborhood threshold; demand stability, not the best cell."""
    r = edge_cost_ratio(gross_bps, cost_bps)
    return {t: r >= t for t in RATIO_NEIGHBORHOOD}


def net_return_on_deployed_capital(net_pnl: float, capital: float) -> float:
    return net_pnl / capital if capital > 0 else 0.0


def net_return_per_capital_day(net_pnl: float, capital: float, holding_seconds: float) -> float:
    days = max(holding_seconds / 86400.0, _MIN_HOLD_DAYS)
    return net_return_on_deployed_capital(net_pnl, capital) / days


def risk_adjusted_capital_efficiency(opp: Opportunity) -> float:
    """RACE_V1 in bps per capital-day.

    net return per capital-day x execution reliability / (1 + tail ratio),
    tail ratio = estimated_max_loss / required_capital.
    """
    per_day = net_return_per_capital_day(
        opp.expected_net_pnl, opp.required_capital, opp.expected_holding_seconds
    )
    tail = opp.estimated_max_loss / opp.required_capital if opp.required_capital > 0 else 0.0
    return per_day * 1e4 * max(opp.execution_quality, 0.0) / (1.0 + max(tail, 0.0))
