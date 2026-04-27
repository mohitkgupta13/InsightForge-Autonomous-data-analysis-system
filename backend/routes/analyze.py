"""
routes/analyze.py — POST /api/analyze/<session_id>
Detects problem type, trains all candidate models, selects the best.
Body (JSON, optional):
  target_col: str — column to predict (omit for clustering)
"""

import os
import pandas as pd
from flask import Blueprint, request, jsonify

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from analytics.detector import DatasetAnalyzer
from analytics.classifiers import train_classifiers
from analytics.regressors import train_regressors
from analytics.clustering import run_clustering
from analytics.model_selector import select_and_save
import database as db

analyze_bp = Blueprint("analyze", __name__)


@analyze_bp.route("/api/analyze/<session_id>", methods=["POST"])
def analyze(session_id: str):
    session = db.get_session(session_id)
    if not session:
        return jsonify({"status": "error", "message": "Session not found"}), 404

    src = session.get("cleaned_path") or session["original_path"]
    try:
        df = pd.read_csv(src)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    body = request.get_json(silent=True) or {}
    target_col = body.get("target_col") or None

    # ── Detect problem type ──────────────────────────────────────────────────
    analyzer = DatasetAnalyzer(df, target_col=target_col)
    detection = analyzer.analyze()

    problem_type = detection["problem_type"]
    feature_cols = detection["feature_columns"]
    target_col = detection["target_column"]

    # ── Train models ─────────────────────────────────────────────────────────
    if problem_type == "classification":
        metrics = train_classifiers(df, target_col, feature_cols)
    elif problem_type == "regression":
        metrics = train_regressors(df, target_col, feature_cols)
    else:
        metrics = run_clustering(df, feature_cols)

    # ── Select & save best model ─────────────────────────────────────────────
    best = select_and_save(
        session_id, problem_type, metrics if isinstance(metrics, dict) else {},
        df, target_col, feature_cols,
    )

    db.save_analysis(session_id, problem_type, best["best_model"], {
        "all_models": metrics if isinstance(metrics, dict) else metrics,
        "best": best,
        "detection": detection,
    })
    db.update_session(session_id, status="analyzed")

    return jsonify({
        "status": "success",
        "session_id": session_id,
        "data": {
            "problem_type": problem_type,
            "target_column": target_col,
            "feature_columns": feature_cols,
            "best_model": best["best_model"],
            "best_metric": best["metric"],
            "all_metrics": metrics if isinstance(metrics, dict) else metrics,
        }
    })
