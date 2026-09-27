import unittest
from decimal import Decimal

from autotrade8.market import BookEvent, BookMonitor, BookStatus, Level


class Clock:
    utc = 1_000_000_000_000
    mono = 5_000_000_000


class BookTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.book = BookMonitor("BTC-USDT-PERP", max_age_ns=100_000_000,
                                max_clock_skew_ns=20_000_000,
                                clock_utc_ns=lambda: self.clock.utc,
                                clock_monotonic_ns=lambda: self.clock.mono)

    def event(self, seq=1, epoch=0, snapshot=True, bids=None, asks=None):
        return BookEvent(1, "BTC-USDT-PERP", epoch, seq, self.clock.utc,
                         self.clock.utc, self.clock.mono,
                         tuple(bids if bids is not None else [Level(Decimal("100"), Decimal("2"))]),
                         tuple(asks if asks is not None else [Level(Decimal("101"), Decimal("3"))]),
                         snapshot)

    def test_warming_snapshot_delta_and_delete(self):
        self.assertFalse(self.book.health().entry_allowed)
        self.assertTrue(self.book.apply(self.event()).entry_allowed)
        update = self.event(2, snapshot=False, bids=[Level(Decimal("100"), Decimal(0)),
                                                    Level(Decimal("99"), Decimal(4))], asks=[])
        health = self.book.apply(update)
        self.assertTrue(health.entry_allowed)
        self.assertEqual(health.best_bid, Decimal(99))

    def test_gap_invalidates_until_newer_snapshot(self):
        self.book.apply(self.event())
        self.assertEqual(self.book.apply(self.event(3, snapshot=False)).reason, "DATA_SEQUENCE_GAP")
        self.assertFalse(self.book.apply(self.event(4, snapshot=False)).entry_allowed)
        self.assertTrue(self.book.apply(self.event(4)).entry_allowed)

    def test_duplicate_crossed_and_empty_fail_closed(self):
        self.book.apply(self.event())
        self.assertEqual(self.book.apply(self.event(1, snapshot=False)).reason, "DATA_DUPLICATE_OR_LATE")
        self.assertEqual(self.book.apply(self.event(2, bids=[Level(Decimal(102), Decimal(1))])).reason,
                         "DATA_EMPTY_OR_CROSSED_BOOK")
        self.assertEqual(self.book.apply(self.event(3, bids=[])).status, BookStatus.INVALID)

    def test_stale_and_wall_clock_rollback(self):
        self.book.apply(self.event())
        self.clock.mono += 100_000_001
        self.clock.utc += 100_000_001
        self.assertEqual(self.book.health().reason, "DATA_STALE")
        self.assertTrue(self.book.apply(self.event(2)).entry_allowed)
        self.clock.utc -= 50_000_000
        self.assertEqual(self.book.health().reason, "DATA_CLOCK_SKEW")

    def test_epoch_requires_snapshot_and_recovery(self):
        self.book.apply(self.event())
        self.assertEqual(self.book.apply(self.event(2, epoch=1, snapshot=False)).reason,
                         "DATA_NEW_EPOCH_NEEDS_SNAPSHOT")
        self.assertTrue(self.book.apply(self.event(2, epoch=1)).entry_allowed)
        self.assertFalse(self.book.apply(self.event(3, epoch=0)).entry_allowed)

    def test_validation_and_future_arrival(self):
        with self.assertRaises(ValueError):
            Level(Decimal("NaN"), Decimal(1))
        with self.assertRaises(ValueError):
            self.event(bids=[Level(Decimal(100), Decimal(1)), Level(Decimal(100), Decimal(2))])
        future = BookEvent(1, "BTC-USDT-PERP", 0, 1, self.clock.utc,
                           self.clock.utc, self.clock.mono + 1, (Level(Decimal(100), Decimal(1)),),
                           (Level(Decimal(101), Decimal(1)),), True)
        self.assertEqual(self.book.apply(future).reason, "DATA_STALE")


if __name__ == "__main__":
    unittest.main()
