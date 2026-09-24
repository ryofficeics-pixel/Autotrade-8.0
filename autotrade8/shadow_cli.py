"""Run a read-only abstention decision from an observed public capture.

Raw responses cannot enter the scanner until event clocks, multipliers, book
units, funding interval and fee tiers are validated by a separate normalizer.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import deque
from pathlib import Path

from .allocator import CapitalAllocator, CapitalLedger
from .scanner import OpportunityScanner
from .sentry import SentryContext


def inspect_capture(path: Path, *, reference_capital_usd: float) -> dict[str, object]:
    if reference_capital_usd <= 0:
        raise ValueError("reference capital must be positive")
    with path.open("rb") as stream:
        last = deque((row for row in stream if row.strip()), maxlen=1)
        line = last[0] if last else None
    if line is None:
        raise ValueError("capture is empty")
    record = json.loads(line)
    if record.get("schema") != "PUBLIC_FORWARD_CAPTURE_V1" or record.get("mode") != "SHADOW":
        raise ValueError("capture identity is invalid")
    feeds = record.get("feeds")
    if not isinstance(feeds, dict):
        raise ValueError("capture has no feed status")
    statuses = {name: str(value.get("status")) for name, value in feeds.items()
                if isinstance(value, dict)}
    reason = ("PUBLIC_FEEDS_UNAVAILABLE" if not any(v == "OK" for v in statuses.values())
              else "NORMALIZER_NOT_VALIDATED")
    now = time.time()
    # No raw API payload is allowed into the normalized scanner.
    scanned = OpportunityScanner().scan([], SentryContext(now, reference_capital_usd,
                                                         reference_capital_usd))
    allocator = CapitalAllocator(CapitalLedger(reference_capital_usd))
    decision = allocator.decide(list(scanned.opportunities),
                                SentryContext(now, reference_capital_usd,
                                              reference_capital_usd))
    return {"mode": "SHADOW", "live": "DISABLED", "paper_execution": "DISABLED",
            "account_equity": None, "reference_capital_usd": reference_capital_usd,
            "capture_time": record.get("captured_at"), "feeds": statuses,
            "normalized_opportunities": len(scanned.opportunities),
            "qualified_alpha_families": 0, "paper_eligible": 0,
            "allocation": "CASH" if decision.action == "CASH" else "BLOCKED",
            "first_rejection_reason": reason,
            "limitations": "No verified exchange event clock, executable VWAP or OOS alpha"}


def main() -> None:
    parser = argparse.ArgumentParser(description="AUTOTRADE 8 read-only shadow decision")
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--reference-capital", type=float, default=300.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    state = inspect_capture(args.capture, reference_capital_usd=args.reference_capital)
    result = json.dumps(state, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    print(result, end="")


if __name__ == "__main__":
    main()
