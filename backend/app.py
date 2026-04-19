"""
Snake Arcade – Flask Backend (Production Ready)
Render deployment: gunicorn app:app
Local development: python app.py
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# ─── App + CORS ───────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app, origins="*")   # allow all origins (tighten in production)

# ─── Database ─────────────────────────────────────────────────────────────────
# On Render with a persistent disk, set DB_PATH env var to e.g.
# /opt/render/project/src/snake_arcade.db
# Locally it just creates snake_arcade.db in the backend/ folder.
DB_PATH = os.environ.get("DB_PATH", "snake_arcade.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables. Called once at module load so Gunicorn sees it too."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT    NOT NULL,
                score     INTEGER NOT NULL,
                level     INTEGER NOT NULL DEFAULT 1,
                timestamp TEXT    NOT NULL
            )
        """)
        conn.commit()
    print("✅ Database ready:", DB_PATH)


# ── Run init_db() at module level so it works under both
#    'python app.py'  AND  'gunicorn app:app'
init_db()


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def health():
    """Render keep-alive + quick sanity check."""
    return jsonify({"status": "ok", "message": "Snake Arcade API is running 🐍"})


@app.route("/submit", methods=["POST"])
def submit_score():
    """
    POST /submit
    JSON body: { "name": "Alice", "score": 150, "level": 3 }
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON body required"}), 400

    name  = str(data.get("name", "")).strip()
    score = data.get("score")
    level = data.get("level", 1)

    # Validation
    if not name:
        return jsonify({"error": "name is required"}), 400
    if len(name) > 30:
        return jsonify({"error": "name max 30 chars"}), 400
    if not isinstance(score, (int, float)) or score < 0:
        return jsonify({"error": "score must be a non-negative number"}), 400

    score     = int(score)
    level     = int(level) if isinstance(level, (int, float)) else 1
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO players (name, score, level, timestamp) VALUES (?, ?, ?, ?)",
            (name, score, level, timestamp)
        )
        conn.commit()

    return jsonify({
        "message": "Score saved!",
        "entry": {"id": cursor.lastrowid, "name": name, "score": score, "level": level}
    }), 201


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    """
    GET /leaderboard?limit=10
    Returns each player's personal best, sorted highest first.
    """
    try:
        limit = max(1, min(int(request.args.get("limit", 10)), 100))
    except (ValueError, TypeError):
        limit = 10

    with get_db() as conn:
        rows = conn.execute("""
            SELECT   name,
                     MAX(score)     AS score,
                     MAX(level)     AS level,
                     MAX(timestamp) AS timestamp
            FROM     players
            GROUP BY LOWER(name)
            ORDER BY score DESC
            LIMIT    ?
        """, (limit,)).fetchall()

    return jsonify({
        "leaderboard": [
            {
                "rank":      i + 1,
                "name":      r["name"],
                "score":     r["score"],
                "level":     r["level"],
                "timestamp": r["timestamp"],
            }
            for i, r in enumerate(rows)
        ],
        "count": len(rows)
    })


# ─── Local dev entry point ────────────────────────────────────────────────────
# Gunicorn (Render) never runs this block — it imports app directly.
# use_reloader=False stops the "SystemExit: 3" crash in VS Code debugger.

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=True,
        use_reloader=False,
        threaded=True,
    )
