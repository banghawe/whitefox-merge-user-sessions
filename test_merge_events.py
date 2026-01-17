"""
Test suite for merge_user_events function.

Covers:
- Empty input
- Single event
- Multiple events same session
- Session boundary (600s vs 601s)
- Multiple users
- Deep merge meta conflicts
- Nested meta merging
- Unsorted input handling
- No input mutation
"""

import copy
import pytest

from merge_events import (
    deep_merge_meta,
    collect_unique_types,
    group_events_by_user,
    create_session,
    split_into_sessions,
    merge_user_events,
)


# =============================================================================
# UNIT TESTS: deep_merge_meta
# =============================================================================


class TestDeepMergeMeta:
    """Tests for the deep_merge_meta helper function."""

    def test_merge_empty_dicts(self):
        """Merging two empty dicts returns empty dict."""
        assert deep_merge_meta({}, {}) == {}

    def test_merge_base_empty(self):
        """New values are added when base is empty."""
        base = {}
        new = {"key": "value"}
        result = deep_merge_meta(base, new)
        assert result == {"key": "value"}

    def test_merge_new_empty(self):
        """Base is preserved when new is empty."""
        base = {"key": "value"}
        new = {}
        result = deep_merge_meta(base, new)
        assert result == {"key": "value"}

    def test_no_conflict_disjoint_keys(self):
        """Disjoint keys are both included."""
        base = {"a": 1}
        new = {"b": 2}
        result = deep_merge_meta(base, new)
        assert result == {"a": 1, "b": 2}

    def test_conflict_keeps_base_value(self):
        """On conflict, base (earliest) value wins."""
        base = {"page": "/home"}
        new = {"page": "/about"}
        result = deep_merge_meta(base, new)
        assert result == {"page": "/home"}

    def test_nested_dict_merge(self):
        """Nested dicts are merged recursively."""
        base = {"nested": {"a": 1}}
        new = {"nested": {"b": 2}}
        result = deep_merge_meta(base, new)
        assert result == {"nested": {"a": 1, "b": 2}}

    def test_nested_conflict_keeps_earliest(self):
        """Nested conflicts keep earliest value."""
        base = {"nested": {"key": "first"}}
        new = {"nested": {"key": "second"}}
        result = deep_merge_meta(base, new)
        assert result == {"nested": {"key": "first"}}

    def test_mixed_types_keeps_base(self):
        """When base has non-dict and new has dict, keep base."""
        base = {"key": "string_value"}
        new = {"key": {"nested": True}}
        result = deep_merge_meta(base, new)
        assert result == {"key": "string_value"}

    def test_does_not_mutate_inputs(self):
        """Inputs should not be mutated."""
        base = {"a": {"b": 1}}
        new = {"a": {"c": 2}}
        base_copy = copy.deepcopy(base)
        new_copy = copy.deepcopy(new)
        
        deep_merge_meta(base, new)
        
        assert base == base_copy
        assert new == new_copy

    def test_none_value_preserved(self):
        """None values are preserved when earliest."""
        base = {"key": None}
        new = {"key": "value"}
        result = deep_merge_meta(base, new)
        assert result == {"key": None}


# =============================================================================
# UNIT TESTS: collect_unique_types
# =============================================================================


class TestCollectUniqueTypes:
    """Tests for collect_unique_types helper function."""

    def test_empty_list(self):
        """Empty list returns empty types."""
        assert collect_unique_types([]) == []

    def test_single_event(self):
        """Single event returns single type."""
        events = [{"type": "click"}]
        assert collect_unique_types(events) == ["click"]

    def test_preserves_order(self):
        """Types are returned in order of first occurrence."""
        events = [
            {"type": "view"},
            {"type": "click"},
            {"type": "scroll"},
        ]
        assert collect_unique_types(events) == ["view", "click", "scroll"]

    def test_removes_duplicates(self):
        """Duplicate types are removed."""
        events = [
            {"type": "click"},
            {"type": "view"},
            {"type": "click"},  # duplicate
            {"type": "scroll"},
            {"type": "view"},  # duplicate
        ]
        assert collect_unique_types(events) == ["click", "view", "scroll"]

    def test_missing_type_treated_as_empty(self):
        """Missing type key treated as empty string."""
        events = [{"no_type": True}]
        assert collect_unique_types(events) == [""]


# =============================================================================
# UNIT TESTS: group_events_by_user
# =============================================================================


