# Assumptions

## Explicit Assumptions

| Assumption | Source |
|------------|--------|
| Session gap threshold is 600 seconds | Spec: "at most 10 minutes apart" |
| Gap ≤ 600s = same session | Spec: "≤ 600 seconds" |
| Output sorted by `start_ts` | Spec: "sorted by start_ts ascending" |
| No in-place mutation | Spec: "must not modify events in-place" |

## Implicit Assumptions

| Assumption | Rationale |
|------------|-----------|
| `types` = unique types in first-occurrence order | Spec says "duplicates removed, count preserved" — interpreted as ordered unique list |
| Missing `meta` → empty dict `{}` | Defensive handling to avoid KeyError |
| Python 3.7+ dict ordering | Standard in modern Python |
| `copy.deepcopy` is acceptable | Simplest way to prevent mutation |

## Edge Case Assumptions

| Scenario | Assumed Behavior |
|----------|------------------|
| Empty input | Return `[]` |
| Single event | Session with `start_ts == end_ts` |
| Same timestamp | Same session, order undefined but deterministic |
| `None` in meta | Preserved as-is |
| Missing `type` key | Treated as empty string `""` |
