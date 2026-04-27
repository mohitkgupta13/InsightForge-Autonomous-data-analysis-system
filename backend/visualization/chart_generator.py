"""
visualization/chart_generator.py
All 9 chart types from ARCHITECTURE.MD §3.6.
Every function saves a PNG and returns a dict:
  {"name": str, "path": str, "base64": str}
"""

import os
import base64
import io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="darkgrid", palette="muted")
FIGSIZE = (8, 5)


def _save_and_encode(fig: plt.Figure, path: str) -> str:
    """Save figure to file and return Base64 string."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=120, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close(fig)
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# ── 1. Histogram / Distribution ───────────────────────────────────────────────

def plot_distribution(col: str, series: pd.Series, out_path: str) -> dict:
    fig, ax = plt.subplots(figsize=FIGSIZE, facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")
    sns.histplot(series.dropna(), kde=True, ax=ax, color="#e94560")
    ax.set_title(f"Distribution of {col}", color="white")
    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    b64 = _save_and_encode(fig, out_path)
    return {"name": f"distribution_{col}", "path": out_path, "base64": b64}


# ── 2. Correlation Heatmap ────────────────────────────────────────────────────

def plot_correlation_heatmap(df: pd.DataFrame, out_path: str) -> dict:
    numeric = df.select_dtypes(include=[np.number])
    if numeric.shape[1] < 2:
        return {}
    corr = numeric.corr()
    fig, ax = plt.subplots(figsize=(max(8, len(corr.columns)), max(6, len(corr.columns) - 1)),
                           facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax,
                linewidths=0.5, annot_kws={"size": 8})
    ax.set_title("Correlation Heatmap", color="white")
    ax.tick_params(colors="white")
    b64 = _save_and_encode(fig, out_path)
    return {"name": "correlation_heatmap", "path": out_path, "base64": b64}


# ── 3. Bar Chart ──────────────────────────────────────────────────────────────

def plot_bar_chart(col: str, series: pd.Series, out_path: str) -> dict:
    counts = series.value_counts().head(20)
    fig, ax = plt.subplots(figsize=FIGSIZE, facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")
    sns.barplot(x=counts.index.astype(str), y=counts.values, ax=ax, palette="magma")
    ax.set_title(f"Bar Chart — {col}", color="white")
    ax.tick_params(colors="white", axis="both")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", color="white")
    ax.yaxis.label.set_color("white")
    b64 = _save_and_encode(fig, out_path)
    return {"name": f"bar_{col}", "path": out_path, "base64": b64}


# ── 4. Scatter Plot ───────────────────────────────────────────────────────────

def plot_scatter(x_col: str, y_col: str, x: pd.Series, y: pd.Series, out_path: str) -> dict:
    fig, ax = plt.subplots(figsize=FIGSIZE, facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")
    ax.scatter(x, y, alpha=0.6, color="#e94560", s=20)
    ax.set_xlabel(x_col, color="white")
    ax.set_ylabel(y_col, color="white")
    ax.set_title(f"{x_col} vs {y_col}", color="white")
    ax.tick_params(colors="white")
    b64 = _save_and_encode(fig, out_path)
    return {"name": f"scatter_{x_col}_{y_col}", "path": out_path, "base64": b64}


# ── 5. Confusion Matrix ───────────────────────────────────────────────────────

def plot_confusion_matrix(cm: list, labels: list | None, out_path: str) -> dict:
    cm_arr = np.array(cm)
    fig, ax = plt.subplots(figsize=(6, 5), facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")
    sns.heatmap(cm_arr, annot=True, fmt="d", cmap="Blues", ax=ax,
                xticklabels=labels or "auto",
                yticklabels=labels or "auto")
    ax.set_title("Confusion Matrix", color="white")
    ax.set_xlabel("Predicted", color="white")
    ax.set_ylabel("Actual", color="white")
    ax.tick_params(colors="white")
    b64 = _save_and_encode(fig, out_path)
    return {"name": "confusion_matrix", "path": out_path, "base64": b64}


# ── 6. ROC Curve ──────────────────────────────────────────────────────────────

def plot_roc_curve(fpr: list, tpr: list, auc: float, out_path: str) -> dict:
    fig, ax = plt.subplots(figsize=FIGSIZE, facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")
    ax.plot(fpr, tpr, color="#e94560", lw=2, label=f"AUC = {auc:.3f}")
    ax.plot([0, 1], [0, 1], "k--", lw=1)
    ax.set_xlabel("False Positive Rate", color="white")
    ax.set_ylabel("True Positive Rate", color="white")
    ax.set_title("ROC Curve", color="white")
    ax.legend(facecolor="#16213e", labelcolor="white")
    ax.tick_params(colors="white")
    b64 = _save_and_encode(fig, out_path)
    return {"name": "roc_curve", "path": out_path, "base64": b64}


# ── 7. Feature Importance ─────────────────────────────────────────────────────

def plot_feature_importance(importances: dict, out_path: str) -> dict:
    sorted_items = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:20]
    features, scores = zip(*sorted_items)
    fig, ax = plt.subplots(figsize=FIGSIZE, facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")
    sns.barplot(x=list(scores), y=list(features), ax=ax, palette="viridis")
    ax.set_title("Feature Importance", color="white")
    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    b64 = _save_and_encode(fig, out_path)
    return {"name": "feature_importance", "path": out_path, "base64": b64}


# ── 8. Elbow Curve ────────────────────────────────────────────────────────────

def plot_elbow_curve(inertia_curve: dict, best_k: int, out_path: str) -> dict:
    ks = sorted(inertia_curve.keys())
    vals = [inertia_curve[k] for k in ks]
    fig, ax = plt.subplots(figsize=FIGSIZE, facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")
    ax.plot(ks, vals, "o-", color="#e94560", lw=2)
    ax.axvline(best_k, color="#0f3460", linestyle="--", label=f"Best K = {best_k}")
    ax.set_xlabel("Number of Clusters (K)", color="white")
    ax.set_ylabel("Inertia", color="white")
    ax.set_title("Elbow Curve", color="white")
    ax.legend(facecolor="#16213e", labelcolor="white")
    ax.tick_params(colors="white")
    b64 = _save_and_encode(fig, out_path)
    return {"name": "elbow_curve", "path": out_path, "base64": b64}


# ── 9. Cluster Scatter ────────────────────────────────────────────────────────

def plot_cluster_scatter(df: pd.DataFrame, labels: list, out_path: str) -> dict:
    numeric = df.select_dtypes(include=[np.number])
    if numeric.shape[1] < 2:
        return {}
    col1, col2 = numeric.columns[0], numeric.columns[1]
    fig, ax = plt.subplots(figsize=FIGSIZE, facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")
    scatter = ax.scatter(numeric[col1], numeric[col2],
                         c=labels, cmap="tab10", alpha=0.7, s=20)
    ax.set_xlabel(col1, color="white")
    ax.set_ylabel(col2, color="white")
    ax.set_title("Cluster Scatter Plot", color="white")
    ax.tick_params(colors="white")
    plt.colorbar(scatter, ax=ax, label="Cluster")
    b64 = _save_and_encode(fig, out_path)
    return {"name": "cluster_scatter", "path": out_path, "base64": b64}
