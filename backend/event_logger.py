import sqlite3
import os
from datetime import datetime


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATABASE_FOLDER = os.path.join(
    BASE_DIR,
    "database"
)

DB_PATH = os.path.join(
    DATABASE_FOLDER,
    "events.db"
)


# ============================================================
# CREATE DATABASE FOLDER
# ============================================================

os.makedirs(
    DATABASE_FOLDER,
    exist_ok=True
)


# ============================================================
# CREATE EVENTS TABLE
# ============================================================

def create_event_table():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            username TEXT
        )
    """)

    conn.commit()

    columns = [
        row[1]
        for row in cursor.execute(
            "PRAGMA table_info(events)"
        ).fetchall()
    ]

    if "username" not in columns:

        cursor.execute(
            "ALTER TABLE events ADD COLUMN username TEXT"
        )

        conn.commit()

    conn.close()


# ============================================================
# LOG EVENT
# ============================================================

def log_event(
    event_type,
    severity="INFO",
    username=None
):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO events
        (event_type, severity, timestamp, username)
        VALUES (?, ?, ?, ?)
    """, (
        event_type,
        severity,
        timestamp,
        username
    ))

    conn.commit()

    conn.close()

    print(
        f"[EVENT] {event_type} | "
        f"{severity} | "
        f"{timestamp}"
    )

    print(
        f"Saved to: {DB_PATH}"
    )


# ============================================================
# CREATE TABLE WHEN FILE STARTS
# ============================================================

create_event_table()