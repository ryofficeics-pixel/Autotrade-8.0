"""Causal volume zones. A fractal is published only after its right bars close."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Sequence


@dataclass(frozen=True)
class Bar:
    close_time: int
    high: float
    low: float
    open: float
    close: float
    volume: float


@dataclass(frozen=True)
class Zone:
    zone_created_at: int
    zone_confirmed_at: int
    zone_low: float
    zone_high: float
    zone_type: str
    source_timeframe: str
    relative_volume: float
    touch_count: int = 0
    break_count: int = 0
    age: int = 0


def confirmed_zones(bars: Sequence[Bar], *, left: int = 3, right: int = 3,
                    min_relative_volume: float = 1.5, timeframe: str = "1h") -> tuple[Zone, ...]:
    if left < 1 or right < 1 or min_relative_volume <= 0:
        raise ValueError("invalid causal fractal parameters")
    if any(b.close_time <= a.close_time for a, b in zip(bars, bars[1:])):
        raise ValueError("bars must have strictly increasing close times")
    output: list[Zone] = []
    for i in range(left, len(bars) - right):
        bar = bars[i]
        reference = median(b.volume for b in bars[i - left:i])
        if reference <= 0 or bar.volume < reference * min_relative_volume:
            continue
        before = bars[i - left:i]
        after = bars[i + 1:i + right + 1]
        high = all(bar.high > b.high for b in (*before, *after))
        low = all(bar.low < b.low for b in (*before, *after))
        if high:
            output.append(Zone(bar.close_time, bars[i + right].close_time,
                               max(bar.open, bar.close), bar.high, "SUPPLY",
                               timeframe, bar.volume / reference))
        if low:
            output.append(Zone(bar.close_time, bars[i + right].close_time,
                               bar.low, min(bar.open, bar.close), "DEMAND",
                               timeframe, bar.volume / reference))
    return tuple(output)


def visible_zones(zones: Sequence[Zone], at_close_time: int) -> tuple[Zone, ...]:
    return tuple(z for z in zones if z.zone_confirmed_at <= at_close_time)
