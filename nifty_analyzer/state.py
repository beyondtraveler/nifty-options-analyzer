from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import Any


@dataclass
class AnalyzerSnapshot:
    timestamp: datetime | None = None
    market_bias: str = "Neutral"
    top_resistance: int | None = None
    top_support: int | None = None
    atm_analysis: dict[str, Any] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)
    strikes: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class SharedState:
    def __init__(self) -> None:
        self._lock = Lock()
        self._snapshot = AnalyzerSnapshot()

    def update(self, snapshot: AnalyzerSnapshot) -> None:
        with self._lock:
            self._snapshot = snapshot

    def get(self) -> AnalyzerSnapshot:
        with self._lock:
            return self._snapshot
