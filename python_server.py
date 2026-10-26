
import os
from functools import wraps
from datetime import datetime
from pathlib import Path

import mysql.connector
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session
)

# Project folders
BASE_DIR = Path(__file__).resolve().parent

# Keep your folder name as "statics"
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "statics"),
    static_url_path="/statics"
)

# Session configuration
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "local-development-only-change-me"
)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)

# MySQL configuration

# MySQL configuration

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "attendance_app",
    "password": "MyNewPrivatePass_2026!",
    "database": "college_attendance",
}


# Local development credentials only
ADMIN_USER = os.getenv("APP_USER", "admin")
ADMIN_PASS = os.getenv("APP_PASS", "admin123")


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return jsonify({"error": "Please log in first."}), 401
        return function(*args, **kwargs)
    return wrapper


def valid_date(value):
    if not isinstance(value, str):
        return False

    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def db_error(error):
    app.logger.error("Database operation failed: %s", error)
    return jsonify({
        "error": "Database error. Check MySQL, tables, and settings."
    }), 500


def close_db(cursor, connection):
    if cursor is not None:
        cursor.close()

    if connection is not None and connection.is_connected():
        connection.close()


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Login
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    username = data.get("username", "")
    password = data.get("password", "")

    if (
        isinstance(username, str)
        and isinstance(password, str)
        and username == ADMIN_USER
        and password == ADMIN_PASS
    ):
        session.clear()
        session["logged_in"] = True
        session["username"] = username
        return jsonify({"message": "Login successful."})

    return jsonify({"error": "Incorrect username or password."}), 401


# Logout
@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out."})


# Check login session
@app.route("/api/session", methods=["GET"])
def check_session():
    return jsonify({
        "logged_in": bool(session.get("logged_in"))
    })


# Get students
@app.route("/api/students", methods=["GET"])
@login_required
def list_students():
    connection = None
    cursor = None

    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT roll, name, course FROM students ORDER BY roll"
        )
        return jsonify(cursor.fetchall())

    except mysql.connector.Error as error:
        return db_error(error)

    finally:
        close_db(cursor, connection)


# Add student
@app.route("/api/students", methods=["POST"])
@login_required
def add_student():
    data = request.get_json(silent=True) or {}

    roll = str(data.get("roll", "")).strip()
    name = str(data.get("name", "")).strip()
    course = str(data.get("course", "")).strip()

    if not roll or not name or not course:
        return jsonify({
            "error": "Fill in roll number, name and course."
        }), 400

    if len(roll) > 30 or len(name) > 100 or len(course) > 100:
        return jsonify({
            "error": "One or more fields are too long."
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_db()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO students (roll, name, course)
            VALUES (%s, %s, %s)
            """,
            (roll, name, course)
        )

        connection.commit()

        return jsonify({
            "message": "Student added successfully."
        }), 201

    except mysql.connector.IntegrityError as error:
        if error.errno == 1062:
            return jsonify({
                "error": "That roll number already exists."
            }), 409
        return db_error(error)

    except mysql.connector.Error as error:
        return db_error(error)

    finally:
        close_db(cursor, connection)


# Delete student
@app.route("/api/students/<path:roll>", methods=["DELETE"])
@login_required
def remove_student(roll):
    connection = None
    cursor = None

    try:
        connection = get_db()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM students WHERE roll = %s",
            (roll,)
        )
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found."}), 404

        return jsonify({"message": "Student deleted."})

    except mysql.connector.Error as error:
        return db_error(error)

    finally:
        close_db(cursor, connection)


# Get attendance for a date and subject
@app.route("/api/attendance", methods=["GET"])
@login_required
def list_attendance():
    attendance_date = request.args.get("date", "")
    subject = request.args.get("subject", "").strip()

    if not valid_date(attendance_date) or not subject:
        return jsonify({
            "error": "Select a valid date and subject."
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT roll, status
            FROM attendance
            WHERE att_date = %s AND subject = %s
            ORDER BY roll
            """,
            (attendance_date, subject)
        )

        return jsonify(cursor.fetchall())

    except mysql.connector.Error as error:
        return db_error(error)

    finally:
        close_db(cursor, connection)


# Save attendance
@app.route("/api/attendance", methods=["POST"])
@login_required
def save_attendance():
    data = request.get_json(silent=True) or {}

    attendance_date = data.get("date", "")
    subject = str(data.get("subject", "")).strip()
    records = data.get("records", [])

    if not valid_date(attendance_date) or not subject:
        return jsonify({
            "error": "Select a valid date and subject."
        }), 400

    if len(subject) > 100:
        return jsonify({
            "error": "Subject name is too long."
        }), 400

    if not isinstance(records, list):
        return jsonify({"error": "Invalid attendance data."}), 400

    for record in records:
        if not isinstance(record, dict):
            return jsonify({"error": "Invalid attendance row."}), 400

        roll = str(record.get("roll", "")).strip()
        status = record.get("status")

        if not roll or status not in ("P", "A"):
            return jsonify({
                "error": "Each row must have a roll and P or A status."
            }), 400

    connection = None
    cursor = None

    try:
        connection = get_db()
        connection.start_transaction()
        cursor = connection.cursor()

        sql = """
            INSERT INTO attendance (att_date, subject, roll, status)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE status = VALUES(status)
        """

        rows = [
            (
                attendance_date,
                subject,
                str(record["roll"]).strip(),
                record["status"]
            )
            for record in records
        ]

        if rows:
            cursor.executemany(sql, rows)

        connection.commit()

        return jsonify({
            "message": "Attendance saved successfully."
        })

    except mysql.connector.Error as error:
        if connection and connection.is_connected():
            connection.rollback()
        return db_error(error)

    finally:
        close_db(cursor, connection)


# Attendance report
@app.route("/api/report", methods=["GET"])
@login_required
def attendance_report():
    connection = None
    cursor = None

    try:
        connection = get_db()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                s.roll,
                s.name,
                s.course,
                COUNT(a.id) AS total,
                COALESCE(
                    SUM(CASE WHEN a.status = 'P' THEN 1 ELSE 0 END), 0
                ) AS present,
                COALESCE(
                    SUM(CASE WHEN a.status = 'A' THEN 1 ELSE 0 END), 0
                ) AS absent
            FROM students AS s
            LEFT JOIN attendance AS a ON a.roll = s.roll
            GROUP BY s.roll, s.name, s.course
            ORDER BY s.roll
            """
        )

        rows = cursor.fetchall()

        for row in rows:
            total = row["total"]
            row["percentage"] = (
                round(row["present"] * 100 / total, 2)
                if total else 0
            )

        return jsonify(rows)

    except mysql.connector.Error as error:
        return db_error(error)

    finally:
        close_db(cursor, connection)


# Start server
if __name__ == "__main__":
    print("Starting College Attendance System...")
    print("Open http://127.0.0.1:8080 in your browser.")

    app.run(
        host="127.0.0.1",
        port=8080,
        debug=False
    )
