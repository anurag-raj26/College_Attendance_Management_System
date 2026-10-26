# College Attendance Management System

A web-based college attendance application built with **Python, Flask, MySQL, HTML, CSS, and JavaScript**. The Flask server provides login/session handling, student management, attendance recording, and attendance reports through JSON API endpoints.

> **Project status:** This README is based on the supplied `python_server.py`. The frontend files and SQL schema were not included in the supplied file, so their exact contents and UI behavior could not be verified.

## Features

- Admin login and logout using a Flask session.
- List students and add new student records.
- Delete a student by roll number.
- Record attendance for a selected date and subject.
- Mark attendance as **Present (`P`)** or **Absent (`A`)**.
- Update an existing attendance record for the same date, subject, and roll number.
- Generate a report with total, present, absent, and attendance percentage for each student.
- Validate dates and required fields.
- Return JSON error messages for common API errors.

## Technology Stack

- **Backend:** Python, Flask
- **Database:** MySQL
- **Database connector:** `mysql-connector-python`
- **Frontend:** HTML, CSS, JavaScript (served from the `templates/` and `statics/` folders, as configured by the server)
- **Session:** Flask session cookies

## Folder Structure

Use this structure for the project. Keep the folder names `templates` and `statics` exactly as shown because the server is configured to use them.

```text
college-attendance-system/
├── python_server.py
├── requirements.txt
├── .env                  
├── .gitignore
├── README.md
├── templates/
│   └── index.html        
└── statics/
    ├── css/
    │   └── style.css    
    └── js/
        └── script.js     
```

The `css/` and `js/` subfolders are suggested organization; create them only if your frontend files use those paths. The supplied server renders `templates/index.html` and serves static files under `/statics/...`.

## Requirements

- Python 3.10 or later recommended
- MySQL Server
- pip
- A web browser

## 1. Clone or open the project

If the project is already on your computer, open a terminal in the project folder. To clone it from GitHub:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

Replace the URL with your repository URL.

## 2. Create a virtual environment

**Windows (Command Prompt):**

```bat
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Python dependencies

Create a `requirements.txt` file containing:

```text
Flask
mysql-connector-python
```

Then install:

```bash
python -m pip install -r requirements.txt
```

## 4. Configure MySQL

Start your MySQL server and create the database and a dedicated application user. Run the following in MySQL as an administrator, changing the example password to a strong, unique password:

```sql
CREATE DATABASE college_attendance
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'attendance_app'@'localhost'
  IDENTIFIED BY 'REPLACE_WITH_A_STRONG_DATABASE_PASSWORD';

GRANT SELECT, INSERT, UPDATE, DELETE
  ON college_attendance.*
  TO 'attendance_app'@'localhost';

FLUSH PRIVILEGES;
```

The supplied Python code expects these tables and columns:

```sql
CREATE TABLE students (
    roll VARCHAR(30) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    course VARCHAR(100) NOT NULL
);

CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    att_date DATE NOT NULL,
    subject VARCHAR(100) NOT NULL,
    roll VARCHAR(30) NOT NULL,
    status ENUM('P', 'A') NOT NULL,
    UNIQUE KEY unique_attendance (att_date, subject, roll),
    CONSTRAINT fk_attendance_student
        FOREIGN KEY (roll) REFERENCES students(roll)
        ON DELETE CASCADE
);
```

**Important:** The `UNIQUE` key allows the server's `ON DUPLICATE KEY UPDATE` query to update attendance for the same student, date, and subject. The foreign key also means a student must exist before attendance can be recorded for them. If you already have a schema, compare it with these expected columns before running this SQL.

## 5. Set environment variables

The server reads `SECRET_KEY`, `APP_USER`, and `APP_PASS` from environment variables. Set them before starting the app.

**Windows Command Prompt:**

```bat
set SECRET_KEY=replace-with-a-long-random-secret
set APP_USER=admin
set APP_PASS=replace-with-a-strong-admin-password
```

**Windows PowerShell:**

```powershell
$env:SECRET_KEY = "replace-with-a-long-random-secret"
$env:APP_USER = "admin"
$env:APP_PASS = "replace-with-a-strong-admin-password"
```

**macOS/Linux:**

```bash
export SECRET_KEY='replace-with-a-long-random-secret'
export APP_USER='admin'
export APP_PASS='replace-with-a-strong-admin-password'
```

The current supplied file still contains MySQL connection values directly in `DB_CONFIG`. Before publishing or deploying, change the code to read the database host, username, password, and database name from environment variables too. Do not upload real passwords or secret keys to GitHub. Also replace the fallback Flask secret key in the source; it is intended only for local development.

## 6. Run the application

With MySQL running and the database configured, start the server:

```bash
python python_server.py
```

Open:

```text
http://127.0.0.1:8080
```

The server is configured to listen on `127.0.0.1` port `8080`, so it is intended for local access as written.

## Login configuration

The code uses `APP_USER` and `APP_PASS` environment variables for the admin login. If they are not set, the current code falls back to the development defaults `admin` and `admin123`.

**Do not use those defaults for a public deployment.** Set strong environment variables and consider replacing the plain-text credential comparison with a database-backed account and a password-hashing library before using this system with real student data.

## API Endpoints

The API expects and returns JSON for login and data operations.

| Method | Endpoint | Purpose | Login required? |
|---|---|---|---|
| `GET` | `/` | Render the home page (`templates/index.html`) | No |
| `POST` | `/api/login` | Log in and create a session | No |
| `POST` | `/api/logout` | Clear the current session | No |
| `GET` | `/api/session` | Check whether the session is logged in | No |
| `GET` | `/api/students` | List students | Yes |
| `POST` | `/api/students` | Add a student | Yes |
| `DELETE` | `/api/students/<roll>` | Delete a student | Yes |
| `GET` | `/api/attendance?date=YYYY-MM-DD&subject=SUBJECT` | Get attendance for a date and subject | Yes |
| `POST` | `/api/attendance` | Save attendance records | Yes |
| `GET` | `/api/report` | Get attendance totals and percentages | Yes |

### Example request bodies

**Login — `POST /api/login`**

```json
{
  "username": "admin",
  "password": "your-configured-admin-password"
}
```

**Add a student — `POST /api/students`**

```json
{
  "roll": "101",
  "name": "Example Student",
  "course": "BCA"
}
```

**Save attendance — `POST /api/attendance`**

```json
{
  "date": "2026-10-26",
  "subject": "Python",
  "records": [
    {
      "roll": "101",
      "status": "P"
    },
    {
      "roll": "102",
      "status": "A"
    }
  ]
}
```

Attendance status must be `P` or `A`. Use a real date in `YYYY-MM-DD` format and ensure each roll number exists in the `students` table.

## Testing checklist

- [ ] MySQL is running and the database credentials work.
- [ ] The `students` and `attendance` tables exist with the required columns and keys.
- [ ] `http://127.0.0.1:8080` opens the home page.
- [ ] Login succeeds with the environment-configured credentials.
- [ ] Student list loads after login.
- [ ] A student can be added and deleted.
- [ ] Attendance can be saved and retrieved for a date and subject.
- [ ] Saving attendance again for the same date, subject, and roll updates the status.
- [ ] The report returns totals and percentage.
- [ ] Logging out prevents access to protected endpoints.

