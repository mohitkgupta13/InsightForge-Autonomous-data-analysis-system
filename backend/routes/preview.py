"""
routes/preview.py — GET /api/preview/<session_id>
Returns first N rows + column info of the uploaded dataset.
"""

import os
import pandas as pd
from flask import Blueprint, jsonify, request

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import PREVIEW_ROWS
import database as db

preview_bp = Blueprint("preview", __name__)


@preview_bp.route("/api/preview/<session_id>", methods=["GET"])
def preview(session_id: str):
    session = db.get_session(session_id)
    if not session:
        return jsonify({"status": "error", "message": "Session not found"}), 404

    path = session["cleaned_path"] or session["original_path"]
    n = int(request.args.get("rows", PREVIEW_ROWS))

    try:
        if path.endswith(".csv"):
            df = pd.read_csv(path, nrows=n)
        else:
            df = pd.read_excel(path, nrows=n)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    # Column summary
    col_info = []
    for col in df.columns:
        col_info.append({
            "name": col,
            "dtype": str(df[col].dtype),
            "missing": int(df[col].isnull().sum()),
            "unique": int(df[col].nunique()),
        })

    return jsonify({
        "status": "success",
        "session_id": session_id,
        "data": {
            "rows": df.replace({float("nan"): None}).to_dict(orient="records"),
            "columns": col_info,
            "total_rows": session["row_count"],
            "total_cols": session["col_count"],
        }
    })
