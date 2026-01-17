#!/usr/bin/env python3
"""
Manual verification script for merge_user_events.

Run: python demo.py
"""

from merge_events import merge_user_events
import json


def print_json(data, label=""):
    """Pretty print JSON data."""
    if label:
        print(f"\n{label}")
        print("=" * len(label))
    print(json.dumps(data, indent=2))


def main():
    print("\n" + "=" * 60)
    print("MERGE USER EVENTS - MANUAL VERIFICATION")
    print("=" * 60)

    # ---------------------------------------------------------------------
    # Test 1: Basic session merging
    # ---------------------------------------------------------------------
    print("\n\n📋 TEST 1: Basic Session Merging")
    print("-" * 40)
    
    events = [
        {"user_id": "u1", "ts": 1500, "type": "click", "meta": {"page": "/"}},
        {"user_id": "u1", "ts": 1000, "type": "view", "meta": {"page": "/home"}},
        {"user_id": "u1", "ts": 2200, "type": "scroll", "meta": {"ref": "google"}},
    ]
    
    print("\nInput (unsorted):")
    for e in events:
        print(f"  - user={e['user_id']}, ts={e['ts']}, type={e['type']}")
    
    result = merge_user_events(events)
    
    print("\nExpected: 2 sessions")
    print("  - Session 1: ts 1000→1500 (gap=500s ≤ 600s)")
    print("  - Session 2: ts 2200→2200 (gap=700s > 600s, new session)")
    
    print_json(result, "Actual Output:")
    
    assert len(result) == 2, f"Expected 2 sessions, got {len(result)}"
    assert result[0]["start_ts"] == 1000
    assert result[0]["end_ts"] == 1500
    assert result[1]["start_ts"] == 2200
    print("\n✅ PASSED")

    # ---------------------------------------------------------------------
    # Test 2: Multiple users
    # ---------------------------------------------------------------------
    print("\n\n📋 TEST 2: Multiple Users")
    print("-" * 40)
    
    events = [
        {"user_id": "alice", "ts": 2000, "type": "login", "meta": {}},
        {"user_id": "bob", "ts": 1000, "type": "view", "meta": {}},
        {"user_id": "alice", "ts": 2100, "type": "click", "meta": {}},
    ]
    
    print("\nInput:")
    for e in events:
        print(f"  - user={e['user_id']}, ts={e['ts']}, type={e['type']}")
    
    result = merge_user_events(events)
    
    print("\nExpected: 2 sessions, sorted by start_ts")
    print("  - bob at ts=1000")
    print("  - alice at ts=2000-2100")
    
    print_json(result, "Actual Output:")
    
    assert len(result) == 2
    assert result[0]["user_id"] == "bob"
    assert result[1]["user_id"] == "alice"
    print("\n✅ PASSED")

    # ---------------------------------------------------------------------
    # Test 3: Deep meta merge
    # ---------------------------------------------------------------------
    print("\n\n📋 TEST 3: Deep Meta Merge (earliest wins)")
    print("-" * 40)
    
    events = [
        {"user_id": "u1", "ts": 1000, "type": "a", "meta": {"page": "/first", "data": {"x": 1}}},
        {"user_id": "u1", "ts": 1100, "type": "b", "meta": {"page": "/second", "data": {"y": 2}}},
    ]
    
    print("\nInput meta values:")
    print("  - ts=1000: page='/first', data.x=1")
    print("  - ts=1100: page='/second', data.y=2")
    
    result = merge_user_events(events)
    
    print("\nExpected merged meta:")
    print("  - page='/first' (earliest wins on conflict)")
    print("  - data={x:1, y:2} (nested dicts merged)")
    
    print_json(result[0]["meta"], "Actual meta:")
    
    assert result[0]["meta"]["page"] == "/first"
    assert result[0]["meta"]["data"] == {"x": 1, "y": 2}
    print("\n✅ PASSED")

    # ---------------------------------------------------------------------
    # Test 4: Session boundary (600s vs 601s)
    # ---------------------------------------------------------------------
    print("\n\n📋 TEST 4: Session Boundary (600s threshold)")
    print("-" * 40)
    
    # 600s gap - same session
    events_600 = [
        {"user_id": "u1", "ts": 1000, "type": "a", "meta": {}},
        {"user_id": "u1", "ts": 1600, "type": "b", "meta": {}},
    ]
    result_600 = merge_user_events(events_600)
    
    # 601s gap - new session
    events_601 = [
        {"user_id": "u1", "ts": 1000, "type": "a", "meta": {}},
        {"user_id": "u1", "ts": 1601, "type": "b", "meta": {}},
    ]
    result_601 = merge_user_events(events_601)
    
    print("\n600s gap (ts: 1000 → 1600):")
    print(f"  Sessions: {len(result_600)} (expected: 1)")
    
    print("\n601s gap (ts: 1000 → 1601):")
    print(f"  Sessions: {len(result_601)} (expected: 2)")
    
    assert len(result_600) == 1, "600s should be same session"
    assert len(result_601) == 2, "601s should be new session"
    print("\n✅ PASSED")

    # ---------------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("🎉 ALL MANUAL VERIFICATION TESTS PASSED!")
    print("=" * 60)
    print("\nTo run full test suite:")
    print("  source venv/bin/activate && python -m pytest test_merge_events.py -v")
    print()


if __name__ == "__main__":
    main()
