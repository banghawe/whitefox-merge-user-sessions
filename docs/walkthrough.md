# Merge User Events — Walkthrough

## Summary

Implemented `merge_user_events(events)` that groups user events into sessions based on time proximity (≤600s gap).

---

## Changes Made

### [merge_events.py](file:///Users/hendrawardana/Documents/interview/whitefox/merge_events.py)

| Function | Purpose |
|----------|---------|
| `deep_merge_meta` | Recursive dict merge, earliest value wins on conflicts |
| `collect_unique_types` | Unique types in chronological order |
| `group_events_by_user` | Group events by `user_id` |
| `create_session` | Merge events into single session dict |
| `split_into_sessions` | Split sorted events by 600s gap threshold |
| `merge_user_events` | Main entry point |

### [test_merge_events.py](file:///Users/hendrawardana/Documents/interview/whitefox/test_merge_events.py)

Comprehensive test suite with **36 test cases** covering:
- Unit tests for `deep_merge_meta`, `collect_unique_types`, `group_events_by_user`
- Integration tests for session boundary (600s vs 601s)
- Multiple users, unsorted input, nested meta merging
- No-mutation guarantees

---

## Test Results

```
36 passed in 0.03s
```

All tests pass, including:
- ✅ Empty input handling
- ✅ Single event → single session
- ✅ 600s gap → same session
- ✅ 601s gap → new session
- ✅ Multiple users sorted by `start_ts`
- ✅ Deep merge with conflict resolution
- ✅ No input mutation

---

## How to Run Tests

```bash
cd /Users/hendrawardana/Documents/interview/whitefox
source venv/bin/activate
python -m pytest test_merge_events.py -v
```

---

## Assumptions & Trade-offs

| Assumption | Rationale |
|------------|-----------|
| `types` = unique types in first-occurrence order | Spec: "duplicates removed, count preserved" |
| Missing `meta` → empty dict | Defensive handling |
| `copy.deepcopy` for input | Ensures no mutation |

| Trade-off | Decision |
|-----------|----------|
| Clarity vs. micro-optimization | Chose readable code |
| Deep copy entire input | Safer than selective copying |

---

## Complexity

- **Time**: O(n log n) — dominated by sorting
- **Space**: O(n) — deep copy + output sessions
