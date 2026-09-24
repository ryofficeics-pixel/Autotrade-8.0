"""Safety regressions runnable without the optional Nautilus/pytest toolchain."""

import math
import unittest

from autotrade8.allocator import CapitalAllocator, CapitalError, CapitalLedger
from autotrade8.event import EventEvidence, HoundEvent, evaluate_shadow
from autotrade8.hedge import BundleState, HedgeAction, IllegalTransition, LegFill, MultiLegBundle
from autotrade8.opportunity import CostBreakdown, Family, Leg, Lifecycle, Opportunity, Side, VenueHealth
from autotrade8.scanner import OpportunityScanner, Quote, ScanConfig
from autotrade8.sentry import SentryContext, evaluate
from autotrade8.zones import Bar, confirmed_zones, visible_zones


def quote(venue="gate", kind="PERP", *, received=100.0, event=100.0,
          history=(0.0008,) * 6, interval=8.0, next_funding=3600.0):
    return Quote(venue, "BTC_USDT", kind, 100.0, 100.1, 200, 200,
                 5, 5, event, None, received, 1.0,
                 interval if kind == "PERP" else None,
                 next_funding if kind == "PERP" else None,
                 history if kind == "PERP" else ())


def context(now=100.5):
    return SentryContext(now, 300, 300, {"gate": VenueHealth.HEALTHY,
                                         "other": VenueHealth.HEALTHY})