class TestGroupEventsByUser:
    """Tests for group_events_by_user helper function."""

    def test_empty_list(self):
        """Empty list returns empty dict."""
        assert group_events_by_user([]) == {}

    def test_single_user(self):
        """Single user events grouped correctly."""
        events = [
            {"user_id": "u1", "ts": 1000},
            {"user_id": "u1", "ts": 2000},
        ]
        result = group_events_by_user(events)
        assert "u1" in result
        assert len(result["u1"]) == 2

    def test_multiple_users(self):
        """Multiple users grouped separately."""
        events = [
            {"user_id": "u1", "ts": 1000},
            {"user_id": "u2", "ts": 1500},
            {"user_id": "u1", "ts": 2000},
        ]
        result = group_events_by_user(events)
        assert len(result) == 2
        assert len(result["u1"]) == 2
        assert len(result["u2"]) == 1


# =============================================================================
# INTEGRATION TESTS: merge_user_events
# =============================================================================


class TestMergeUserEventsBasic:
    """Basic integration tests for merge_user_events."""

    def test_empty_input(self):
        """Empty input returns empty list."""
        assert merge_user_events([]) == []

    def test_single_event(self):
        """Single event creates single session with same start/end."""
        events = [
            {"user_id": "u1", "ts": 1000, "type": "click", "meta": {"page": "/"}}
        ]
        result = merge_user_events(events)
        
        assert len(result) == 1
        session = result[0]
        assert session["user_id"] == "u1"
        assert session["start_ts"] == 1000
        assert session["end_ts"] == 1000
        assert session["types"] == ["click"]
        assert session["meta"] == {"page": "/"}

    def test_two_events_same_session(self):
        """Two events within 600s gap create one session."""
        events = [
            {"user_id": "u1", "ts": 1000, "type": "view", "meta": {}},
            {"user_id": "u1", "ts": 1500, "type": "click", "meta": {}},
        ]
        result = merge_user_events(events)
        
        assert len(result) == 1
        assert result[0]["start_ts"] == 1000
        assert result[0]["end_ts"] == 1500
        assert result[0]["types"] == ["view", "click"]


class TestMergeUserEventsSessionBoundary:
    """Tests for session boundary conditions (600s threshold)."""

    def test_exactly_600s_gap_same_session(self):
        """Gap of exactly 600s keeps events in same session."""
        events = [
            {"user_id": "u1", "ts": 1000, "type": "a", "meta": {}},
            {"user_id": "u1", "ts": 1600, "type": "b", "meta": {}},  # 600s gap
        ]
        result = merge_user_events(events)
        
        assert len(result) == 1
        assert result[0]["types"] == ["a", "b"]

    def test_601s_gap_new_session(self):
        """Gap of 601s creates new session."""
        events = [
            {"user_id": "u1", "ts": 1000, "type": "a", "meta": {}},
            {"user_id": "u1", "ts": 1601, "type": "b", "meta": {}},  # 601s gap
        ]
        result = merge_user_events(events)
        
        assert len(result) == 2
        assert result[0]["types"] == ["a"]
        assert result[1]["types"] == ["b"]

    def test_multiple_sessions_single_user(self):
        """User with multiple sessions based on time gaps."""
        events = [
            {"user_id": "u1", "ts": 1000, "type": "view", "meta": {}},
            {"user_id": "u1", "ts": 1500, "type": "click", "meta": {}},  # +500s, same
            {"user_id": "u1", "ts": 2200, "type": "scroll", "meta": {}},  # +700s, new
        ]
        result = merge_user_events(events)
        
        assert len(result) == 2
        assert result[0]["start_ts"] == 1000
        assert result[0]["end_ts"] == 1500
        assert result[0]["types"] == ["view", "click"]
        assert result[1]["start_ts"] == 2200
        assert result[1]["end_ts"] == 2200
        assert result[1]["types"] == ["scroll"]


class TestMergeUserEventsMultipleUsers:
    """Tests for multiple users scenarios."""

    def test_two_users_separate_sessions(self):
        """Each user gets their own sessions."""
        events = [
            {"user_id": "u1", "ts": 1000, "type": "click", "meta": {}},
            {"user_id": "u2", "ts": 1100, "type": "view", "meta": {}},
        ]
        result = merge_user_events(events)
        
        assert len(result) == 2
        # Sorted by start_ts
        assert result[0]["user_id"] == "u1"
        assert result[1]["user_id"] == "u2"

    def test_interleaved_users_sorted_by_start_ts(self):
        """Output sorted by start_ts across all users."""
        events = [
            {"user_id": "u2", "ts": 2000, "type": "b", "meta": {}},
            {"user_id": "u1", "ts": 1000, "type": "a", "meta": {}},
            {"user_id": "u3", "ts": 1500, "type": "c", "meta": {}},
        ]
        result = merge_user_events(events)
        
        assert len(result) == 3
        assert result[0]["start_ts"] == 1000  # u1
        assert result[1]["start_ts"] == 1500  # u3
        assert result[2]["start_ts"] == 2000  # u2


