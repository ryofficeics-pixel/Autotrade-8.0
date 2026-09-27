"""Local, read-only L2 replay inspector. Run: python -m autotrade8.app."""

from __future__ import annotations

import argparse
from dataclasses import asdict
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from typing import Any

from .market import BookEvent, BookMonitor, Level


MAX_FILE_BYTES = 16 * 1024 * 1024
SAMPLE = [
    {"schema_version": 1, "instrument_id": "SAMPLE-USDT-PERP", "connection_epoch": 1,
     "sequence": 100, "exchange_ts_ns": 1_000_000_000_000, "receive_utc_ns": 1_000_000_000_000,
     "receive_monotonic_ns": 5_000_000_000, "is_snapshot": True,
     "bids": [["100.00", "2.0"]], "asks": [["100.05", "1.5"]]},
    {"schema_version": 1, "instrument_id": "SAMPLE-USDT-PERP", "connection_epoch": 1,
     "sequence": 101, "exchange_ts_ns": 1_000_010_000_000, "receive_utc_ns": 1_000_010_000_000,
     "receive_monotonic_ns": 5_010_000_000, "is_snapshot": False,
     "bids": [["100.01", "1.0"]], "asks": []},
    {"schema_version": 1, "instrument_id": "SAMPLE-USDT-PERP", "connection_epoch": 1,
     "sequence": 103, "exchange_ts_ns": 1_000_020_000_000, "receive_utc_ns": 1_000_020_000_000,
     "receive_monotonic_ns": 5_020_000_000, "is_snapshot": False,
     "bids": [["100.02", "1.0"]], "asks": []},
]