class Alpha8SafetyTests(unittest.TestCase):
    def test_carry_is_shadow_and_costed_on_matched_notional(self):
        scanner = OpportunityScanner(ScanConfig(matched_notional_usd=75))
        result = scanner.scan([quote(kind="SPOT"), quote()], context())
        self.assertEqual(len(result.opportunities), 1)
        o = result.opportunities[0]
        self.assertEqual(o.family, Family.FUNDING_CARRY)
        self.assertAlmostEqual(o.gross_expected_edge_bps, 24)  # 3 projected prints at 8 bps each
        self.assertGreater(o.expected_cost_bps, 40)  # four fees, spreads, exit, hedge buffer
        self.assertEqual(o.sentry.state, "BLOCKED")
        self.assertEqual(o.first_rejection_reason, "ALPHA_NOT_PROMOTED:OBSERVING")
        self.assertFalse(o.executable)

    def test_interval_normalization_uses_actual_settlement_schedule(self):
        a = quote(history=(0.0008,) * 6, interval=8, next_funding=3600)
        b = quote("other", history=(0.0001,) * 6, interval=1, next_funding=3600)
        result = OpportunityScanner().scan([a, b], context())
        self.assertEqual(len(result.opportunities), 1)
        self.assertAlmostEqual(result.opportunities[0].gross_expected_edge_bps, 0)

    def test_missing_time_depth_and_funding_fail_closed(self):
        scanner = OpportunityScanner()
        self.assertIn("EXCHANGE_EVENT_TIME_MISSING", scanner.scan([
            quote(kind="SPOT", event=None), quote()], context()).rejections[0])
        self.assertIn("DEPTH_UNAVAILABLE", scanner.scan([
            quote(kind="SPOT"), Quote("gate", "BTC_USDT", "PERP", 100, 100.1,
                                     0, 200, 5, 5, 100, None, 100, 1, 8, 3600,
                                     (0.0008,) * 6)], context()).rejections[0])
        self.assertEqual(scanner.scan([quote(kind="SPOT"), quote(history=())],
                                      context()).opportunities, ())

    def test_cross_venue_stale_skew_and_unvalidated_basis(self):
        scanner = OpportunityScanner()
        self.assertIn("CROSS_VENUE_TIMESTAMP_SKEW", scanner.scan([
            quote(), quote("other", event=100.4)], context()).rejections[0])
        self.assertIn("STALE_OR_FUTURE_QUOTE", scanner.scan([
            quote(), quote("other", received=50)], context()).rejections[0])
        self.assertIn("CROSS_EXCHANGE_BASIS:CONVERGENCE_NOT_VALIDATED",
                      scanner.scan([quote(), quote("other")], context()).rejections)

    def test_invalid_numbers_and_lifecycle_fail_closed(self):
        with self.assertRaises(ValueError):
            Quote("gate", "BTC_USDT", "SPOT", math.nan, 101, 100, 100,
                  5, 5, 100, None, 100, 1)
        with self.assertRaises(ValueError):
            Opportunity("bad", Family.FUNDING_CARRY, "v1", "p1", 100, 101,
                        (Leg("gate", "BTC", Side.LONG, 1, 100),), 100,
                        CostBreakdown(entry_fees=-5), 100, 100, 3600)
        o = Opportunity("test", Family.FUNDING_CARRY, "v1", "p1", 100, 110,
                        (Leg("gate", "BTC_SPOT", Side.LONG, 1, 100),
                         Leg("gate", "BTC_PERP", Side.SHORT, 1, 100)), 100,
                        CostBreakdown(entry_fees=5, exit_fees=5), 100, 200, 3600,
                        gross_exposure_usd=200, data_quality=1, liquidity_score=1,
                        evidence_score=1, lifecycle=Lifecycle.OBSERVING)
        self.assertEqual(evaluate(o, context()).first_rejection_reason,
                         "ALPHA_NOT_PROMOTED:OBSERVING")

    def test_capital_cannot_be_double_reserved(self):
        ledger = CapitalLedger(300)
        ledger.reserve("a", 157.5)
        with self.assertRaises(CapitalError):
            ledger.reserve("b", 157.5)

    def test_allocator_rechecks_sentry_at_decision_and_commit(self):
        o = OpportunityScanner().scan([quote(kind="SPOT"), quote()], context()).opportunities[0]
        o.lifecycle = Lifecycle.PAPER_ACTIVE  # synthetic safety test; scanner never promotes
        o.evidence_score = 1
        o.execution_quality = 1
        o.estimated_max_loss = 1
        o.gross_expected_edge_bps = 200
        allocator = CapitalAllocator(CapitalLedger(300))
        decision = allocator.decide([o], context())
        self.assertEqual(decision.action, "ALLOCATE")
        with self.assertRaises(CapitalError):
            allocator.commit(decision, context(now=103))
        self.assertEqual(allocator.ledger.available, 300)

    def test_one_leg_fill_prompts_immediate_hedge_action(self):
        b = MultiLegBundle("b", [LegFill("gate", Side.LONG, 1, 1, 100, 100),
                                  LegFill("other", Side.SHORT, 1, 0, 0, 100)])
        b.transition(BundleState.RESERVED, 0)
        b.transition(BundleState.SUBMITTING, 1)
        b.transition(BundleState.PARTIALLY_HEDGED, 2)
        self.assertEqual(b.evaluate(2)[0], HedgeAction.RETRY_HEDGE)
        with self.assertRaises(IllegalTransition):
            b.transition(BundleState.HEDGED, 2.1)
        self.assertNotEqual(b.state, BundleState.ACTIVE)

    def test_zone_is_not_visible_before_confirmation(self):
        bars = [Bar(i, h, 5, 6, 7, v) for i, (h, v) in enumerate([
            (8, 10), (9, 10), (10, 10), (20, 50), (11, 10), (8, 10), (7, 10)])]
        zones = confirmed_zones(bars)
        self.assertEqual(len(zones), 1)
        self.assertEqual(zones[0].zone_created_at, 3)
        self.assertEqual(zones[0].zone_confirmed_at, 6)
        self.assertEqual(visible_zones(zones, 5), ())
        self.assertEqual(len(visible_zones(zones, 6)), 1)

    def test_onchain_missing_safety_and_social_fail_closed(self):
        event = HoundEvent("e1", "ethereum", "0x1", 100, "POOL_CREATED", "public_feed")
        d = evaluate_shadow(EventEvidence(event), intended_notional_usd=75)
        self.assertEqual(d.state, "SHADOW_BLOCKED")
        self.assertEqual(d.components["TIDE"], "SOCIAL_DATA_UNAVAILABLE")
        self.assertEqual(d.components["GUARD"], "CONTRACT_SAFETY_UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
