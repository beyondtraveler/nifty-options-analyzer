from __future__ import annotations

from datetime import datetime

from flask import Flask, render_template

from nifty_analyzer.scheduler import AnalyzerScheduler
from nifty_analyzer.state import SharedState

app = Flask(__name__, template_folder="nifty_analyzer/templates")
state = SharedState()
scheduler = AnalyzerScheduler(state=state, interval_seconds=60)
scheduler.start()


@app.route("/")
def dashboard() -> str:
    snapshot = state.get()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template("dashboard.html", snapshot=snapshot, current_time=current_time)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
