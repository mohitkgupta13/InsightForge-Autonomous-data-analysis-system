"""
analytics/model_selector.py
Ranks all trained models by their primary metric and returns the best one.
Also serializes the best model to models_store/ via joblib.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import MODELS_DIR


_CLASSIFIER_MAP = {
    "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
    "DecisionTreeClassifier": DecisionTreeClassifier(random_state=42),
    "RandomForestClassifier": RandomForestClassifier(n_estimators=100, random_state=42),
    "SVC": SVC(probability=True, random_state=42),
    "KNeighborsClassifier": KNeighborsClassifier(),
}

_REGRESSOR_MAP = {
    "LinearRegression": LinearRegression(),
    "Ridge": Ridge(random_state=42),
    "Lasso": Lasso(random_state=42, max_iter=5000),
    "DecisionTreeRegressor": DecisionTreeRegressor(random_state=42),
    "RandomForestRegressor": RandomForestRegressor(n_estimators=100, random_state=42),
}


def select_and_save(
    session_id: str,
    problem_type: str,
    metrics: dict,
    df: pd.DataFrame,
    target_col: str | None,
    feature_cols: list[str],
) -> dict:
    """
    Picks best model by primary metric, retrains on full data, serializes.

    Returns:
      {"best_model": str, "metric": float, "model_path": str}
    """

    if problem_type == "clustering":
        return {"best_model": "KMeans", "metric": None, "model_path": None}

    # Choose primary sort metric
    primary = "accuracy" if problem_type == "classification" else "r2"

    # Filter out errored models
    valid = {
        name: vals for name, vals in metrics.items()
        if isinstance(vals, dict) and primary in vals
    }
    if not valid:
        return {"best_model": None, "metric": None, "model_path": None}

    best_name = max(valid, key=lambda n: valid[n][primary])
    best_metric = valid[best_name][primary]

    # Retrain on full dataset
    X = df[feature_cols].select_dtypes(include=[np.number])

    if problem_type == "classification":
        le = LabelEncoder()
        y = le.fit_transform(df[target_col].astype(str))
        model_proto = _CLASSIFIER_MAP.get(best_name)
    else:
        y = df[target_col].values
        model_proto = _REGRESSOR_MAP.get(best_name)

    if model_proto is None:
        return {"best_model": best_name, "metric": best_metric, "model_path": None}

    model_proto.fit(X, y)

    model_path = os.path.join(MODELS_DIR, f"{session_id}_best_model.joblib")
    joblib.dump(model_proto, model_path)

    return {
        "best_model": best_name,
        "metric": best_metric,
        "model_path": model_path,
    }
