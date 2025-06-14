"""Backtesting utilities using vectorbt."""

from __future__ import annotations

import pandas as pd
import vectorbt as vbt


def run_backtest(
    prices: pd.Series, signals: pd.Series, fee: float = 0.0015
) -> vbt.Portfolio:
    """Run monthly rebalanced long/short portfolio."""
    entries = signals.shift(1).fillna(0) > 0
    exits = signals.shift(1).fillna(0) < 0
    pf = vbt.Portfolio.from_signals(
        prices,
        entries,
        exits,
        freq="1D",
        fees=fee,
        slippage=0.0005,
    )
    return pf


__all__ = ["run_backtest"]