class TestMergeUserEventsUnsortedInput:
    """Tests for handling unsorted input."""

    def test_unsorted_input_handled_correctly(self):
        """Unsorted events are sorted before processing."""
        events = [
            {"user_id": "u1", "ts": 1500, "type": "click", "meta": {}},
            {"user_id": "u1", "ts": 1000, "type": "view", "meta": {}},  # earlier
        ]
        result = merge_user_events(events)
        
        assert len(result) == 1
        assert result[0]["start_ts"] == 1000
        assert result[0]["end_ts"] == 1500
        assert result[0]["types"] == ["view", "click"]  # chronological order


class TestMergeUserEventsMetaMerge:
    """Tests for meta deep merge functionality."""

    def test_meta_merge_no_conflict(self):
        """Disjoint meta keys are merged."""
        events = [
            {"user_id": "u1", "ts": 1000, "type": "a", "meta": {"page": "/"}},
            {"user_id": "u1", "ts": 1100, "type": "b", "meta": {"ref": "google"}},
        ]
        result = merge_user_events(events)
        
        assert result[0]["meta"] == {"page": "/", "ref": "google"}

    def test_meta_conflict_keeps_earliest(self):
        """Conflicting meta values keep earliest."""
        events = [
            {"user_id": "u1", "ts": 1000, "type": "a", "meta": {"page": "/home"}},
            {"user_id": "u1", "ts": 1100, "type": "b", "meta": {"page": "/about"}},
        ]
        result = merge_user_events(events)
        
        assert result[0]["meta"]["page"] == "/home"

    def test_nested_meta_merge(self):
        """Nested meta dicts are merged recursively."""
        events = [
            {"user_id": "u1", "ts": 1000, "type": "a", "meta": {"data": {"x": 1}}},
            {"user_id": "u1", "ts": 1100, "type": "b", "meta": {"data": {"y": 2}}},
        ]
        result = merge_user_events(events)
        
        assert result[0]["meta"] == {"data": {"x": 1, "y": 2}}

    def test_missing_meta_treated_as_empty(self):
        """Missing meta key treated as empty dict."""
        events = [
            {"user_id": "u1", "ts": 1000, "type": "a"},  # no meta
            {"user_id": "u1", "ts": 1100, "type": "b", "meta": {"page": "/"}},
        ]
        result = merge_user_events(events)
        
        assert result[0]["meta"] == {"page": "/"}


class TestMergeUserEventsNoMutation:
    """Tests ensuring input is not mutated."""

    def test_input_not_mutated(self):
        """Original events list is not modified."""
        events = [
            {"user_id": "u1", "ts": 1000, "type": "click", "meta": {"page": "/"}},
        ]
        original = copy.deepcopy(events)
        
        merge_user_events(events)
        
        assert events == original

    def test_nested_meta_not_mutated(self):
        """Nested meta in original events is not modified."""
        events = [
            {"user_id": "u1", "ts": 1000, "type": "a", "meta": {"data": {"x": 1}}},
            {"user_id": "u1", "ts": 1100, "type": "b", "meta": {"data": {"y": 2}}},
        ]
        original_first_meta = copy.deepcopy(events[0]["meta"])
        
        merge_user_events(events)
        
        assert events[0]["meta"] == original_first_meta


class TestMergeUserEventsEdgeCases:
    """Edge case tests."""

    def test_same_timestamp_events(self):
        """Events with same timestamp are in same session."""
        events = [
            {"user_id": "u1", "ts": 1000, "type": "a", "meta": {}},
            {"user_id": "u1", "ts": 1000, "type": "b", "meta": {}},
        ]
        result = merge_user_events(events)
        
        assert len(result) == 1
        assert result[0]["start_ts"] == 1000
        assert result[0]["end_ts"] == 1000

    def test_large_time_gap(self):
        """Very large time gap creates separate sessions."""
        events = [
            {"user_id": "u1", "ts": 1000, "type": "a", "meta": {}},
            {"user_id": "u1", "ts": 1000000, "type": "b", "meta": {}},
        ]
        result = merge_user_events(events)
        
        assert len(result) == 2

    def test_many_events_same_session(self):
        """Many events within threshold stay in same session."""
        base_ts = 1000
        events = [
            {"user_id": "u1", "ts": base_ts + i * 100, "type": f"t{i}", "meta": {}}
            for i in range(10)
        ]
        result = merge_user_events(events)
        
        assert len(result) == 1
        assert result[0]["start_ts"] == 1000
        assert result[0]["end_ts"] == 1900
        assert len(result[0]["types"]) == 10
