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
    line = _capture_line(result)
    with path.open("ab") as stream:
        stream.write(line)
        stream.flush()
        os.fsync(stream.fileno())


def _capture_line(result: dict[str, object]) -> bytes:
    return (json.dumps(result, sort_keys=True, separators=(",", ":"),
                       allow_nan=False).encode() + b"\n")


class CaptureLimitError(RuntimeError):
    """The read-only capture has reached its storage budget."""


def append_capture_bounded(directory: Path, result: dict[str, object], *,
                           segment_bytes: int, total_bytes: int) -> Path:
    """Append one complete record to a UTC-day segment, or stop before a disk cap.

    Existing segments are never truncated or removed. A restarted collector counts
    their sizes before accepting new data. This cap applies only to files created
    by this collector in the requested directory.
    """
    line = _capture_line(result)
    if segment_bytes <= 0 or total_bytes <= 0 or len(line) > segment_bytes:
        raise CaptureLimitError("CAPTURE_RECORD_EXCEEDS_SEGMENT_LIMIT")
    directory.mkdir(parents=True, exist_ok=True)
    segments = list(directory.glob("capture-????????-???.jsonl"))
    occupied = sum(path.stat().st_size for path in segments)
    if occupied + len(line) > total_bytes:
        raise CaptureLimitError("CAPTURE_TOTAL_STORAGE_LIMIT")
    prefix = f"capture-{datetime.now(UTC):%Y%m%d}-"
    for index in range(1000):
        path = directory / f"{prefix}{index:03d}.jsonl"
        if not path.exists() or path.stat().st_size + len(line) <= segment_bytes:
            append_capture(path, result)
            return path
    raise CaptureLimitError("CAPTURE_DAILY_SEGMENT_LIMIT")


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only raw public market capture")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--output", type=Path, help="single-file capture, requires --once")
    target.add_argument("--output-dir", type=Path, help="bounded rolling capture")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval-seconds", type=float, default=60.0)
    parser.add_argument("--timeout-seconds", type=float, default=5.0)
    parser.add_argument("--max-segment-mib", type=int, default=64)
    parser.add_argument("--max-total-mib", type=int, default=1024)
    args = parser.parse_args()
    if args.interval_seconds < 30 or not 0 < args.timeout_seconds <= 30:
        parser.error("interval >= 30 seconds and 0 < timeout <= 30 seconds required")
    if args.output is not None and not args.once:
        parser.error("continuous capture requires --output-dir for bounded storage")
    if not 0 < args.max_segment_mib <= args.max_total_mib:
        parser.error("0 < max-segment-mib <= max-total-mib required")
    while True:
        record = collect_once(timeout_seconds=args.timeout_seconds)
        if args.output_dir is not None:
            try:
                path = append_capture_bounded(
                    args.output_dir, record, segment_bytes=args.max_segment_mib * 1024**2,
                    total_bytes=args.max_total_mib * 1024**2)
            except CaptureLimitError as exc:
                parser.exit(2, f"Capture stopped: {exc}. Preserve the files and raise the cap "
                            "only after reviewing disk capacity.\n")
        else:
            path = args.output
            append_capture(path, record)
        statuses = {name: row["status"] for name, row in record["feeds"].items()}
        print(json.dumps({"captured_at": record["captured_at"], "statuses": statuses,
                          "file": str(path), "orders": "DISABLED"}), flush=True)
        if args.once:
            return
        time.sleep(args.interval_seconds)


if __name__ == "__main__":
    main()
