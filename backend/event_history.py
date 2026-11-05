import sqlite3
import os


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
# GET EVENTS
# ============================================================

def get_events():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, event_type, severity, timestamp
        FROM events
        ORDER BY id DESC
    """)

    events = cursor.fetchall()

    conn.close()

    return events


# ============================================================
# DISPLAY EVENTS
# ============================================================

def display_events():

    events = get_events()

    print()
    print("=" * 70)
    print("                 DRIVER EVENT HISTORY")
    print("=" * 70)

    if not events:

        print("No events found.")

    else:

        print(
            f"{'ID':<5}"
            f"{'EVENT':<25}"
            f"{'SEVERITY':<12}"
            f"{'TIME':<25}"
        )

        print("-" * 70)

        for event in events:

            event_id = event[0]
            event_type = event[1]
            severity = event[2]
            timestamp = event[3]

            print(
                f"{event_id:<5}"
                f"{event_type:<25}"
                f"{severity:<12}"
                f"{timestamp:<25}"
            )

    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    display_events()