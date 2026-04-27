"""
routes/results.py — GET /api/results/<session_id>
Returns the stored analysis results for a session.
"""

import os
from flask import Blueprint, jsonify

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import database as db

results_bp = Blueprint("results", __name__)


@results_bp.route("/api/results/<session_id>", methods=["GET"])
def results(session_id: str):
    session = db.get_session(session_id)
    if not session:
        return jsonify({"status": "error", "message": "Session not found"}), 404

    analysis = db.get_analysis(session_id)
    if not analysis:
        return jsonify({"status": "error", "message": "No analysis found for this session"}), 404

    return jsonify({
        "status": "success",
        "session_id": session_id,
        "data": {
            "problem_type": analysis["problem_type"],
            "best_model": analysis["best_model"],
            "metrics": analysis["metrics"],
            "created_at": analysis["created_at"],
        }
    })
