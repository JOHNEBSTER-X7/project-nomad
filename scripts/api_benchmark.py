#!/usr/bin/env python3
"""Small, opt-in HTTP benchmark for a NOMAD instance; no third-party dependencies."""
import argparse
import json
import statistics
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone


def request_once(url: str, timeout: float) -> dict:
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            response.read()
            return {"ok": 200 <= response.status < 400, "status": response.status,
                    "latency_ms": (time.perf_counter() - started) * 1000, "error": None}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"ok": False, "status": None,
                "latency_ms": (time.perf_counter() - started) * 1000,
                "error": str(exc)[:240]}


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round((len(ordered) - 1) * p)))
    return round(ordered[index], 2)


def run_benchmark(url: str, requests: int = 30, concurrency: int = 2,
                  timeout: float = 10.0, warmup: int = 2) -> dict:
    if requests < 1 or concurrency < 1 or timeout <= 0 or warmup < 0:
        raise ValueError("requests and concurrency must be positive; timeout positive; warmup non-negative")
    for _ in range(warmup):
        request_once(url, timeout)
    started = time.perf_counter()
    results = []
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(request_once, url, timeout) for _ in range(requests)]
        for future in as_completed(futures):
            results.append(future.result())
    elapsed = time.perf_counter() - started
    latencies = [item["latency_ms"] for item in results]
    successes = sum(item["ok"] for item in results)
    return {
        "schema_version": 1,
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "target_url": url,
        "requests": requests,
        "concurrency": concurrency,
        "warmup_requests": warmup,
        "elapsed_seconds": round(elapsed, 3),
        "successful_requests": successes,
        "failed_requests": requests - successes,
        "throughput_requests_per_second": round(successes / elapsed, 3) if elapsed else None,
        "latency_ms": {"min": round(min(latencies), 2), "median": round(statistics.median(latencies), 2),
                       "p95": percentile(latencies, .95), "max": round(max(latencies), 2)} if latencies else {},
        "errors": [item["error"] for item in results if item["error"]][:10],
        "notice": "Measurement from this client and workload only; not a capacity or school-readiness certification."
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:3000/health")
    parser.add_argument("--requests", type=int, default=30)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--output", help="Optional JSON output file")
    args = parser.parse_args()
    result = run_benchmark(args.url, args.requests, args.concurrency, args.timeout, args.warmup)
    rendered = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered + "\\n")
    print(rendered)


if __name__ == "__main__":
    main()
