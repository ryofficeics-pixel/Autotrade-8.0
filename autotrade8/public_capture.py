"""Public, read-only forward capture. Raw responses are never converted to fill evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path


PUBLIC_ENDPOINTS = {
    "GATE_PERP_TICKER": ("https://api.gateio.ws/api/v4/futures/usdt/tickers", {"contract": "BTC_USDT"}),
    "GATE_PERP_CONTRACT": ("https://api.gateio.ws/api/v4/futures/usdt/contracts/BTC_USDT", {}),
    "GATE_PERP_FUNDING": ("https://api.gateio.ws/api/v4/futures/usdt/funding_rate", {"contract": "BTC_USDT", "limit": "12"}),
    "GATE_PERP_BOOK": ("https://api.gateio.ws/api/v4/futures/usdt/order_book", {"contract": "BTC_USDT", "limit": "10"}),
    "GATE_SPOT_BOOK": ("https://api.gateio.ws/api/v4/spot/order_book", {"currency_pair": "BTC_USDT", "limit": "10"}),
    "BINANCE_PERP_MARK": ("https://fapi.binance.com/fapi/v1/premiumIndex", {"symbol": "BTCUSDT"}),
    "BINANCE_PERP_FUNDING": ("https://fapi.binance.com/fapi/v1/fundingRate", {"symbol": "BTCUSDT", "limit": "12"}),
    "BINANCE_PERP_BOOK": ("https://fapi.binance.com/fapi/v1/depth", {"symbol": "BTCUSDT", "limit": "10"}),
}


def collect_once(*, timeout_seconds: float = 5.0) -> dict[str, object]:
    """Record receive clocks separately; absent exchange event timestamps stay absent."""
    feeds: dict[str, object] = {}
    for name, (url, params) in PUBLIC_ENDPOINTS.items():
        request = urllib.request.Request(
            url + "?" + urllib.parse.urlencode(params),
            headers={"User-Agent": "AUTOTRADE-8-SHADOW-RESEARCH/1", "Accept": "application/json"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310
                if response.status != 200:
                    raise ValueError(f"HTTP_{response.status}")
                body = response.read(2_000_001)
            if len(body) > 2_000_000:
                raise ValueError("RESPONSE_TOO_LARGE")
            payload = json.loads(body)
            feeds[name] = {"status": "OK", "payload": payload,
                           "sha256": hashlib.sha256(body).hexdigest(),
                           "local_receive_time": time.time(),
                           "local_monotonic_time": time.monotonic(),
                           "exchange_event_time": None,
                           "limitation": "Raw endpoint response; timestamp semantics unverified"}
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            feeds[name] = {"status": "UNAVAILABLE", "reason": type(exc).__name__,
                           "local_receive_time": time.time()}
    return {"schema": "PUBLIC_FORWARD_CAPTURE_V1", "mode": "SHADOW",
            "live_orders_enabled": False, "captured_at": datetime.now(UTC).isoformat(),
            "feeds": feeds}


def append_capture(path: Path, result: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(result, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode() + b"\n"
    with path.open("ab") as stream:
        stream.write(line)
        stream.flush()
        os.fsync(stream.fileno())


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only raw public market capture")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval-seconds", type=float, default=60.0)
    parser.add_argument("--timeout-seconds", type=float, default=5.0)
    args = parser.parse_args()
    if args.interval_seconds < 30 or not 0 < args.timeout_seconds <= 30:
        parser.error("interval >= 30 seconds and 0 < timeout <= 30 seconds required")
    while True:
        record = collect_once(timeout_seconds=args.timeout_seconds)
        append_capture(args.output, record)
        statuses = {name: row["status"] for name, row in record["feeds"].items()}
        print(json.dumps({"captured_at": record["captured_at"], "statuses": statuses,
                          "orders": "DISABLED"}))
        if args.once:
            return
        time.sleep(args.interval_seconds)


if __name__ == "__main__":
    main()