HTML = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Autotrade 8 · Market Truth</title><style>
body{margin:0;background:#0b1520;color:#ecf3fa;font:16px system-ui}main{max-width:900px;margin:40px auto;padding:0 20px}
h1{font-size:2rem;margin-bottom:4px}.note{color:#a8bdd0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:24px 0}
.card{background:#162535;border:1px solid #30485c;border-radius:12px;padding:18px}.card strong{display:block;font-size:1.3rem;margin-top:8px}
.blocked{color:#ffba9e}.valid{color:#91e5b9}table{width:100%;border-collapse:collapse;background:#162535}th,td{text-align:left;padding:11px;border-bottom:1px solid #30485c}th{color:#a8bdd0}code{color:#b7d9ff}
</style><main><h1>Autotrade 8 · Market Truth</h1><p class="note">Local replay inspector · Observe only · PAPER architecture · No orders or profit claims</p>
<p id="source" class="note">Loading…</p><div class="grid"><div class="card">Final book<strong id="status">—</strong></div>
<div class="card">Entry gate<strong id="gate">—</strong></div><div class="card">Events<strong id="total">—</strong></div>
<div class="card">Detected failures<strong id="failures">—</strong></div></div>
<h2>Event timeline</h2><table><thead><tr><th>#</th><th>Sequence</th><th>Epoch</th><th>Status</th><th>Reason</th><th>Bid / Ask</th></tr></thead><tbody id="rows"></tbody></table>
<p class="note">A valid L2 book does not authorize trading. Account, cost, risk, audit and manual arm gates are not implemented.</p></main><script>
fetch('/api/report').then(r=>r.json()).then(data=>{
 const set=(id,value)=>{document.getElementById(id).textContent=String(value)};
 set('source',data.source+' · '+data.instrument_id);set('status',data.final_status);
 set('gate',data.entry_allowed?'L2 VALID ONLY':'BLOCKED');set('total',data.events.length);
 set('failures',data.events.filter(e=>!e.entry_allowed).length);
 document.getElementById('gate').className=data.entry_allowed?'valid':'blocked';
 const root=document.getElementById('rows');data.events.forEach((e,i)=>{
   const row=document.createElement('tr');[i+1,e.sequence,e.epoch,e.status,e.reason,
     (e.best_bid??'—')+' / '+(e.best_ask??'—')].forEach(x=>{
       const cell=document.createElement('td');cell.textContent=String(x);row.appendChild(cell)});root.appendChild(row)
 })
}).catch(err=>{document.getElementById('source').textContent='Unable to load report: '+err.message});
</script></html>"""


def parse_event(data: dict[str, Any]) -> BookEvent:
    expected = {"schema_version", "instrument_id", "connection_epoch", "sequence", "exchange_ts_ns",
                "receive_utc_ns", "receive_monotonic_ns", "is_snapshot", "bids", "asks"}
    if set(data) != expected:
        raise ValueError("missing or unknown event fields")
    for name in ("schema_version", "connection_epoch", "sequence", "exchange_ts_ns",
                 "receive_utc_ns", "receive_monotonic_ns"):
        if type(data[name]) is not int:
            raise ValueError(f"{name} must be an integer")
    if type(data["is_snapshot"]) is not bool or type(data["instrument_id"]) is not str:
        raise ValueError("invalid snapshot flag or instrument")

    def levels(value: Any) -> tuple[Level, ...]:
        if not isinstance(value, list):
            raise ValueError("levels must be arrays")
        if len(value) > 1000:
            raise ValueError("too many levels")
        result = []
        for item in value:
            if not isinstance(item, list) or len(item) != 2 or not all(isinstance(x, str) for x in item):
                raise ValueError("level must contain decimal strings [price, quantity]")
            result.append(Level(Decimal(item[0]), Decimal(item[1])))
        return tuple(result)

    return BookEvent(*(data[name] for name in ("schema_version", "instrument_id", "connection_epoch",
                     "sequence", "exchange_ts_ns", "receive_utc_ns", "receive_monotonic_ns")),
                     levels(data["bids"]), levels(data["asks"]), data["is_snapshot"])


def load_events(path: Path | None) -> tuple[list[BookEvent], str]:
    if path is None:
        return [parse_event(e) for e in SAMPLE], "SYNTHETIC SAMPLE (not exchange data)"
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("input exceeds 16 MiB; use a bounded replay fixture")
    events = []
    with path.open(encoding="utf-8") as stream:
        for index, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                events.append(parse_event(json.loads(line)))
            except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
                raise ValueError(f"invalid event at line {index}: {error}") from error
    if not events:
        raise ValueError("input contains no events")
    return events, f"LOCAL FIXTURE: {path.name} (unverified provenance)"


def build_report(events: list[BookEvent], source: str, *, max_age_ns: int,
                 max_clock_skew_ns: int) -> dict[str, Any]:
    instrument = events[0].instrument_id
    clock = {"utc": events[0].receive_utc_ns, "mono": events[0].receive_monotonic_ns}
    monitor = BookMonitor(instrument, max_age_ns=max_age_ns, max_clock_skew_ns=max_clock_skew_ns,
                          clock_utc_ns=lambda: clock["utc"], clock_monotonic_ns=lambda: clock["mono"])
    results = []
    for event in events:
        # Replay observes arrival order; rolling clocks backwards is an integrity failure.
        clock["utc"] = event.receive_utc_ns
        clock["mono"] = max(clock["mono"], event.receive_monotonic_ns)
        health = monitor.apply(event)
        item = asdict(health)
        item["best_bid"] = str(health.best_bid) if health.best_bid is not None else None
        item["best_ask"] = str(health.best_ask) if health.best_ask is not None else None
        item["entry_allowed"] = health.entry_allowed
        results.append(item)
    final = monitor.health()
    return {"source": source, "instrument_id": instrument, "final_status": final.status.value,
            "entry_allowed": final.entry_allowed, "events": results, "trading_enabled": False}


def serve(report: dict[str, Any], port: int) -> None:
    payload = json.dumps(report, separators=(",", ":")).encode()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/":
                body, content_type = HTML.encode(), "text/html; charset=utf-8"
            elif self.path == "/api/report":
                body, content_type = payload, "application/json; charset=utf-8"
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'")
            self.end_headers()
            self.wfile.write(body)

    with ThreadingHTTPServer(("127.0.0.1", port), Handler) as server:
        print(f"Observe-only replay: http://127.0.0.1:{server.server_port}", flush=True)
        server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Local, read-only market book replay inspector")
    parser.add_argument("--input", type=Path, help="Canonical L2 NDJSON fixture (default: labeled synthetic sample)")
    parser.add_argument("--port", type=int, default=8768)
    parser.add_argument("--max-age-ms", type=int, default=1000)
    parser.add_argument("--max-clock-skew-ms", type=int, default=500)
    parser.add_argument("--summary", action="store_true", help="Print JSON report and exit")
    args = parser.parse_args()
    if args.max_age_ms <= 0 or args.max_clock_skew_ms < 0:
        parser.error("invalid threshold")
    events, source = load_events(args.input)
    report = build_report(events, source, max_age_ns=args.max_age_ms * 1_000_000,
                          max_clock_skew_ns=args.max_clock_skew_ms * 1_000_000)
    if args.summary:
        print(json.dumps(report, indent=2))
    else:
        serve(report, args.port)


if __name__ == "__main__":
    main()
