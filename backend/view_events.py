import sqlite3
import os


# ============================================================
# DATABASE PATH
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "events.db"
)


# ============================================================
# CHECK DATABASE
# ============================================================

if not os.path.exists(DATABASE_PATH):

    print("ERROR: events.db not found!")
    print(DATABASE_PATH)

    exit()


# ============================================================
# CONNECT DATABASE
# ============================================================

conn = sqlite3.connect(DATABASE_PATH)

cursor = conn.cursor()


# ============================================================
# GET EVENTS
# ============================================================

cursor.execute("""
    SELECT id, event_type, event_time
    FROM events
    ORDER BY id DESC
""")

events = cursor.fetchall()


# ============================================================
# DISPLAY EVENTS
# ============================================================

print()
print("==============================================")
print("        AI DRIVER EVENT HISTORY")
print("==============================================")
print()

if len(events) == 0:

    print("No events found.")

else:

    print(
        f"{'ID':<8}"
        f"{'EVENT TYPE':<25}"
        f"{'DATE & TIME'}"
    )

    print("-" * 60)

    for event in events:

        event_id = event[0]
        event_type = event[1]
        event_time = event[2]

        print(
            f"{event_id:<8}"
            f"{event_type:<25}"
            f"{event_time}"
        )


print()
print("==============================================")
print(f"Total Events: {len(events)}")
print("==============================================")


# ============================================================
# CLOSE DATABASE
# ============================================================

conn.close()