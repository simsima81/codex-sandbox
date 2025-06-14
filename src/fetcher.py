"""API fetcher with simple caching."""

import os
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

FMP_BASE = "https://financialmodelingprep.com/api/stable"
SEC_BASE = "https://data.sec.gov"
FMP_KEY = os.getenv("FMP_KEY")
SEC_AGENT = os.getenv("SEC_AGENT") or "Mozilla/5.0 (X11; Codex Bot)"
CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_path(name: str, ext: str) -> Path:
    return CACHE_DIR / f"{name}.{ext}"


def _save_json(data: Any, path: Path) -> None:
    path.write_text(json.dumps(data))


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _rate_limit(min_interval: float = 0.1) -> None:
    time.sleep(min_interval)


def fetch_json(url: str, name: str, use_cache: bool = True) -> Dict[str, Any]:
    path = _cache_path(name, "json")
    if use_cache and path.exists():
        return _load_json(path)

    _rate_limit()
    resp = requests.get(url, headers={"User-Agent": SEC_AGENT})
    resp.raise_for_status()
    data = resp.json()
    _save_json(data, path)
    return data


def fetch_fmp(endpoint: str, ticker: str, use_cache: bool = True) -> Dict[str, Any]:
    url = f"{FMP_BASE}/{endpoint}/{ticker}?apikey={FMP_KEY}"
    return fetch_json(url, f"fmp_{endpoint}_{ticker}", use_cache)


def fetch_sec(path: str, name: str, use_cache: bool = True) -> Dict[str, Any]:
    url = f"{SEC_BASE}{path}"
    return fetch_json(url, name, use_cache)


__all__ = ["fetch_fmp", "fetch_sec"]
