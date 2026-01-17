# Problem Summary

## Problem Statement

Implement `merge_user_events(events)` that groups user events into "sessions" based on time proximity.

A session is a consecutive run of events for the same user where adjacent events are at most **600 seconds (10 minutes)** apart.

## Rules

1. **Grouping**: Events are grouped by `user_id`
2. **Session boundary**: Gap > 600 seconds starts a new session
3. **Types**: Unique event types in chronological order of first occurrence
4. **Meta merge**: Deep merge all meta objects; conflicts keep earliest value
5. **Sorting**: Output sorted by `start_ts` ascending (across all users)
6. **No mutation**: Input events must not be modified

## Input/Output Example

**Input** (unsorted):
```python
events = [
    {"user_id": "u1", "ts": 1500, "type": "click", "meta": {"page": "/"}},
    {"user_id": "u1", "ts": 1000, "type": "view", "meta": {"page": "/home"}},
    {"user_id": "u1", "ts": 2200, "type": "scroll", "meta": {"ref": "google"}},
]
```

**Output**:
```python
[
    {
        "user_id": "u1",
        "start_ts": 1000,
        "end_ts": 1500,
        "types": ["view", "click"],
        "meta": {"page": "/home"}
    },
    {
        "user_id": "u1",
        "start_ts": 2200,
        "end_ts": 2200,
        "types": ["scroll"],
        "meta": {"ref": "google"}
    }
]
```

**Explanation**:
- Events at t=1000 and t=1500 → same session (gap=500s ≤ 600s)
- Event at t=2200 → new session (gap=700s > 600s)

## Requirements Clarification

| Requirement | Clarification |
|-------------|---------------|
| `types` field | Unique types in order of first occurrence (duplicates removed) |
| `meta` conflicts | Deep merge recursively; earliest value wins on non-dict conflicts |
| Missing `meta` | Treated as empty dict `{}` |
| Same timestamp | Events processed in arbitrary but deterministic order |
| Empty input | Returns empty list `[]` |
| Single event | Session with `start_ts == end_ts` |
