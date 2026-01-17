"""
Merge User Events Module

Groups user events into sessions based on time proximity (≤600 seconds gap).
"""

from __future__ import annotations

import copy
from collections import defaultdict
from typing import Any


# -----------------------------------------------------------------------------
# CONSTANTS
# -----------------------------------------------------------------------------

SESSION_GAP_THRESHOLD = 600  # seconds


# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------


def deep_merge_meta(base: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively merge two meta dictionaries.
    
    Rules:
    - If both have a key with dict values, merge recursively.
    - If there's a conflict on a non-dict value, keep the base (earliest) value.
    
    Args:
        base: The base dictionary (earlier in time, takes precedence on conflicts).
        new: The new dictionary to merge in.
    
    Returns:
        A new merged dictionary (does not mutate inputs).
    """
    result = copy.deepcopy(base)
    
    for key, new_value in new.items():
        if key not in result:
            # Key doesn't exist in base, add it
            result[key] = copy.deepcopy(new_value)
        elif isinstance(result[key], dict) and isinstance(new_value, dict):
            # Both are dicts, merge recursively
            result[key] = deep_merge_meta(result[key], new_value)
        # else: conflict on non-dict value, keep base (earliest) - do nothing
    
    return result


def collect_unique_types(events: list[dict[str, Any]]) -> list[str]:
    """
    Collect unique event types in chronological order of first occurrence.
    
    Args:
        events: List of events, assumed to be sorted by timestamp.
    
    Returns:
        List of unique type strings in order of first occurrence.
    """
    seen: set[str] = set()
    types: list[str] = []
    
    for event in events:
        event_type = event.get("type", "")
        if event_type not in seen:
            seen.add(event_type)
            types.append(event_type)
    
    return types


def group_events_by_user(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """
    Group events by user_id.
    
    Args:
        events: List of event dictionaries.
    
    Returns:
        Dictionary mapping user_id to list of their events.
    """
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    
    for event in events:
        user_id = event.get("user_id", "")
        groups[user_id].append(event)
    
    return dict(groups)


def create_session(events: list[dict[str, Any]], user_id: str) -> dict[str, Any]:
    """
    Create a single session from a list of events.
    
    Assumes events are sorted by timestamp and belong to the same user.
    
    Args:
        events: Non-empty list of events for the session.
        user_id: The user ID for this session.
    
    Returns:
        Session dictionary with user_id, start_ts, end_ts, types, and meta.
    """
    if not events:
        raise ValueError("Cannot create session from empty events list")
    
    # Get timestamps
    start_ts = events[0]["ts"]
    end_ts = events[-1]["ts"]
    
    # Collect unique types in order
    types = collect_unique_types(events)
    
    # Deep merge all meta objects, earliest takes precedence on conflicts
    merged_meta: dict[str, Any] = {}
    for event in events:
        event_meta = event.get("meta", {}) or {}
        merged_meta = deep_merge_meta(merged_meta, event_meta)
    
    return {
        "user_id": user_id,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "types": types,
        "meta": merged_meta,
    }


def split_into_sessions(
    sorted_events: list[dict[str, Any]], user_id: str
) -> list[dict[str, Any]]:
    """
    Split a sorted list of events into sessions based on time gaps.
    
    A new session starts when the gap between consecutive events exceeds
    SESSION_GAP_THRESHOLD (600 seconds).
    
    Args:
        sorted_events: List of events sorted by timestamp.
        user_id: The user ID for these events.
    
    Returns:
        List of session dictionaries.
    """
    if not sorted_events:
        return []
    
    sessions: list[dict[str, Any]] = []
    current_session_events: list[dict[str, Any]] = [sorted_events[0]]
    
    for i in range(1, len(sorted_events)):
        prev_event = sorted_events[i - 1]
        curr_event = sorted_events[i]
        
        gap = curr_event["ts"] - prev_event["ts"]
        
        if gap > SESSION_GAP_THRESHOLD:
            # Gap exceeds threshold, finalize current session and start new one
            sessions.append(create_session(current_session_events, user_id))
            current_session_events = [curr_event]
        else:
            # Within threshold, add to current session
            current_session_events.append(curr_event)
    
    # Finalize the last session
    sessions.append(create_session(current_session_events, user_id))
    
    return sessions


# -----------------------------------------------------------------------------
# MAIN FUNCTION
# -----------------------------------------------------------------------------


def merge_user_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Merge user events into sessions.
    
    A session is a consecutive run of events for the same user where adjacent
    events are at most 600 seconds apart.
    
    Args:
        events: List of event dictionaries. Each event should have:
            - user_id: str
            - ts: int (Unix timestamp)
            - type: str
            - meta: dict (optional)
    
    Returns:
        List of session dictionaries sorted by start_ts, each containing:
            - user_id: str
            - start_ts: int
            - end_ts: int
            - types: list[str] (unique types in chronological order)
            - meta: dict (deep merged from all events)
    
    Note:
        This function does NOT modify the input events list.
    """
    if not events:
        return []
    
    # Deep copy to prevent mutation of input
    events_copy = copy.deepcopy(events)
    
    # Group events by user_id
    user_groups = group_events_by_user(events_copy)
    
    # Create sessions for each user
    all_sessions: list[dict[str, Any]] = []
    
    for user_id, user_events in user_groups.items():
        # Sort user's events by timestamp
        sorted_events = sorted(user_events, key=lambda e: e["ts"])
        
        # Split into sessions and add to results
        sessions = split_into_sessions(sorted_events, user_id)
        all_sessions.extend(sessions)
    
    # Sort all sessions by start_ts
    return sorted(all_sessions, key=lambda s: s["start_ts"])
