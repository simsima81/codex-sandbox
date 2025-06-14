"""Feature engineering for Hanauer-style factors."""

from __future__ import annotations

import pandas as pd


def compute_features(prices: pd.DataFrame, fundamentals: pd.DataFrame) -> pd.DataFrame:
    """Return dataframe of factor exposures."""
    df = pd.DataFrame(index=prices.index)
    df["size"] = fundamentals["market_cap"].apply(lambda x: x.rank(pct=True))
    df["value"] = fundamentals["book_to_market"].rank(pct=True)
    df["momentum"] = prices.pct_change(252).rank(pct=True)
    df["quality"] = fundamentals["roa"].rank(pct=True)
    df["volatility"] = prices.pct_change().rolling(252).std().rank(pct=True)

    # interaction terms
    df["size_value"] = df["size"] * df["value"]
    df["mom_vol"] = df["momentum"] / df["volatility"].replace(0, pd.NA)
    return df


__all__ = ["compute_features"]
