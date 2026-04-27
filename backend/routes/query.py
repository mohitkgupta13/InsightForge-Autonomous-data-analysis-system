"""
routes/query.py — POST /api/query/<session_id>
Body: {"query": "Show me rows where Age > 30"}
"""

import os
import pandas as pd
from flask import Blueprint, request, jsonify

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import database as db
from nlp.query_executor import execute_query
from config import CHARTS_DIR

query_bp = Blueprint("query", __name__)


@query_bp.route("/api/query/<session_id>", methods=["POST"])
def nlp_query(session_id: str):
    session = db.get_session(session_id)
    if not session:
        return jsonify({"status": "error", "message": "Session not found"}), 404

    body = request.get_json(silent=True) or {}
    query_text = body.get("query", "").strip()
    if not query_text:
        return jsonify({"status": "error", "message": "No query provided"}), 400

    src = session.get("cleaned_path") or session["original_path"]
    try:
        df = pd.read_csv(src)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    result = execute_query(query_text, df, session_id, CHARTS_DIR)

    db.log_query(session_id, query_text, result.get("intent"), result)

    return jsonify({
        "status": "success",
        "session_id": session_id,
        "data": result,
    })
