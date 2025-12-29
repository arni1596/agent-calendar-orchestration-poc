from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class DiagnosticEvent:
    ts: str
    level: str
    code: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Diagnostics:
    events: List[DiagnosticEvent] = field(default_factory=list)

    def info(self, code: str, message: str, **details: Any) -> None:
        self._add("info", code, message, details)

    def warn(self, code: str, message: str, **details: Any) -> None:
        self._add("warn", code, message, details)

    def error(self, code: str, message: str, **details: Any) -> None:
        self._add("error", code, message, details)

    def _add(self, level: str, code: str, message: str, details: Dict[str, Any]) -> None:
        self.events.append(
            DiagnosticEvent(
                ts=datetime.utcnow().isoformat() + "Z",
                level=level,
                code=code,
                message=message,
                details=details,
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"events": [e.__dict__ for e in self.events]}
