"""Generate long/short signals based on mispricing."""

from __future__ import annotations

import pandas as pd


def generate_signals(preds: pd.Series) -> pd.Series:
    """Return +1/-1 signals based on decile ranks."""
    mispricing = preds - preds.mean()
    ranks = mispricing.rank(pct=True)
    signals = pd.Series(0, index=preds.index)
    signals[ranks >= 0.9] = 1
    signals[ranks <= 0.1] = -1
    return signals


__all__ = ["generate_signals"]
