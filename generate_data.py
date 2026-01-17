#!/usr/bin/env python3
"""
Generate large test datasets for merge_user_events.

Usage:
    python generate_data.py              # Generate default dataset
    python generate_data.py --users 100 --events 10000
"""

import argparse
import json
import random
import time
from pathlib import Path


def generate_events(
    num_users: int = 50,
    events_per_user: int = 200,
    seed: int = 42,
) -> list[dict]:
    """
    Generate a large dataset of random events.
    
    Args:
        num_users: Number of unique users
        events_per_user: Average events per user
        seed: Random seed for reproducibility
    
    Returns:
        List of event dictionaries (unsorted)
    """
    random.seed(seed)
    
    event_types = ["view", "click", "scroll", "hover", "submit", "login", "logout"]
    pages = ["/", "/home", "/about", "/products", "/cart", "/checkout", "/profile"]
    refs = ["google", "facebook", "twitter", "email", "direct", None]
    
    events = []
    base_ts = 1700000000  # Unix timestamp (Nov 2023)
    
    for user_num in range(num_users):
        user_id = f"user_{user_num:04d}"
        
        # Random number of events for this user (±50% of average)
        num_events = random.randint(
            events_per_user // 2, 
            events_per_user + events_per_user // 2
        )
        
        # Generate events with varying time gaps
        current_ts = base_ts + random.randint(0, 86400)  # Random start within a day
        
        for _ in range(num_events):
            # 70% chance of small gap (same session), 30% chance of large gap (new session)
            if random.random() < 0.7:
                gap = random.randint(10, 500)  # 10s to 500s (same session)
            else:
                gap = random.randint(700, 7200)  # 700s to 2h (new session)
            
            current_ts += gap
            
            event = {
                "user_id": user_id,
                "ts": current_ts,
                "type": random.choice(event_types),
                "meta": {
                    "page": random.choice(pages),
                    "data": {
                        "scroll_depth": random.randint(0, 100),
                        "viewport": {"width": 1920, "height": 1080},
                    },
                },
            }
            
            # Randomly add optional meta fields
            if random.random() < 0.3:
                event["meta"]["ref"] = random.choice(refs)
            
            events.append(event)
    
    # Shuffle to simulate unsorted input
    random.shuffle(events)
    
    return events


def main():
    parser = argparse.ArgumentParser(description="Generate test data for merge_user_events")
    parser.add_argument("--users", type=int, default=50, help="Number of users")
    parser.add_argument("--events", type=int, default=200, help="Events per user (average)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--output", type=str, default="test_data.json", help="Output file")
    args = parser.parse_args()
    
    print(f"Generating {args.users} users × ~{args.events} events each...")
    
    start = time.time()
    events = generate_events(
        num_users=args.users,
        events_per_user=args.events,
        seed=args.seed,
    )
    gen_time = time.time() - start
    
    # Save to file
    output_path = Path(args.output)
    with open(output_path, "w") as f:
        json.dump(events, f)
    
    file_size = output_path.stat().st_size / 1024 / 1024  # MB
    
    print(f"\n✅ Generated {len(events):,} events")
    print(f"   Users: {args.users}")
    print(f"   Generation time: {gen_time:.2f}s")
    print(f"   Output: {output_path} ({file_size:.2f} MB)")


if __name__ == "__main__":
    main()
