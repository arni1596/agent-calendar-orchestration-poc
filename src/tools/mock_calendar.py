from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List


@dataclass
class MockCalendarClient:
    """
    Deterministic mock calendar client.
    Returns repeatable busy blocks as Google-like event items with start/end dateTime.
    """

    timezone: str = "America/Chicago"

    def list_events(self, calendar_id: str, time_min: str, time_max: str) -> List[Dict[str, Any]]:
        start = datetime.fromisoformat(time_min)
        end = datetime.fromisoformat(time_max)

        items: List[Dict[str, Any]] = []
        day = start

        # Deterministic busy blocks:
        # - Busy 10:00-10:30 and 15:00-15:45 each day in the window (if within range)
        while day < end:
            s1 = day.replace(hour=10, minute=0, second=0, microsecond=0)
            e1 = s1 + timedelta(minutes=30)

            s2 = day.replace(hour=15, minute=0, second=0, microsecond=0)
            e2 = s2 + timedelta(minutes=45)

            if start <= s1 <= end:
                items.append({"start": {"dateTime": s1.isoformat()}, "end": {"dateTime": e1.isoformat()}})
            if start <= s2 <= end:
                items.append({"start": {"dateTime": s2.isoformat()}, "end": {"dateTime": e2.isoformat()}})

            day += timedelta(days=1)

        return items

    def create_event(self, calendar_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": "mock_event_123",
            "htmlLink": "https://calendar.google.com/calendar/mock-event",
        }
