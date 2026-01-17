# Approach

## Algorithm Overview

```
1. Deep copy input (prevent mutation)
2. Group events by user_id
3. For each user:
   a. Sort events by timestamp
   b. Split into sessions (gap > 600s = new session)
   c. Merge events within each session
4. Collect all sessions
5. Sort by start_ts
6. Return
```

## Component Design

| Component | Responsibility |
|-----------|----------------|
| `deep_merge_meta` | Recursive dict merge, earliest wins |
| `collect_unique_types` | Unique types in chronological order |
| `group_events_by_user` | Dict: user_id → [events] |
| `create_session` | Merge events into session dict |
| `split_into_sessions` | Split by 600s gap threshold |
| `merge_user_events` | Main entry point |

## Data Flow

```
Input events (unsorted)
    ↓
Deep copy
    ↓
Group by user_id → {user_id: [events]}
    ↓
For each user: sort by ts
    ↓
Split into sessions (gap > 600s)
    ↓
Merge each session (types + meta)
    ↓
Collect all sessions
    ↓
Sort by start_ts
    ↓
Output
```

## Complexity

| Metric | Value | Reason |
|--------|-------|--------|
| Time | O(n log n) | Sorting dominates |
| Space | O(n) | Deep copy + output |
