"""
analytics/regressors.py
Trains 5 regressors, evaluates each, returns metrics dict.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def train_regressors(
    df: pd.DataFrame,
    target_col: str,
    feature_cols: list[str],
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict:
    """
    Returns:
      {
        "ModelName": {"mae": ..., "mse": ..., "rmse": ..., "r2": ..., "cv_r2": ...}, ...
      }
    """

    X = df[feature_cols].select_dtypes(include=[np.number])
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    models = {
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(random_state=random_state),
        "Lasso": Lasso(random_state=random_state, max_iter=5000),
        "DecisionTreeRegressor": DecisionTreeRegressor(random_state=random_state),
        "RandomForestRegressor": RandomForestRegressor(n_estimators=100, random_state=random_state),
    }

    results = {}
    cv = KFold(n_splits=5, shuffle=True, random_state=random_state)

    for name, model in models.items():
        try:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

            mse = mean_squared_error(y_test, y_pred)
            results[name] = {
                "mae":   float(round(mean_absolute_error(y_test, y_pred), 4)),
                "mse":   float(round(mse, 4)),
                "rmse":  float(round(np.sqrt(mse), 4)),
                "r2":    float(round(r2_score(y_test, y_pred), 4)),
                "cv_r2": float(round(
                    cross_val_score(model, X, y, cv=cv, scoring="r2").mean(), 4
                )),
            }
        except Exception as e:
            results[name] = {"error": str(e)}

    return results
