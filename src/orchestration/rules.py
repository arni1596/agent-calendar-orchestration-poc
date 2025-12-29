from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Tuple

from dateutil import tz

from .policy import SchedulingPolicy


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return max(a_start, b_start) < min(a_end, b_end)


def generate_candidate_slots(
    now: datetime, window_start: datetime, window_end: datetime, policy: SchedulingPolicy
) -> List[Tuple[datetime, datetime, str]]:
    """
    Generate candidate slots that satisfy policy constraints.
    Each candidate includes a qualification reason (for audit/debug).
    """
    local_tz = tz.gettz(policy.timezone)
    if not local_tz:
        raise ValueError(f"Invalid timezone: {policy.timezone}")

    min_start = now + timedelta(hours=policy.min_notice_hours)

    candidates: List[Tuple[datetime, datetime, str]] = []
    cursor = window_start

    step = timedelta(minutes=policy.slot_step_min)
    dur = timedelta(minutes=policy.duration_min)

    while cursor < window_end:
        local = cursor.astimezone(local_tz)

        if local.weekday() < 5:  # Mon–Fri only
            in_work = policy.work_start_hour <= local.hour < policy.work_end_hour
            in_lunch = policy.avoid_lunch_start <= local.hour < policy.avoid_lunch_end

            if in_work and not in_lunch and cursor >= min_start:
                s = cursor
                e = cursor + dur
                candidates.append((s, e, "Meets work-hours + notice-period + no-lunch constraints"))

        cursor += step

    return candidates


def filter_conflicts(
    candidates: List[Tuple[datetime, datetime, str]],
    busy_blocks: List[Tuple[datetime, datetime]],
) -> Tuple[List[Tuple[datetime, datetime, str]], List[str]]:
    """
    Returns:
      - kept candidates
      - rejected reason summaries (non-sensitive)
    """
    kept: List[Tuple[datetime, datetime, str]] = []
    rejected: List[str] = []

    for s, e, why in candidates:
        conflict = False
        for bs, be in busy_blocks:
            if overlaps(s, e, bs, be):
                conflict = True
                rejected.append("Rejected candidate: conflict with existing busy block")
                break
        if not conflict:
            kept.append((s, e, why))

    return kept, rejected
