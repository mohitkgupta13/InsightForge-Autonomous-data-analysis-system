"""
visualization/manager.py — VisualizationManager
Auto-selects which charts to generate based on problem type + dataset properties.
"""

import os
import numpy as np
import pandas as pd
import json

from visualization.chart_generator import (
    plot_distribution,
    plot_correlation_heatmap,
    plot_bar_chart,
    plot_scatter,
    plot_confusion_matrix,
    plot_feature_importance,
    plot_elbow_curve,
    plot_cluster_scatter,
)

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import CHARTS_DIR


class VisualizationManager:

    def __init__(self, session_id: str, df: pd.DataFrame, analysis: dict):
        self.session_id = session_id
        self.df = df
        self.analysis = analysis  # from db.get_analysis()
        self.charts: list[dict] = []

    def _path(self, name: str) -> str:
        return os.path.join(CHARTS_DIR, self.session_id, f"{name}.png")

    def generate_all(self) -> list[dict]:
        metrics = self.analysis.get("metrics", {})
        problem_type = self.analysis.get("problem_type", "")
        all_model_metrics = metrics.get("all_models", {})
        detection = metrics.get("detection", {})
        feature_cols = detection.get("feature_columns", list(self.df.columns))
        target_col = detection.get("target_column")

        os.makedirs(os.path.join(CHARTS_DIR, self.session_id), exist_ok=True)

        # Numeric distributions (up to 5 columns)
        numeric_cols = self.df[feature_cols].select_dtypes(include=[np.number]).columns.tolist()
        for col in numeric_cols[:5]:
            c = plot_distribution(col, self.df[col], self._path(f"dist_{col}"))
            if c:
                self.charts.append(c)

        # Correlation heatmap
        c = plot_correlation_heatmap(self.df[feature_cols], self._path("corr_heatmap"))
        if c:
            self.charts.append(c)

        # Categorical bar charts (up to 3)
        cat_cols = self.df[feature_cols].select_dtypes(include=["object", "category"]).columns.tolist()
        for col in cat_cols[:3]:
            c = plot_bar_chart(col, self.df[col], self._path(f"bar_{col}"))
            if c:
                self.charts.append(c)

        if problem_type == "regression" and target_col and numeric_cols:
            x_col = numeric_cols[0]
            c = plot_scatter(x_col, target_col, self.df[x_col], self.df[target_col],
                             self._path(f"scatter_{x_col}_{target_col}"))
            if c:
                self.charts.append(c)

        if problem_type == "classification":
            best_name = metrics.get("best", {}).get("best_model")
            if best_name and best_name in all_model_metrics:
                bm = all_model_metrics[best_name]
                if "confusion_matrix" in bm:
                    c = plot_confusion_matrix(bm["confusion_matrix"], None,
                                              self._path("confusion_matrix"))
                    if c:
                        self.charts.append(c)

            # Feature importance for tree-based models
            best_model_path = metrics.get("best", {}).get("model_path")
            if best_model_path and os.path.exists(best_model_path):
                try:
                    import joblib
                    model = joblib.load(best_model_path)
                    if hasattr(model, "feature_importances_"):
                        imp = dict(zip(
                            self.df[feature_cols].select_dtypes(include=[np.number]).columns,
                            model.feature_importances_,
                        ))
                        c = plot_feature_importance(imp, self._path("feature_importance"))
                        if c:
                            self.charts.append(c)
                except Exception:
                    pass

        if problem_type == "clustering":
            inertia_curve = all_model_metrics.get("inertia_curve", {})
            best_k = all_model_metrics.get("best_k", 2)
            labels = all_model_metrics.get("labels", [])

            if inertia_curve:
                c = plot_elbow_curve(
                    {int(k): v for k, v in inertia_curve.items()},
                    best_k,
                    self._path("elbow_curve"),
                )
                if c:
                    self.charts.append(c)

            if labels:
                c = plot_cluster_scatter(self.df[feature_cols], labels,
                                         self._path("cluster_scatter"))
                if c:
                    self.charts.append(c)

        return self.charts
