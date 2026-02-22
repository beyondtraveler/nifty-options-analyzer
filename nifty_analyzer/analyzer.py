from __future__ import annotations

from datetime import datetime
from typing import Any

from nifty_analyzer.state import AnalyzerSnapshot


def _extract_strike_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in payload.get("records", {}).get("data", []):
        strike = item.get("strikePrice")
        ce = item.get("CE") or {}
        pe = item.get("PE") or {}
        row = {
            "strike": strike,
            "call": {
                "oi": ce.get("openInterest", 0),
                "change_oi": ce.get("changeinOpenInterest", 0),
                "volume": ce.get("totalTradedVolume", 0),
                "ltp": ce.get("lastPrice", 0.0),
                "price_change": ce.get("change", 0.0),
            },
            "put": {
                "oi": pe.get("openInterest", 0),
                "change_oi": pe.get("changeinOpenInterest", 0),
                "volume": pe.get("totalTradedVolume", 0),
                "ltp": pe.get("lastPrice", 0.0),
                "price_change": pe.get("change", 0.0),
            },
        }
        rows.append(row)
    return rows


def _classify_build_up(side: dict[str, Any]) -> str:
    price_up = side.get("price_change", 0) > 0 and side.get("change_oi", 0) > 0
    price_down = side.get("price_change", 0) < 0 and side.get("change_oi", 0) > 0
    if price_up:
        return "Long build-up"
    if price_down:
        return "Short build-up"
    return "None"


def analyze_option_chain(payload: dict[str, Any]) -> AnalyzerSnapshot:
    strikes = _extract_strike_rows(payload)
    if not strikes:
        return AnalyzerSnapshot(timestamp=datetime.now(), errors=["No strike data returned from NSE"])

    underlying = payload.get("records", {}).get("underlyingValue")
    if underlying is None:
        underlying = payload.get("filtered", {}).get("underlyingValue", 0)

    for row in strikes:
        row["call"]["build_up"] = _classify_build_up(row["call"])
        row["put"]["build_up"] = _classify_build_up(row["put"])

    top_call = max(strikes, key=lambda x: x["call"]["oi"]) if strikes else None
    top_put = max(strikes, key=lambda x: x["put"]["oi"]) if strikes else None

    resistance = top_call["strike"] if top_call else None
    support = top_put["strike"] if top_put else None

    ce_change = sum(r["call"]["change_oi"] for r in strikes)
    pe_change = sum(r["put"]["change_oi"] for r in strikes)

    if pe_change > ce_change * 1.1:
        bias = "Bullish"
    elif ce_change > pe_change * 1.1:
        bias = "Bearish"
    else:
        bias = "Neutral"

    atm = min(strikes, key=lambda x: abs(x["strike"] - underlying))
    atm_analysis = {
        "strike": atm["strike"],
        "call_ltp": atm["call"]["ltp"],
        "put_ltp": atm["put"]["ltp"],
        "call_oi": atm["call"]["oi"],
        "put_oi": atm["put"]["oi"],
        "call_build_up": atm["call"]["build_up"],
        "put_build_up": atm["put"]["build_up"],
    }

    summary = {
        "underlying": underlying,
        "total_call_change_oi": ce_change,
        "total_put_change_oi": pe_change,
    }

    return AnalyzerSnapshot(
        timestamp=datetime.now(),
        market_bias=bias,
        top_resistance=resistance,
        top_support=support,
        atm_analysis=atm_analysis,
        summary=summary,
        strikes=strikes,
    )
