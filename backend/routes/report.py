"""
routes/report.py — GET /api/report/<session_id>
Returns a complete JSON analysis report.
"""

import os
from flask import Blueprint, jsonify

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import database as db

report_bp = Blueprint("report", __name__)


@report_bp.route("/api/report/<session_id>", methods=["GET"])
def report(session_id: str):
    session = db.get_session(session_id)
    if not session:
        return jsonify({"status": "error", "message": "Session not found"}), 404

    analysis = db.get_analysis(session_id)

    conn = db.get_connection()
    queries = conn.execute(
        "SELECT query_text, intent, response_json FROM query_logs WHERE session_id = ?",
        (session_id,)
    ).fetchall()
    conn.close()

    return jsonify({
        "status": "success",
        "session_id": session_id,
        "data": {
            "session": session,
            "analysis": analysis,
            "query_history": [dict(q) for q in queries],
        }
    })
