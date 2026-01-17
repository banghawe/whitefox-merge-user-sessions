# Merge User Events

Groups user events into sessions based on time proximity.

## Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install pytest

# Run tests
python -m pytest test_merge_events.py -v

# Run manual verification demo
python demo.py
```

## Usage

```python
from merge_events import merge_user_events

events = [
    {"user_id": "u1", "ts": 1000, "type": "view", "meta": {"page": "/home"}},
    {"user_id": "u1", "ts": 1500, "type": "click", "meta": {"page": "/"}},
    {"user_id": "u1", "ts": 2200, "type": "scroll", "meta": {}},
]

sessions = merge_user_events(events)
# Returns 2 sessions:
# - Session 1: ts 1000-1500 (gap=500s ≤ 600s)
# - Session 2: ts 2200-2200 (gap=700s > 600s, new session)
```

## Session Rules

- Events grouped by `user_id`
- Adjacent events ≤ 600 seconds apart → same session
- Gap > 600 seconds → new session

## Output Format

```python
{
    "user_id": "u1",
    "start_ts": 1000,
    "end_ts": 1500,
    "types": ["view", "click"],  # unique, chronological order
    "meta": {"page": "/home"}    # deep merged, earliest wins on conflict
}
```

## Assumptions

| Assumption | Rationale |
|------------|-----------|
| `types` = unique types in order of first occurrence | Spec: "duplicates removed, count preserved" |
| Missing `meta` → `{}` | Defensive handling |
| Deep copy input | Guarantee no mutation |

## Trade-offs

| Trade-off | Decision |
|-----------|----------|
| Clarity vs. performance | Chose readable code |
| Full deep copy | Safer than selective copying |

## Complexity

- **Time**: O(n log n) — sorting
- **Space**: O(n) — copy + output

## Benchmarking

```bash
# Generate large test dataset (100 users × 500 events each)
python generate_data.py --users 100 --events 500

# Run benchmark
python benchmark.py

# Generate fresh data and benchmark
python benchmark.py --generate --users 100 --events 500
```

