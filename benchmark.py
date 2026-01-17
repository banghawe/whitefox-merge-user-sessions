#!/usr/bin/env python3
"""
Benchmark merge_user_events with large datasets.

Usage:
    python benchmark.py                    # Run with default test_data.json
    python benchmark.py --generate         # Generate fresh data first
    python benchmark.py --users 100 --events 500
"""

import argparse
import json
import time
from pathlib import Path

from merge_events import merge_user_events
from generate_data import generate_events


def benchmark(events: list[dict], warmup: int = 1, runs: int = 5) -> dict:
    """
    Benchmark merge_user_events with timing statistics.
    
    Args:
        events: List of events to process
        warmup: Number of warmup runs (not counted)
        runs: Number of timed runs
    
    Returns:
        Dict with timing stats
    """
    # Warmup
    for _ in range(warmup):
        merge_user_events(events)
    
    # Timed runs
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        result = merge_user_events(events)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    
    return {
        "events": len(events),
        "sessions": len(result),
        "min_ms": min(times) * 1000,
        "max_ms": max(times) * 1000,
        "avg_ms": sum(times) / len(times) * 1000,
        "runs": runs,
    }


def main():
    parser = argparse.ArgumentParser(description="Benchmark merge_user_events")
    parser.add_argument("--generate", action="store_true", help="Generate fresh data")
    parser.add_argument("--users", type=int, default=50, help="Number of users")
    parser.add_argument("--events", type=int, default=200, help="Events per user")
    parser.add_argument("--runs", type=int, default=5, help="Number of benchmark runs")
    parser.add_argument("--input", type=str, default="test_data.json", help="Input file")
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("MERGE USER EVENTS - BENCHMARK")
    print("=" * 60)
    
    # Load or generate data
    if args.generate or not Path(args.input).exists():
        print(f"\n📊 Generating data: {args.users} users × {args.events} events...")
        events = generate_events(num_users=args.users, events_per_user=args.events)
        
        # Save for reuse
        with open(args.input, "w") as f:
            json.dump(events, f)
        print(f"   Saved to {args.input}")
    else:
        print(f"\n📂 Loading data from {args.input}...")
        with open(args.input) as f:
            events = json.load(f)
    
    print(f"   Total events: {len(events):,}")
    
    # Count unique users
    unique_users = len(set(e["user_id"] for e in events))
    print(f"   Unique users: {unique_users:,}")
    
    # Run benchmark
    print(f"\n⏱️  Benchmarking ({args.runs} runs)...")
    stats = benchmark(events, runs=args.runs)
    
    # Results
    print("\n" + "-" * 40)
    print("RESULTS")
    print("-" * 40)
    print(f"  Input events:    {stats['events']:,}")
    print(f"  Output sessions: {stats['sessions']:,}")
    print(f"  Avg time:        {stats['avg_ms']:.2f} ms")
    print(f"  Min time:        {stats['min_ms']:.2f} ms")
    print(f"  Max time:        {stats['max_ms']:.2f} ms")
    print(f"  Throughput:      {stats['events'] / (stats['avg_ms'] / 1000):,.0f} events/sec")
    print()
    
    # Verify correctness with a spot check
    print("🔍 Spot check...")
    result = merge_user_events(events)
    
    # Verify sorted by start_ts
    sorted_correctly = all(
        result[i]["start_ts"] <= result[i + 1]["start_ts"]
        for i in range(len(result) - 1)
    )
    print(f"   Sorted by start_ts: {'✅' if sorted_correctly else '❌'}")
    
    # Verify all sessions have required fields
    required_fields = {"user_id", "start_ts", "end_ts", "types", "meta"}
    all_fields_present = all(
        required_fields <= set(session.keys()) for session in result
    )
    print(f"   All fields present: {'✅' if all_fields_present else '❌'}")
    
    print("\n" + "=" * 60)
    print("✅ BENCHMARK COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
