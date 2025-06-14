"""Machine learning model to predict expected returns."""

from __future__ import annotations

import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from lightgbm import LGBMRegressor


class MispricingModel:
    def __init__(self, n_splits: int = 60):
        self.n_splits = n_splits
        self.scaler = StandardScaler()
        self.model = LGBMRegressor()

    def fit_predict(self, X: pd.DataFrame, y: pd.Series) -> pd.Series:
        """Rolling fit and predict using expanding window."""
        preds = pd.Series(index=y.index, dtype=float)
        tscv = TimeSeriesSplit(n_splits=self.n_splits)
        for train_idx, test_idx in tscv.split(X):
            X_train = self.scaler.fit_transform(X.iloc[train_idx])
            y_train = y.iloc[train_idx]
            self.model.fit(X_train, y_train)
            X_test = self.scaler.transform(X.iloc[test_idx])
            preds.iloc[test_idx] = self.model.predict(X_test)
        return preds


__all__ = ["MispricingModel"]
