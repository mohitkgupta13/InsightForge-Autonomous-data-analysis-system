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
    @app.route("/api/health", methods=["GET", "OPTIONS"])
    def health():
        return jsonify({"status": "ok", "service": "InsightForge API"})

    # ── Serve frontend index.html at / ────────────────────────────────────
    @app.route("/", methods=["GET", "OPTIONS"])
    def serve_index():
        from flask import make_response
        resp = make_response(send_from_directory(FRONTEND_DIR, "index.html"))
        resp.headers["Cache-Control"] = "no-store"
        return resp

    # ── Serve frontend static assets (no-cache so JS/CSS changes apply instantly) ─
    @app.route("/static/<path:filename>", methods=["GET", "OPTIONS"])
    def serve_static(filename):
        from flask import make_response
        resp = make_response(
            send_from_directory(os.path.join(FRONTEND_DIR, "static"), filename)
        )
        resp.headers["Cache-Control"] = "no-store"
        return resp

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
    # Prevent joblib/sklearn multiprocessing from crashing or triggering Flask reloader on Windows
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["LOKY_MAX_CPU_COUNT"] = "1"
    os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"

    application = create_app()
    print("\n[InsightForge] Open http://127.0.0.1:5000 in your browser\n")
    # Disable debug mode because the Flask debugger and reloader clash with joblib multiprocessing on Windows
    application.run(debug=False, port=5000)
