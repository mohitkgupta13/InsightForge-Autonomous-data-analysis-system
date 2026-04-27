"""
database.py — SQLite schema initialization and helper functions.
Tables:
  - upload_sessions : tracks each uploaded dataset
  - analysis_results: stores ML metrics per session
  - query_logs      : records NLP queries + responses
"""

import sqlite3
import json
from config import DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS upload_sessions (
            session_id   TEXT PRIMARY KEY,
            filename     TEXT NOT NULL,
            original_path TEXT NOT NULL,
            cleaned_path  TEXT,
            row_count    INTEGER,
            col_count    INTEGER,
            status       TEXT DEFAULT 'uploaded',
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS analysis_results (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id   TEXT NOT NULL,
            problem_type TEXT,
            best_model   TEXT,
            metrics_json TEXT,
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES upload_sessions(session_id)
        );

        CREATE TABLE IF NOT EXISTS query_logs (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id   TEXT NOT NULL,
            query_text   TEXT NOT NULL,
            intent       TEXT,
            response_json TEXT,
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES upload_sessions(session_id)
        );
    """)

    conn.commit()
    conn.close()
    print("[DB] Database initialized.")


# ── Session helpers ──────────────────────────────────────────────────────────

def create_session(session_id, filename, original_path, row_count, col_count):
    conn = get_connection()
    conn.execute(
        """INSERT INTO upload_sessions
           (session_id, filename, original_path, row_count, col_count, status)
           VALUES (?, ?, ?, ?, ?, 'uploaded')""",
        (session_id, filename, original_path, row_count, col_count),
    )
    conn.commit()
    conn.close()


def update_session(session_id, **kwargs):
    if not kwargs:
        return
    fields = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [session_id]
    conn = get_connection()
    conn.execute(f"UPDATE upload_sessions SET {fields} WHERE session_id = ?", values)
    conn.commit()
    conn.close()


def get_session(session_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM upload_sessions WHERE session_id = ?", (session_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


# ── Analysis helpers ─────────────────────────────────────────────────────────

def save_analysis(session_id, problem_type, best_model, metrics: dict):
    conn = get_connection()
    conn.execute(
        """INSERT INTO analysis_results
           (session_id, problem_type, best_model, metrics_json)
           VALUES (?, ?, ?, ?)""",
        (session_id, problem_type, best_model, json.dumps(metrics)),
    )
    conn.commit()
    conn.close()


def get_analysis(session_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM analysis_results WHERE session_id = ? ORDER BY created_at DESC LIMIT 1",
        (session_id,),
    ).fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["metrics"] = json.loads(d["metrics_json"])
        return d
    return None


# ── Query log helpers ────────────────────────────────────────────────────────

def log_query(session_id, query_text, intent, response: dict):
    conn = get_connection()
    conn.execute(
        """INSERT INTO query_logs (session_id, query_text, intent, response_json)
           VALUES (?, ?, ?, ?)""",
        (session_id, query_text, intent, json.dumps(response)),
    )
    conn.commit()
    conn.close()
