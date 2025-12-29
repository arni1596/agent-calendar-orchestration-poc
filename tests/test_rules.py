from datetime import datetime, timedelta
from dateutil import tz

from src.orchestration.policy import SchedulingPolicy
from src.orchestration.rules import generate_candidate_slots, filter_conflicts


def test_generate_candidates_respects_window_and_policy():
    policy = SchedulingPolicy(
        timezone="America/Chicago",
        work_start_hour=9,
        work_end_hour=17,
        avoid_lunch_start=12,
        avoid_lunch_end=13,
        min_notice_hours=0,
        duration_min=30,
        slot_step_min=30,
        max_suggestions=3,
    )

    local_tz = tz.gettz(policy.timezone)
    now = datetime(2026, 1, 5, 8, 0, tzinfo=local_tz)  # Monday
    start = datetime(2026, 1, 5, 9, 0, tzinfo=local_tz)
    end = datetime(2026, 1, 5, 12, 0, tzinfo=local_tz)

    candidates = generate_candidate_slots(now, start, end, policy)
    assert len(candidates) > 0
    for s, e, _ in candidates:
        assert s.hour != 12


def test_filter_conflicts_removes_overlaps():
    policy = SchedulingPolicy(
        timezone="America/Chicago",
        work_start_hour=9,
        work_end_hour=17,
        avoid_lunch_start=12,
        avoid_lunch_end=13,
        min_notice_hours=0,
        duration_min=30,
        slot_step_min=30,
        max_suggestions=3,
    )

    local_tz = tz.gettz(policy.timezone)
    now = datetime(2026, 1, 5, 8, 0, tzinfo=local_tz)
    start = datetime(2026, 1, 5, 9, 0, tzinfo=local_tz)
    end = datetime(2026, 1, 5, 11, 0, tzinfo=local_tz)

    candidates = generate_candidate_slots(now, start, end, policy)

    busy = [(start, start + timedelta(minutes=30))]
    kept, rejected = filter_conflicts(candidates, busy)

    assert len(kept) < len(candidates)
    assert len(rejected) >= 1
