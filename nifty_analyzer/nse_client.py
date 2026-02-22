from __future__ import annotations

from typing import Any

import requests


NSE_BASE = "https://www.nseindia.com"
OPTION_CHAIN_API = f"{NSE_BASE}/api/option-chain-indices?symbol=NIFTY"


class NSEClient:
    def __init__(self, timeout: int = 15) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json,text/plain,*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": f"{NSE_BASE}/option-chain",
                "Connection": "keep-alive",
            }
        )

    def warm_up(self) -> None:
        self.session.get(f"{NSE_BASE}/option-chain", timeout=self.timeout)

    def fetch_option_chain(self) -> dict[str, Any]:
        self.warm_up()
        response = self.session.get(OPTION_CHAIN_API, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
