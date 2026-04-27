"""
analytics/classifiers.py
Trains 5 classifiers, evaluates each, returns metrics dict.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, roc_auc_score,
)
from sklearn.preprocessing import LabelEncoder


def train_classifiers(
    df: pd.DataFrame,
    target_col: str,
    feature_cols: list[str],
    test_size: float = 0.2,
    random_state: int = 42,
) -> dict:
    """
    Returns:
      {
        "ModelName": {
          "accuracy": ..., "precision": ..., "recall": ..., "f1": ...,
          "roc_auc": ...,   # binary only
          "cv_accuracy": ...,
          "confusion_matrix": [[...]],
        }, ...
      }
    """

    X = df[feature_cols].select_dtypes(include=[np.number])
    y = df[target_col]

    # Encode string targets
    le = LabelEncoder()
    y_enc = le.fit_transform(y.astype(str))
    n_classes = len(le.classes_)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=test_size, random_state=random_state, stratify=y_enc
    )

    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=random_state),
        "DecisionTreeClassifier": DecisionTreeClassifier(random_state=random_state),
        "RandomForestClassifier": RandomForestClassifier(n_estimators=100, random_state=random_state),
        "SVC": SVC(probability=True, random_state=random_state),
        "KNeighborsClassifier": KNeighborsClassifier(),
    }

    results = {}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)

    for name, model in models.items():
        try:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None

            avg = "binary" if n_classes == 2 else "weighted"
            metrics = {
                "accuracy": float(round(accuracy_score(y_test, y_pred), 4)),
                "precision": float(round(precision_score(y_test, y_pred, average=avg, zero_division=0), 4)),
                "recall": float(round(recall_score(y_test, y_pred, average=avg, zero_division=0), 4)),
                "f1": float(round(f1_score(y_test, y_pred, average=avg, zero_division=0), 4)),
                "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
                "cv_accuracy": float(round(
                    cross_val_score(model, X, y_enc, cv=cv, scoring="accuracy").mean(), 4
                )),
            }

            if y_proba is not None and n_classes == 2:
                metrics["roc_auc"] = float(round(
                    roc_auc_score(y_test, y_proba[:, 1]), 4
                ))
            elif y_proba is not None:
                metrics["roc_auc"] = float(round(
                    roc_auc_score(y_test, y_proba, multi_class="ovr", average="weighted"), 4
                ))

            results[name] = metrics
        except Exception as e:
            results[name] = {"error": str(e)}

    return results
