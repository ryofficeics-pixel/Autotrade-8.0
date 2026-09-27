"""Immutable canonical L2 events and deterministic fail-closed integrity monitor.

Sequence semantics here are *contiguous integer update IDs*. A venue with different
semantics needs its own validated normalizer; do not pass its raw IDs directly.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Callable


class BookStatus(str, Enum):
    WARMING = "WARMING"
    VALID = "VALID"
    INVALID = "INVALID"


@dataclass(frozen=True)
class Level:
    price: Decimal
    quantity: Decimal

    def __post_init__(self) -> None:
        if not self.price.is_finite() or self.price <= 0:
            raise ValueError("price must be finite and positive")
        if not self.quantity.is_finite() or self.quantity < 0:
            raise ValueError("quantity must be finite and nonnegative")


@dataclass(frozen=True)
class BookEvent:
    schema_version: int
    instrument_id: str
    connection_epoch: int
    sequence: int
    exchange_ts_ns: int
    receive_utc_ns: int
    receive_monotonic_ns: int
    bids: tuple[Level, ...]
    asks: tuple[Level, ...]
    is_snapshot: bool
    # Venue normalizer verifies sequence and makes one canonical delta per update ID.

    def __post_init__(self) -> None:
        if self.schema_version != 1 or not self.instrument_id:
            raise ValueError("unsupported schema or missing instrument")
        if min(self.connection_epoch, self.sequence, self.exchange_ts_ns,
               self.receive_utc_ns, self.receive_monotonic_ns) < 0:
            raise ValueError("timestamps, epoch and sequence must be nonnegative")
        if not self.is_snapshot and not self.bids and not self.asks:
            raise ValueError("empty delta")
        if len({x.price for x in self.bids}) != len(self.bids) or len({x.price for x in self.asks}) != len(self.asks):
            raise ValueError("duplicate price in event")
        if self.is_snapshot and any(x.quantity == 0 for x in self.bids + self.asks):
            raise ValueError("snapshot contains zero quantity")


@dataclass(frozen=True)
class BookHealth:
    status: BookStatus
    reason: str
    sequence: int | None
    epoch: int | None
    age_ns: int | None
    best_bid: Decimal | None
    best_ask: Decimal | None

    @property
    def entry_allowed(self) -> bool:
        return self.status == BookStatus.VALID


class BookMonitor:
    """One instrument per instance. No implicit resync or hidden gap repair.

    Consumers must persist raw data and audit decisions independently. This
    monitor never declares the whole account tradable; it grades only one book.
    """

    def __init__(self, instrument_id: str, *, max_age_ns: int, max_clock_skew_ns: int,
                 clock_utc_ns: Callable[[], int], clock_monotonic_ns: Callable[[], int]) -> None:
        if not instrument_id or max_age_ns <= 0 or max_clock_skew_ns < 0:
            raise ValueError("invalid monitor configuration")
        self.instrument_id = instrument_id
        self.max_age_ns = max_age_ns
        self.max_clock_skew_ns = max_clock_skew_ns
        self.clock_utc_ns = clock_utc_ns
        self.clock_monotonic_ns = clock_monotonic_ns
        self.status = BookStatus.WARMING
        self.reason = "DATA_NO_SNAPSHOT"
        self.sequence: int | None = None
        self.epoch: int | None = None
        self.last_receive_monotonic_ns: int | None = None
        self.last_receive_utc_ns: int | None = None
        self.bids: dict[Decimal, Decimal] = {}
        self.asks: dict[Decimal, Decimal] = {}

    def _invalidate(self, reason: str) -> BookHealth:
        self.status = BookStatus.INVALID
        self.reason = reason
        self.bids.clear()
        self.asks.clear()
        return self.health()

    def health(self) -> BookHealth:
        now_mono = self.clock_monotonic_ns()
        now_utc = self.clock_utc_ns()
        age = None if self.last_receive_monotonic_ns is None else now_mono - self.last_receive_monotonic_ns
        if self.status == BookStatus.VALID:
            if age is None or age < 0:
                return self._invalidate("DATA_MONOTONIC_ROLLBACK")
            if age > self.max_age_ns:
                return self._invalidate("DATA_STALE")
            if self.last_receive_utc_ns is None or abs(now_utc - (self.last_receive_utc_ns + age)) > self.max_clock_skew_ns:
                return self._invalidate("DATA_CLOCK_SKEW")
        return BookHealth(self.status, self.reason, self.sequence, self.epoch, age,
                          max(self.bids) if self.bids else None,
                          min(self.asks) if self.asks else None)

    def apply(self, event: BookEvent) -> BookHealth:
        if event.instrument_id != self.instrument_id:
            return self._invalidate("DATA_INSTRUMENT_MISMATCH")
        # The local clock is injected: never trust event-supplied arrival time alone.
        now_mono, now_utc = self.clock_monotonic_ns(), self.clock_utc_ns()
        if event.receive_monotonic_ns > now_mono or now_mono - event.receive_monotonic_ns > self.max_age_ns:
            return self._invalidate("DATA_STALE")
        if self.last_receive_monotonic_ns is not None and event.receive_monotonic_ns < self.last_receive_monotonic_ns:
            return self._invalidate("DATA_MONOTONIC_ROLLBACK")
        if abs(now_utc - event.receive_utc_ns) > self.max_clock_skew_ns or abs(event.exchange_ts_ns - event.receive_utc_ns) > self.max_clock_skew_ns:
            return self._invalidate("DATA_CLOCK_SKEW")
        if self.epoch is not None and event.connection_epoch < self.epoch:
            return self._invalidate("DATA_OLD_EPOCH")
        if event.is_snapshot:
            # A new epoch requires a fresh snapshot; an older snapshot in the
            # same epoch cannot roll a healthy book backwards.
            if self.epoch == event.connection_epoch and self.sequence is not None and event.sequence <= self.sequence:
                return self._invalidate("DATA_OUT_OF_ORDER")
            bids = {x.price: x.quantity for x in event.bids}
            asks = {x.price: x.quantity for x in event.asks}
        else:
            if self.epoch != event.connection_epoch:
                return self._invalidate("DATA_NEW_EPOCH_NEEDS_SNAPSHOT")
            if self.status != BookStatus.VALID or self.sequence is None:
                return self._invalidate("DATA_NO_SNAPSHOT")
            if event.sequence <= self.sequence:
                return self._invalidate("DATA_DUPLICATE_OR_LATE")
            if event.sequence != self.sequence + 1:
                return self._invalidate("DATA_SEQUENCE_GAP")
            bids, asks = self.bids.copy(), self.asks.copy()
            for updates, side in ((event.bids, bids), (event.asks, asks)):
                for level in updates:
                    if level.quantity == 0:
                        side.pop(level.price, None)
                    else:
                        side[level.price] = level.quantity
        if not bids or not asks or max(bids) >= min(asks):
            return self._invalidate("DATA_EMPTY_OR_CROSSED_BOOK")
        self.bids, self.asks = bids, asks
        self.sequence, self.epoch = event.sequence, event.connection_epoch
        self.last_receive_monotonic_ns = event.receive_monotonic_ns
        self.last_receive_utc_ns = event.receive_utc_ns
        self.status, self.reason = BookStatus.VALID, "DATA_OK"
        return self.health()
