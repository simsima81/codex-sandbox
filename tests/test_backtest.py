import pytest
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

pd = pytest.importorskip("pandas")
np = pytest.importorskip("numpy")
pytest.importorskip("vectorbt")

from src.backtest import run_backtest


def test_backtest_basic():
    dates = pd.date_range("2020-01-01", periods=100, freq="D")
    prices = pd.Series(np.linspace(100, 110, 100), index=dates)
    signals = pd.Series([1, -1] * 50, index=dates)
    pf = run_backtest(prices, signals)
    assert not pf.returns.isna().any()
