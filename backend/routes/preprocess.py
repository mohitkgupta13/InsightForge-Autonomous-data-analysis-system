"""
routes/preprocess.py — POST /api/preprocess/<session_id>
Runs the full preprocessing pipeline and saves the cleaned CSV.
Body (JSON, all optional):
  missing_strategy : "mean" | "median" | "mode" | "drop"
  outlier_method   : "iqr" | "zscore" | "none"
  encoding_method  : "onehot" | "label"
  scaling_method   : "standard" | "minmax" | "none"
"""

import os
import pandas as pd
from flask import Blueprint, request, jsonify

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import OUTPUT_DIR
from preprocessing.pipeline import PreprocessingPipeline
import database as db

preprocess_bp = Blueprint("preprocess", __name__)


@preprocess_bp.route("/api/preprocess/<session_id>", methods=["POST"])
def preprocess(session_id: str):
    session = db.get_session(session_id)
    if not session:
        return jsonify({"status": "error", "message": "Session not found"}), 404

    body = request.get_json(silent=True) or {}

    pipeline = PreprocessingPipeline(
        missing_strategy=body.get("missing_strategy", "mean"),
        outlier_method=body.get("outlier_method", "iqr"),
        encoding_method=body.get("encoding_method", "onehot"),
        scaling_method=body.get("scaling_method", "standard"),
    )

    src = session["original_path"]
    try:
        if src.endswith(".csv"):
            df = pd.read_csv(src, encoding="utf-8", on_bad_lines="skip")
        else:
            df = pd.read_excel(src)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Could not read file: {e}"}), 500

    cleaned_df = pipeline.run(df)
    report = pipeline.get_report()

    # Save cleaned CSV
    cleaned_path = os.path.join(OUTPUT_DIR, f"{session_id}_cleaned.csv")
    cleaned_df.to_csv(cleaned_path, index=False)

    db.update_session(
        session_id,
        cleaned_path=cleaned_path,
        row_count=cleaned_df.shape[0],
        col_count=cleaned_df.shape[1],
        status="preprocessed",
    )

    return jsonify({
        "status": "success",
        "session_id": session_id,
        "data": {
            "report": report,
            "cleaned_shape": report["cleaned_shape"],
            "cleaned_path": cleaned_path,
        }
    })
