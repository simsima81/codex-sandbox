#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CANSLIM Stock Screener – FMP Ultimate Edition
Author : Codex + ChatGPT ‘대박’
Date   : 2025-07-05
License: MIT
"""

from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
from dotenv import load_dotenv
from tqdm import tqdm
import concurrent.futures as cf

load_dotenv()

FMP_KEY: str | None = os.getenv("FMP_KEY")
if not FMP_KEY:
    raise RuntimeError("FMP_KEY not found")

BASE_URL = "https://financialmodelingprep.com/api/v3"
HEADERS = {"User-Agent": "canslim-bot/1.1 (+https://github.com/yourrepo)"}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def _get(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    retry: int = 3,
    timeout: int = 30,
) -> Any:
    """GET wrapper with retry and API key."""
    if params is None:
        params = {}
    params["apikey"] = FMP_KEY
    url = f"{BASE_URL}/{endpoint}"
    for _ in range(retry):
        try:
            resp = SESSION.get(url, params=params, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
        except requests.RequestException:
            pass
        time.sleep(1.5)
    raise RuntimeError(
        f"FMP API fail: {url} :: {resp.status_code} :: {resp.text[:200]}"
    )


def get_universe() -> List[str]:
    """Return active tickers on NASDAQ, NYSE and AMEX."""
    data = _get("listing_status", {"exchange": "NASDAQ,NYSE,AMEX", "status": "Active"})
    return [d["symbol"] for d in data if d.get("status") == "Active"]


def fetch_ticker_data(ticker: str) -> Optional[Dict[str, Any]]:
    """Collect metrics required for CANSLIM rules."""
    out: Dict[str, Any] = {"symbol": ticker}

    q_inc = _get(
        f"income-statement/{ticker}",
        {"period": "quarter", "limit": 8},
    )
    a_inc = _get(
        f"income-statement/{ticker}",
        {"period": "annual", "limit": 6},
    )
    if not q_inc or not a_inc:
        return None

    try:
        eps_now = q_inc[0]["eps"]
        eps_ly = q_inc[4]["eps"]
        if eps_now <= 0 or eps_ly <= 0:
            return None
        out["C_eps_yoy"] = eps_now / eps_ly - 1
    except (KeyError, IndexError, TypeError):
        return None

    try:
        eps_last = a_inc[0]["eps"]
        eps_3y = a_inc[3]["eps"]
        if eps_last <= 0 or eps_3y <= 0:
            return None
        out["A_eps_cagr3"] = (eps_last / eps_3y) ** (1 / 3) - 1
    except (KeyError, IndexError, TypeError):
        return None

    profile = _get(f"profile/{ticker}")
    if not profile:
        return None
    shares_float = profile[0].get("floatShares") or profile[0].get("sharesOutstanding")
    if not shares_float:
        return None
    out["S_float"] = shares_float

    price_hist = _get(
        f"historical-price-full/{ticker}",
        {"serietype": "line", "timeseries": 250},
    )
    if not price_hist or "historical" not in price_hist:
        return None
    prices = pd.DataFrame(price_hist["historical"]).sort_values("date")
    prices["close"] = pd.to_numeric(prices["close"], errors="coerce")
    if "volume" not in prices:
        return None
    prices["volume"] = pd.to_numeric(prices["volume"], errors="coerce")
    if prices["close"].isna().all():
        return None
    close_series = prices["close"].astype(float)
    vol_series = prices["volume"].astype(float)
    last_close = close_series.iloc[-1]
    sma50 = close_series.rolling(50).mean().iloc[-1]
    sma200 = close_series.rolling(200).mean().iloc[-1]
    vol50 = vol_series.rolling(50).mean().iloc[-1]
    vol200 = vol_series.rolling(200).mean().iloc[-1]
    out.update(
        {
            "last_close": last_close,
            "sma50": sma50,
            "sma200": sma200,
            "vol50": vol50,
            "vol200": vol200,
        }
    )

    inst = _get(f"institutional-ownership/{ticker}")
    if inst and len(inst) >= 2:
        latest, prev = inst[0], inst[1]
        if prev.get("shares"):
            out["I_change_pct"] = (latest.get("shares", 0) - prev["shares"]) / prev[
                "shares"
            ]

    return out


def canslim_filter(data: Dict[str, Any]) -> bool:
    """Return True if ticker satisfies CANSLIM rules."""
    if data.get("C_eps_yoy", -1) < 0.25:
        return False
    if data.get("A_eps_cagr3", -1) < 0.20:
        return False
    if data.get("S_float", float("inf")) > 500_000_000:
        return False
    if data.get("vol50", 0) <= data.get("vol200", 0):
        return False
    if not (data["last_close"] > data["sma50"] > data["sma200"]):
        return False
    if data.get("I_change_pct") is not None and data["I_change_pct"] <= 0:
        return False
    return True


def main() -> None:
    """Run the screener and print results."""
    universe = get_universe()
    results: List[Dict[str, Any]] = []

    with cf.ThreadPoolExecutor(max_workers=16) as ex:
        for data in tqdm(
            ex.map(fetch_ticker_data, universe),
            total=len(universe),
        ):
            if data and canslim_filter(data):
                results.append(data)

    if not results:
        print("Found 0 tickers")
        return

    df = pd.DataFrame(results).sort_values("C_eps_yoy", ascending=False)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_csv = f"canslim_{ts}.csv"
    df.to_csv(out_csv, index=False)

    print(f"Found {len(df)} tickers -> {out_csv}")
    pd.set_option("display.float_format", lambda x: f"{x:.2%}")
    print(
        df[["symbol", "C_eps_yoy", "A_eps_cagr3", "I_change_pct"]].to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
