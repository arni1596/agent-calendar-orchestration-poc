from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Tuple, Protocol

from dateutil import tz

from ..diagnostics import Diagnostics
from ..config import settings
from .policy import SchedulingPolicy
from .rules import generate_candidate_slots, filter_conflicts


class CalendarClient(Protocol):
    def list_events(self, calendar_id: str, time_min: str, time_max: str) -> List[Dict[str, Any]]: ...
    def create_event(self, calendar_id: str, body: Dict[str, Any]) -> Dict[str, Any]: ...


@dataclass
class EngineResult:
    decision_explanation: Dict[str, Any]
    result: Dict[str, Any]
    diagnostics: Dict[str, Any]
    metrics: Dict[str, float]


def _parse_busy(events: List[Dict[str, Any]]) -> List[Tuple[datetime, datetime]]:
    """
    Privacy-minded parsing: we only extract busy time ranges.
    We do not persist event titles/summaries in traces.
    """
    busy: List[Tuple[datetime, datetime]] = []
    for e in events:
        s = e.get("start", {}).get("dateTime")
        en = e.get("end", {}).get("dateTime")
        if s and en:
            busy.append((datetime.fromisoformat(s), datetime.fromisoformat(en)))
    return busy


def run_engine(
    *,
    goal: str,
    dry_run: bool,
    calendar_client: CalendarClient,
    calendar_id: str,
    window_start: datetime,
    window_end: datetime,
) -> EngineResult:
    """
    Core deterministic engine shared by real and mock partner integrations.
    Produces decision explanation + result + diagnostics + metrics.
    """
    diag = Diagnostics()
    metrics: Dict[str, float] = {}

    local_tz = tz.gettz(settings.timezone)
    if not local_tz:
        diag.error("TZ_INVALID", "Invalid timezone.", timezone=settings.timezone)
        raise ValueError(f"Invalid timezone: {settings.timezone}")

    now = datetime.now(tz=local_tz)

    policy = SchedulingPolicy(
        timezone=settings.timezone,
        work_start_hour=settings.work_start_hour,
        work_end_hour=settings.work_end_hour,
        avoid_lunch_start=settings.avoid_lunch_start,
        avoid_lunch_end=settings.avoid_lunch_end,
        min_notice_hours=settings.min_notice_hours,
        duration_min=settings.default_event_duration_min,
        slot_step_min=settings.slot_step_min,
        max_suggestions=settings.max_suggestions,
    )

    t0 = time.perf_counter()
    diag.info("LIST_EVENTS", "Listing busy blocks.", calendar_id=calendar_id)
    events = calendar_client.list_events(calendar_id, window_start.isoformat(), window_end.isoformat())
    busy_blocks = _parse_busy(events)
    metrics["partner_list_events_ms"] = (time.perf_counter() - t0) * 1000.0
    diag.info("BUSY_PARSED", "Busy blocks extracted.", count=len(busy_blocks))

    t1 = time.perf_counter()
    candidates = generate_candidate_slots(now, window_start, window_end, policy)
    metrics["generate_candidates_ms"] = (time.perf_counter() - t1) * 1000.0
    diag.info("CANDIDATES", "Candidates generated.", count=len(candidates))

    t2 = time.perf_counter()
    available, rejected = filter_conflicts(candidates, busy_blocks)
    metrics["filter_conflicts_ms"] = (time.perf_counter() - t2) * 1000.0
    diag.info("AVAILABLE", "Available slots after filtering.", count=len(available))

    available = available[: policy.max_suggestions]
    chosen = available[0] if available else None

    decision_explanation: Dict[str, Any] = {
        "policy": policy.__dict__,
        "selection_rule": "Earliest valid slot satisfying policy + conflict constraints",
        "chosen_slot_reason": None,
        "rejected_summary": rejected[:10],
    }

    if not chosen:
        decision_explanation["chosen_slot_reason"] = "No slots satisfied constraints within window."
        diag.warn("NO_SLOTS", "No available slots found under current policy.")
        result = {
            "status": "no_slots",
            "advice": [
                "Widen the date window (increase WINDOW_END_DAYS).",
                "Relax constraints (work hours / lunch / notice period).",
                "Reduce duration (DEFAULT_EVENT_DURATION_MIN).",
            ],
        }
        return EngineResult(decision_explanation, result, diag.to_dict(), metrics)

    s, e, why = chosen
    decision_explanation["chosen_slot_reason"] = "Selected earliest available slot under policy."

    event_body = {
        "summary": "Interview Prep Block",
        "description": f"Scheduled by policy-driven orchestration.\nGoal: {goal}\nDecision: {why}",
        "start": {"dateTime": s.isoformat(), "timeZone": settings.timezone},
        "end": {"dateTime": e.isoformat(), "timeZone": settings.timezone},
    }
    alternatives = [{"start": a.isoformat(), "end": b.isoformat()} for a, b, _ in available[1:]]

    if dry_run:
        diag.info("DRY_RUN", "Dry-run mode: no event created.")
        result = {
            "status": "dry_run",
            "chosen": {"start": s.isoformat(), "end": e.isoformat()},
            "alternatives": alternatives,
            "event_body_preview": event_body,
        }
        return EngineResult(decision_explanation, result, diag.to_dict(), metrics)

    diag.info("CREATE_EVENT", "Creating event.", calendar_id=calendar_id)
    created = calendar_client.create_event(calendar_id, event_body)
    result = {
        "status": "created",
        "chosen": {"start": s.isoformat(), "end": e.isoformat()},
        "alternatives": alternatives,
        "event_id": created.get("id"),
        "htmlLink": created.get("htmlLink"),
    }
    diag.info("CREATED", "Event created.", event_id=created.get("id"))
    return EngineResult(decision_explanation, result, diag.to_dict(), metrics)
