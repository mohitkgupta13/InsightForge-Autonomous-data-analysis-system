"""
analytics/detector.py — DatasetAnalyzer
Automatically detects the problem type (Classification / Regression / Clustering)
by inspecting the target column supplied by the user (or auto-detected).
"""

import pandas as pd
import numpy as np


class DatasetAnalyzer:
    """
    Detects problem type and recommends candidate algorithms.

    Args:
        df        : cleaned DataFrame
        target_col: name of target column (None → Clustering)
    """

    CLASSIFICATION_THRESHOLD = 20  # max unique values to be treated as classification

    def __init__(self, df: pd.DataFrame, target_col: str | None = None):
        self.df = df
        self.target_col = target_col
        self.problem_type: str = ""
        self.candidate_models: list[str] = []
        self.feature_cols: list[str] = []

    def analyze(self) -> dict:
        if self.target_col is None or self.target_col not in self.df.columns:
            return self._clustering()

        target = self.df[self.target_col]
        self.feature_cols = [c for c in self.df.columns if c != self.target_col]

        if pd.api.types.is_numeric_dtype(target):
            n_unique = target.nunique()
            if n_unique <= self.CLASSIFICATION_THRESHOLD:
                return self._classification()
            else:
                return self._regression()
        else:
            return self._classification()

    # ── Problem-type helpers ─────────────────────────────────────────────────

    def _classification(self) -> dict:
        self.problem_type = "classification"
        self.candidate_models = [
            "LogisticRegression",
            "DecisionTreeClassifier",
            "RandomForestClassifier",
            "SVC",
            "KNeighborsClassifier",
        ]
        return self._result()

    def _regression(self) -> dict:
        self.problem_type = "regression"
        self.candidate_models = [
            "LinearRegression",
            "Ridge",
            "Lasso",
            "DecisionTreeRegressor",
            "RandomForestRegressor",
        ]
        return self._result()

    def _clustering(self) -> dict:
        self.problem_type = "clustering"
        self.target_col = None
        self.feature_cols = list(self.df.columns)
        self.candidate_models = ["KMeans"]
        return self._result()

    def _result(self) -> dict:
        return {
            "problem_type": self.problem_type,
            "target_column": self.target_col,
            "feature_columns": self.feature_cols,
            "candidate_models": self.candidate_models,
            "n_samples": len(self.df),
            "n_features": len(self.feature_cols),
        }
