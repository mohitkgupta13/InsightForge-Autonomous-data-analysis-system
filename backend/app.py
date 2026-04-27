"""
app.py — InsightForge Flask Application Entry Point
Registers all blueprints and starts the development server.
"""

import sys
import os

# Make backend/ importable when running from the backend/ directory
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config import MAX_CONTENT_LENGTH
import database as db

# Blueprint imports
from routes.upload import upload_bp
from routes.preview import preview_bp
from routes.preprocess import preprocess_bp
from routes.analyze import analyze_bp
from routes.results import results_bp
from routes.visualize import visualize_bp
from routes.query import query_bp
from routes.report import report_bp

# ── App factory ───────────────────────────────────────────────────────────────

def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    # Allow requests from the frontend (served separately during dev)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize DB
    db.init_db()

    # Register blueprints
    for bp in [
        upload_bp, preview_bp, preprocess_bp,
        analyze_bp, results_bp, visualize_bp,
        query_bp, report_bp,
    ]:
        app.register_blueprint(bp)

    # Health-check endpoint
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "InsightForge API"})

    # 404 handler
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"status": "error", "message": "Endpoint not found"}), 404

    # 413 handler (file too large)
    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"status": "error", "message": "File exceeds 50 MB limit"}), 413

    return app


if __name__ == "__main__":
    application = create_app()
    print("\n🚀 InsightForge API running at http://127.0.0.1:5000\n")
    application.run(debug=True, port=5000)
