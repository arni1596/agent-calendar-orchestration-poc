from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import structlog
from dateutil import tz

from .config import settings
from .orchestration.engine import run_engine
from .tools.mock_calendar import MockCalendarClient

log = structlog.get_logger()


def run_simulation(goal: str, dry_run: bool = True) -> Dict[str, Any]:
    """
    Runs the engine against a mocked partner calendar.
    Produces regression-friendly trace artifacts.
    """
    request_id = f"sim_{uuid.uuid4()}"

    local_tz = tz.gettz(settings.timezone)
    if not local_tz:
        raise ValueError(f"Invalid timezone: {settings.timezone}")

    now = datetime.now(tz=local_tz)
    window_start = now + timedelta(days=settings.window_start_days)
    window_end = now + timedelta(days=settings.window_end_days)

    client = MockCalendarClient(timezone=settings.timezone)
    calendar_id = "mock_primary"

    engine_out = run_engine(
        goal=goal,
        dry_run=dry_run,
        calendar_client=client,
        calendar_id=calendar_id,
        window_start=window_start,
        window_end=window_end,
    )

    trace = {
        "request_id": request_id,
        "mode": "simulate",
        "goal": goal,
        "dry_run": dry_run,
        "time_window": {"start": window_start.isoformat(), "end": window_end.isoformat()},
        "decision_explanation": engine_out.decision_explanation,
        "result": engine_out.result,
        "diagnostics": engine_out.diagnostics,
        "metrics": engine_out.metrics,
        "regression": {"note": "Suitable as a golden artifact for deterministic regression checks."},
    }

    Path("runs").mkdir(exist_ok=True)
    out_path = Path("runs", f"{request_id}.json")
    out_path.write_text(json.dumps(trace, indent=2), encoding="utf-8")

    log.info("simulation_complete", request_id=request_id, status=engine_out.result.get("status"))
    return trace
