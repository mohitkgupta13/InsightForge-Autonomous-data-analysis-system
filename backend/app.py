"""
app.py — InsightForge Flask Application Entry Point
Serves frontend at http://127.0.0.1:5000/ and API at /api/*
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config import MAX_CONTENT_LENGTH
import database as db

from routes.upload import upload_bp
from routes.preview import preview_bp
from routes.preprocess import preprocess_bp
from routes.analyze import analyze_bp
from routes.results import results_bp
from routes.visualize import visualize_bp
from routes.query import query_bp
from routes.report import report_bp

# Absolute path to the frontend folder
FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    CORS(app, origins="*")   # allow all origins in dev
    db.init_db()

    # ── API blueprints ──────────────────────────────────────────────────────
    for bp in [upload_bp, preview_bp, preprocess_bp,
               analyze_bp, results_bp, visualize_bp,
               query_bp, report_bp]:
        app.register_blueprint(bp)

    # ── Health check ────────────────────────────────────────────────────────
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "InsightForge API"})

    # ── Serve frontend index.html at / ──────────────────────────────────────
    @app.route("/")
    def serve_index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    # ── Serve frontend static assets ────────────────────────────────────────
    @app.route("/static/<path:filename>")
    def serve_static(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, "static"), filename)

    # ── Error handlers ──────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"status": "error", "message": "Endpoint not found"}), 404

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"status": "error", "message": "File exceeds 50 MB limit"}), 413

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"status": "error", "message": f"Internal server error: {e}"}), 500

    return app


if __name__ == "__main__":
    application = create_app()
    print("\n[InsightForge] Open http://127.0.0.1:5000 in your browser\n")
    application.run(debug=True, port=5000, use_reloader=True)
