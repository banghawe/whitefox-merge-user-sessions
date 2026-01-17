# Merge User Events

Groups user events into sessions based on time proximity (≤600s gap).

## Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install pytest

# Run
python demo.py                         # Manual verification
python -m pytest test_merge_events.py -v  # Full test suite
python benchmark.py --generate         # Performance benchmark
```

## Usage

```python
from merge_events import merge_user_events

events = [
    {"user_id": "u1", "ts": 1000, "type": "view", "meta": {"page": "/"}},
    {"user_id": "u1", "ts": 1500, "type": "click", "meta": {}},
]

sessions = merge_user_events(events)
```

## Documentation

| Document | Description |
|----------|-------------|
| [Problem Summary](docs/problem_summary.md) | Requirements and examples |
| [Approach](docs/approach.md) | Algorithm and design |
| [Assumptions](docs/assumptions.md) | Explicit and implicit assumptions |
| [Trade-offs](docs/tradeoffs.md) | Design decisions |
