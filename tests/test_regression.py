from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

from dateutil import tz

from src.config import settings


def _parse_dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


def _is_weekday(dt: datetime) -> bool:
    return dt.weekday() < 5


def _in_work_hours(local: datetime) -> bool:
    return settings.work_start_hour <= local.hour < settings.work_end_hour


def _in_lunch(local: datetime) -> bool:
    return settings.avoid_lunch_start <= local.hour < settings.avoid_lunch_end


def _load_latest_sim_trace() -> dict:
    runs = Path("runs")
    assert runs.exists(), "runs/ folder missing. Run `python -m src.app simulate --dry-run` first."

    sim_files = sorted(runs.glob("sim_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    assert sim_files, "No sim traces found. Run `python -m src.app simulate --dry-run` first."

    return json.loads(sim_files[0].read_text(encoding="utf-8"))


def test_simulation_trace_invariants():
    trace = _load_latest_sim_trace()

    assert trace.get("mode") == "simulate"
    assert "decision_explanation" in trace
    assert "result" in trace
    assert "metrics" in trace

    result = trace["result"]
    decision = trace["decision_explanation"]
    policy = decision["policy"]

    assert policy["work_start_hour"] == settings.work_start_hour
    assert policy["work_end_hour"] == settings.work_end_hour
    assert policy["avoid_lunch_start"] == settings.avoid_lunch_start
    assert policy["avoid_lunch_end"] == settings.avoid_lunch_end
    assert policy["duration_min"] == settings.default_event_duration_min

    assert result["status"] in {"dry_run", "created", "no_slots"}

    if result["status"] == "no_slots":
        assert "chosen_slot_reason" in decision and decision["chosen_slot_reason"]
        assert "advice" in result and len(result["advice"]) >= 1
        return

    chosen = result["chosen"]
    start = _parse_dt(chosen["start"])
    end = _parse_dt(chosen["end"])
    assert end > start

    local_tz = tz.gettz(settings.timezone)
    assert local_tz
    start_local = start.astimezone(local_tz)

    assert _is_weekday(start_local)
    assert _in_work_hours(start_local)
    assert not _in_lunch(start_local)

    alts = result.get("alternatives", [])
    assert isinstance(alts, list)
    for a in alts:
        _parse_dt(a["start"])
        _parse_dt(a["end"])

    metrics = trace["metrics"]
    for key in ["partner_list_events_ms", "generate_candidates_ms", "filter_conflicts_ms"]:
        assert key in metrics
        assert metrics[key] >= 0.0
