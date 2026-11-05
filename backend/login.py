import os
import sqlite3
import subprocess
import sys

from flask import Flask, request, jsonify
from flask_cors import CORS


# ============================================================
# APP
# ============================================================

app = Flask(__name__)

CORS(app)


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ============================================================
# DATABASE PATHS
# ============================================================

USERS_DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "users.db"
)


EVENTS_DB_PATH = os.path.join(
    BASE_DIR,
    "database",
    "events.db"
)


# ============================================================
# DRIVER MONITOR PROCESS
# ============================================================

monitor_process = None


# ============================================================
# USERS DATABASE CONNECTION
# ============================================================

def get_users_connection():

    return sqlite3.connect(
        USERS_DB_PATH
    )


def get_event_statistics(username=None):

    conn = sqlite3.connect(EVENTS_DB_PATH)

    try:

        query = "SELECT event_type FROM events"
        parameters = []

        if username is not None:
            query += " WHERE username = ?"
            parameters.append(username)

        rows = conn.execute(query, parameters).fetchall()

    finally:

        conn.close()

    counts = {
        "total_events": len(rows),
        "drowsiness": 0,
        "phone_usage": 0,
        "yawning": 0,
        "distraction": 0
    }

    for row in rows:

        event_type = str(row[0] or "").strip().upper()

        if "DROWS" in event_type:
            counts["drowsiness"] += 1
        elif "PHONE" in event_type or "MOBILE" in event_type:
            counts["phone_usage"] += 1
        elif "YAWN" in event_type:
            counts["yawning"] += 1
        elif "DISTRACT" in event_type or "HEAD" in event_type:
            counts["distraction"] += 1

    return counts


# ============================================================
# REGISTER USER
# ============================================================

