import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")

DB_PATH = os.environ.get("DB_PATH", "snake_arcade.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                score INTEGER NOT NULL,
                level INTEGER NOT NULL DEFAULT 1,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()

# 🔥 VERY IMPORTANT → RUN ALWAYS
init_db()


@app.route("/")
def home():
    return jsonify({"status": "ok"})


@app.route("/submit", methods=["POST"])
def submit_score():
    data = request.get_json()

    name = data.get("name")
    score = int(data.get("score"))
    level = int(data.get("level", 1))

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO players (name, score, level, timestamp) VALUES (?, ?, ?, ?)",
            (name, score, level, timestamp)
        )
        conn.commit()

    return jsonify({"message": "saved"})


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    with get_db() as conn:
        rows = conn.execute("""
            SELECT name, MAX(score) as score, MAX(level) as level
            FROM players
            GROUP BY name
            ORDER BY score DESC
            LIMIT 10
        """).fetchall()

    result = []
    for i, row in enumerate(rows):
        result.append({
            "rank": i + 1,
            "name": row["name"],
            "score": row["score"],
            "level": row["level"]
        })

    return jsonify({"leaderboard": result})













