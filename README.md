# NIFTY Options Analyzer

A Python + Flask project that fetches NSE NIFTY option-chain data every minute, detects OI/price build-up behavior, derives support/resistance levels, and presents the latest market bias on a dashboard.

## Features

- Fetches NSE option chain for `NIFTY` every 60 seconds.
- Extracts per-strike values:
  - Open Interest (OI)
  - Change in OI
  - Volume
  - Last Traded Price (LTP)
- Detects:
  - Long build-up (price up + OI up)
  - Short build-up (price down + OI up)
  - Highest call OI (resistance)
  - Highest put OI (support)
- Computes overall market bias: **Bullish / Bearish / Neutral**.
- Flask dashboard showing:
  - Current time
  - Market bias
  - Top resistance
  - Top support
  - ATM analysis

## Project Structure

```
.
├── app.py
├── requirements.txt
└── nifty_analyzer
    ├── __init__.py
    ├── analyzer.py
    ├── nse_client.py
    ├── scheduler.py
    ├── state.py
    └── templates
        └── dashboard.html
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Open: `http://127.0.0.1:5000`

## Notes

- NSE may throttle/block frequent requests without proper headers/cookies. This project uses an initial session warm-up request to improve reliability.
- If live data is unavailable, the dashboard remains available and shows the latest successful state (or a default placeholder).
