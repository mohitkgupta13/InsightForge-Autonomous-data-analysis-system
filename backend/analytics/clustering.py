"""
analytics/clustering.py
K-Means clustering with automatic K selection via the Elbow Method.
Returns cluster labels, inertia per K, silhouette score.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


def run_clustering(
    df: pd.DataFrame,
    feature_cols: list[str],
    k_min: int = 2,
    k_max: int = 10,
    random_state: int = 42,
) -> dict:
    """
    Returns:
      {
        "best_k": int,
        "silhouette_score": float,
        "inertia_curve": {k: inertia, ...},
        "labels": [int, ...],
        "cluster_centers": [[...], ...]
      }
    """

    X = df[feature_cols].select_dtypes(include=[np.number]).dropna()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    k_max = min(k_max, len(X) - 1)

    inertia_curve = {}
    for k in range(k_min, k_max + 1):
        km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        km.fit(X_scaled)
        inertia_curve[k] = float(round(km.inertia_, 4))

    # Elbow via largest second-derivative
    ks = sorted(inertia_curve.keys())
    inertias = [inertia_curve[k] for k in ks]
    if len(ks) >= 3:
        second_deriv = np.diff(np.diff(inertias))
        best_k = ks[int(np.argmax(second_deriv)) + 1]
    else:
        best_k = ks[0]

    # Final fit
    final_km = KMeans(n_clusters=best_k, random_state=random_state, n_init=10)
    labels = final_km.fit_predict(X_scaled)
    sil = float(round(silhouette_score(X_scaled, labels), 4)) if best_k > 1 else 0.0

    return {
        "best_k": int(best_k),
        "silhouette_score": sil,
        "inertia_curve": inertia_curve,
        "labels": labels.tolist(),
        "cluster_centers": final_km.cluster_centers_.tolist(),
    }
