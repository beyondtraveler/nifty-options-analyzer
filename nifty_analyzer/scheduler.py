from __future__ import annotations

import threading

from nifty_analyzer.analyzer import analyze_option_chain
from nifty_analyzer.nse_client import NSEClient
from nifty_analyzer.state import AnalyzerSnapshot, SharedState


class AnalyzerScheduler:
    def __init__(self, state: SharedState, interval_seconds: int = 60) -> None:
        self.state = state
        self.interval_seconds = interval_seconds
        self.client = NSEClient()
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def _run_loop(self) -> None:
        while not self._stop.is_set():
            try:
                payload = self.client.fetch_option_chain()
                snapshot = analyze_option_chain(payload)
            except Exception as exc:  # noqa: BLE001
                previous = self.state.get()
                errors = list(previous.errors)
                errors.append(str(exc))
                snapshot = AnalyzerSnapshot(
                    timestamp=previous.timestamp,
                    market_bias=previous.market_bias,
                    top_resistance=previous.top_resistance,
                    top_support=previous.top_support,
                    atm_analysis=previous.atm_analysis,
                    summary=previous.summary,
                    strikes=previous.strikes,
                    errors=errors[-5:],
                )

            self.state.update(snapshot)
            self._stop.wait(self.interval_seconds)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
