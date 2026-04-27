"""
routes/visualize.py — GET /api/visualize/<session_id>
Generates (or re-fetches) all charts for the session.
"""

import os
import pandas as pd
from flask import Blueprint, jsonify

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import database as db
from visualization.manager import VisualizationManager

visualize_bp = Blueprint("visualize", __name__)


@visualize_bp.route("/api/visualize/<session_id>", methods=["GET"])
def visualize(session_id: str):
    session = db.get_session(session_id)
    if not session:
        return jsonify({"status": "error", "message": "Session not found"}), 404

    analysis = db.get_analysis(session_id)
    if not analysis:
        return jsonify({"status": "error", "message": "Run /api/analyze first"}), 400

    src = session.get("cleaned_path") or session["original_path"]
    try:
        df = pd.read_csv(src)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    manager = VisualizationManager(session_id, df, analysis)
    charts = manager.generate_all()

    # Strip file paths from response (send only name + base64)
    clean = [{"name": c["name"], "base64": c["base64"]} for c in charts if c]

    return jsonify({
        "status": "success",
        "session_id": session_id,
        "data": {
            "charts": clean,
            "count": len(clean),
        }
    })
