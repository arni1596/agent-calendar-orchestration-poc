from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SchedulingPolicy:
    """
    Policy is separate from execution on purpose.
    This is how you keep orchestration deterministic and explainable.
    """
    timezone: str
    work_start_hour: int
    work_end_hour: int
    avoid_lunch_start: int
    avoid_lunch_end: int
    min_notice_hours: int
    duration_min: int
    slot_step_min: int
    max_suggestions: int
