from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import os


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

CORS(app)


# ============================================================
# DATABASE PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "events.db"
)


# ============================================================
# GET DATABASE CONNECTION
# ============================================================

def get_db_connection():

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# GET ALL EVENTS
# ============================================================

@app.route("/api/events", methods=["GET"])
def get_events():

    conn = get_db_connection()

    events = conn.execute("""
        SELECT
            id,
            event_type,
            severity,
            timestamp
        FROM events
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    events_list = []

    for event in events:

        events_list.append({
            "id": event["id"],
            "event_type": event["event_type"],
            "severity": event["severity"],
            "timestamp": event["timestamp"]
        })

    return jsonify({
        "success": True,
        "count": len(events_list),
        "events": events_list
    })


# ============================================================
# HOME
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return "AI Driver Event API is running!"


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    print("============================================")
    print("       AI DRIVER EVENT API")
    print("============================================")
    print("Database:")
    print(DB_PATH)
    print()
    print("API:")
    print("http://127.0.0.1:5000/api/events")
    print("============================================")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )