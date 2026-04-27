"""
routes/upload.py — POST /api/upload
Accepts a CSV or Excel file, saves it, creates a session, returns session_id.
"""

import os
import uuid
import pandas as pd
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import UPLOAD_DIR, ALLOWED_EXTENSIONS
import database as db

upload_bp = Blueprint("upload", __name__)


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/api/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file part in request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "No file selected"}), 400

    if not _allowed(file.filename):
        return jsonify({
            "status": "error",
            "message": f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400

    session_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_DIR, f"{session_id}_{filename}")
    file.save(save_path)

    # Read to get shape
    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(save_path, encoding="utf-8", on_bad_lines="skip")
        else:
            df = pd.read_excel(save_path)
    except Exception as e:
        os.remove(save_path)
        return jsonify({"status": "error", "message": f"Could not parse file: {str(e)}"}), 422

    rows, cols = df.shape
    db.create_session(session_id, filename, save_path, rows, cols)

    return jsonify({
        "status": "success",
        "session_id": session_id,
        "data": {
            "filename": filename,
            "rows": rows,
            "columns": cols,
            "column_names": list(df.columns),
        }
    }), 201
