"""
Snake Arcade – Flask Backend
REST API for score submission and leaderboard retrieval.
Database: SQLite (swap DATABASE_URL env var for PostgreSQL in production)
"""

import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# ─── CORS ────────────────────────────────────────────────────────────────────
# Allows the frontend (any origin) to call the API in development.
# In production replace "*" with your Netlify domain:
#   CORS(app, origins=["https://your-app.netlify.app"])
CORS(app, origins="*")

# ─── Database ────────────────────────────────────────────────────────────────
DB_PATH = os.environ.get("DB_PATH", "snake_arcade.db")


def get_db():
    """Return a database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # allows dict-style access: row["name"]
    return conn


def init_db():
    """Create the players table if it does not exist yet."""
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
    print("✅  Database initialised.")


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET"])
def health():
    """Health-check endpoint – useful for Render keep-alive pings."""
    return jsonify({"status": "ok", "message": "Snake Arcade API is running 🐍"})


@app.route("/submit", methods=["POST"])
def submit_score():
    """
    POST /submit
    Body (JSON): { "name": "Alice", "score": 120, "level": 3 }
    Returns the saved entry with its auto-generated id.
    """
    data = request.get_json(silent=True)

    # ── Input validation ─────────────────────────────────────────────────────
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    name  = str(data.get("name", "")).strip()
    score = data.get("score")
    level = data.get("level", 1)

    if not name:
        return jsonify({"error": "Player name is required"}), 400
    if len(name) > 30:
        return jsonify({"error": "Name must be 30 characters or fewer"}), 400
    if not isinstance(score, (int, float)) or score < 0:
        return jsonify({"error": "Score must be a non-negative number"}), 400

    score     = int(score)
    level     = int(level) if isinstance(level, (int, float)) else 1
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # ── Insert into database ──────────────────────────────────────────────────
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO players (name, score, level, timestamp) VALUES (?, ?, ?, ?)",
            (name, score, level, timestamp)
        )
        conn.commit()
        entry_id = cursor.lastrowid

    return jsonify({
        "message": "Score submitted successfully!",
        "entry": {
            "id":        entry_id,
            "name":      name,
            "score":     score,
            "level":     level,
            "timestamp": timestamp,
        }
    }), 201


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    """
    GET /leaderboard?limit=10
    Returns top N unique players ordered by personal best score.
    Query param: limit (1-100, default 10)
    """
    limit = request.args.get("limit", 10)
    try:
        limit = max(1, min(int(limit), 100))
    except ValueError:
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

    board = [
        {
            "rank":      i + 1,
            "name":      row["name"],
            "score":     row["score"],
            "level":     row["level"],
            "timestamp": row["timestamp"],
        }
        for i, row in enumerate(rows)
    ]

    return jsonify({"leaderboard": board, "count": len(board)})


@app.route("/leaderboard/<string:name>", methods=["GET"])
def player_scores(name):
    """
    GET /leaderboard/<name>
    Returns all score entries for one player (case-insensitive).
    """
    with get_db() as conn:
        rows = conn.execute("""
            SELECT id, name, score, level, timestamp
            FROM   players
            WHERE  LOWER(name) = LOWER(?)
            ORDER  BY score DESC
        """, (name,)).fetchall()

    if not rows:
        return jsonify({"error": f"No entries found for player '{name}'"}), 404

    return jsonify({
        "player":  name,
        "entries": [dict(r) for r in rows],
    })


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()

    port   = int(os.environ.get("PORT", 5001))
    is_dev = os.environ.get("FLASK_ENV") != "production"

    # FIX: use_reloader=False  → stops "SystemExit: 3" in VS Code debugger.
    #      debugpy conflicts with Flask's built-in file-watcher reloader.
    # FIX: threaded=True       → handles simultaneous fetch() calls from
    #      the browser (leaderboard + submit) without blocking.
    app.run(
        host="0.0.0.0",
        port=port,
        debug=is_dev,
        use_reloader=False,
        threaded=True,
    )