@app.route(
    "/register",
    methods=["POST"]
)
def register():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No registration data received"
            }), 400


        username = data.get("username", "").strip()
        password = data.get("password", "")
        role = data.get("role", "driver").strip() or "driver"

        if not username or not password:

            return jsonify({
                "success": False,
                "message": "Username and password are required"
            }), 400


        conn = get_users_connection()

        conn.execute(
            """
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
            """,
            (username, password, role)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "User registered successfully"
        })


    except sqlite3.IntegrityError:

        return jsonify({
            "success": False,
            "message": "Username already exists"
        }), 409


    except Exception as e:

        print("REGISTER ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ============================================================
# REGISTER DRIVER PROFILE
# ============================================================

@app.route(
    "/register-driver",
    methods=["POST"]
)
def register_driver():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No driver data received"
            }), 400


        required_fields = [
            "username",
            "first_name",
            "last_name",
            "contact",
            "license_number",
            "emergency_contact",
            "vehicle_number",
            "vehicle_type"
        ]

        missing_fields = [
            field
            for field in required_fields
            if not str(data.get(field, "")).strip()
        ]

        if missing_fields:

            return jsonify({
                "success": False,
                "message": "Missing required driver details"
            }), 400


        conn = get_users_connection()

        conn.execute(
            """
            INSERT INTO drivers (
                username,
                first_name,
                last_name,
                phone_number,
                email,
                license_number,
                emergency_name,
                emergency_number,
                vehicle_number,
                vehicle_type,
                vehicle_model
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["username"].strip(),
                data["first_name"].strip(),
                data["last_name"].strip(),
                data["contact"].strip(),
                data.get("email", "").strip(),
                data["license_number"].strip(),
                "Emergency Contact",
                data["emergency_contact"].strip(),
                data["vehicle_number"].strip(),
                data["vehicle_type"].strip(),
                data.get("vehicle_model", "").strip()
            )
        )

        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "message": "Driver details saved successfully"
        })


    except sqlite3.IntegrityError:

        return jsonify({
            "success": False,
            "message": "Driver details already exist for this account"
        }), 409


    except Exception as e:

        print("DRIVER REGISTRATION ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["POST"]
)
def login():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No login data received"
            })


        username = data.get(
            "username",
            ""
        ).strip()


        password = data.get(
            "password",
            ""
        )


        conn = get_users_connection()

        cursor = conn.cursor()


        cursor.execute(
            """
            SELECT username, role
            FROM users
            WHERE username = ?
            AND password = ?
            """,
            (
                username,
                password
            )
        )


        user = cursor.fetchone()

        conn.close()


        if user:

            return jsonify({

                "success": True,

                "message":
                    "Login successful",

                "username":
                    user[0],

                "role":
                    user[1]

            })


        return jsonify({

            "success": False,

            "message":
                "Invalid username or password"

        })


    except Exception as e:

        print(
            "LOGIN ERROR:",
            e
        )

        return jsonify({

            "success": False,

            "message":
                str(e)

        })


# ============================================================
# START DRIVER MONITORING
# ============================================================

@app.route(
    "/start-monitoring",
    methods=["POST"]
)
def start_monitoring():

    global monitor_process


    try:

        data = request.get_json()


        if not data:

            return jsonify({

                "success": False,

                "message":
                    "No monitoring data received"

            })


        username = data.get(
            "username",
            ""
        ).strip()


        if not username:

            return jsonify({

                "success": False,

                "message":
                    "Username is required"

            })


        # ====================================================
        # CHECK WHETHER MONITORING IS ALREADY RUNNING
        # ====================================================

        if (
            monitor_process is not None
            and
            monitor_process.poll() is None
        ):

            return jsonify({

                "success": False,

                "message":
                    "Driver monitoring is already running"

            })


        # ====================================================
        # DRIVER MONITOR FILE
        # ====================================================

        monitor_file = os.path.join(

            BASE_DIR,

            "backend",

            "driver_monitor.py"

        )


        if not os.path.exists(
            monitor_file
        ):

            return jsonify({

                "success": False,

                "message":
                    "driver_monitor.py not found"

            })


        # ====================================================
        # START DRIVER MONITOR
        # ====================================================

        monitor_process = subprocess.Popen(

            [

                sys.executable,

                monitor_file,

                username

            ],

            cwd=BASE_DIR

        )


        print()
        print(
            "===================================="
        )
        print(
            "DRIVER MONITORING STARTED"
        )
        print(
            "Username:",
            username
        )
        print(
            "Process ID:",
            monitor_process.pid
        )
        print(
            "===================================="
        )


        return jsonify({

            "success": True,

            "username":
                username,

            "message":
                "Driver monitoring started"

        })


    except Exception as e:

        print(
            "START MONITORING ERROR:",
            e
        )


        return jsonify({

            "success": False,

            "message":
                str(e)

        })


# ============================================================
# MONITORING STATUS
# ============================================================

@app.route(
    "/monitoring-status",
    methods=["GET"]
)
def monitoring_status():

    global monitor_process


    try:

        if monitor_process is None:

            return jsonify({

                "running": False

            })


        running = (
            monitor_process.poll()
            is None
        )


        return jsonify({

            "running":
                running

        })


    except Exception as e:

        print(
            "MONITOR STATUS ERROR:",
            e
        )


        return jsonify({

            "running":
                False,

            "message":
                str(e)

        })


# ============================================================
# EVENT HISTORY API
# ============================================================

@app.route(
    "/api/events",
    methods=["GET"]
)
def get_events():

    try:

        if not os.path.exists(
            EVENTS_DB_PATH
        ):

            return jsonify({

                "success": True,

                "events": []

            })


        conn = sqlite3.connect(
            EVENTS_DB_PATH
        )


        conn.row_factory = (
            sqlite3.Row
        )


        cursor = conn.cursor()

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


        # ====================================================
        # GET EVENTS
        # ====================================================

        username = request.args.get(
            "username"
        )

        query = """
            SELECT
                id,
                event_type,
                severity,
                timestamp,
                username
            FROM events
        """

        parameters = []

        if username:

            query += " WHERE username = ?"
            parameters.append(username)

        query += " ORDER BY id DESC"

        cursor.execute(query, parameters)


        rows = cursor.fetchall()


        conn.close()


        events = []


        for row in rows:

            events.append({

                "id":
                    row["id"],

                "event_type":
                    row["event_type"],

                "severity":
                    row["severity"],

                "timestamp":
                    row["timestamp"]

                ,

                "username":
                    row["username"]

            })


        return jsonify({

            "success": True,

            "events":
                events

        })


    except Exception as e:

        print(
            "EVENT API ERROR:",
            e
        )


        return jsonify({

            "success": False,

            "events": [],

            "message":
                str(e)

        })


# ============================================================
# DASHBOARD STATISTICS API
# ============================================================

@app.route("/api/dashboard/stats", methods=["GET"])
def dashboard_statistics():

    try:

        return jsonify({
            "success": True,
            **get_event_statistics()
        })

    except Exception as error:

        print("DASHBOARD STATISTICS ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load dashboard statistics."
        }), 500


@app.route("/api/dashboard/stats/<username>", methods=["GET"])
def driver_dashboard_statistics(username):

    try:

        return jsonify({
            "success": True,
            "username": username,
            **get_event_statistics(username)
        })

    except Exception as error:

        print("DRIVER DASHBOARD STATISTICS ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Unable to load dashboard statistics."
        }), 500


# ============================================================
# HOME / TEST API
# ============================================================

@app.route("/")
def home():

    return (
        "AI Driver API is running"
    )


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "===================================="
    )
    print(
        "        AI DRIVER API"
    )
    print(
        "===================================="
    )
    print(
        "Server:"
    )
    print(
        "http://127.0.0.1:5000"
    )
    print(
        "===================================="
    )
    print()


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True,

        use_reloader=False

    )