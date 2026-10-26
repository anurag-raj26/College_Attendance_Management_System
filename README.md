# College Attendance Management System

A web app for teachers to manage students, mark daily attendance and view attendance reports.
Built with **Java** (backend), **MySQL** (database), **HTML, CSS and JavaScript** (frontend).

## Features
- Teacher login
- Add and remove students
- Mark attendance (Present / Absent) by date and subject
- Attendance report with percentage per student (below 75% highlighted)
- Download the report as CSV

## Project structure
```
attendance-management-system/
├── src/Server.java        Java backend (HTTP server + REST API + MySQL)
├── public/                Frontend
│   ├── index.html
│   ├── style.css
│   └── app.js
├── database/schema.sql    Table definitions (also created automatically)
├── lib/                   Put the MySQL JDBC driver .jar here
├── .gitignore
└── README.md
```

## Requirements
- JDK 17 or newer (https://adoptium.net)
- MySQL Server 8 (https://dev.mysql.com/downloads/installer)
- MySQL Connector/J jar (https://dev.mysql.com/downloads/connector/j, choose "Platform Independent")
- Git (https://git-scm.com)

## How to run

### 1. Get the code
```bash
git clone https://github.com/YOUR-USERNAME/attendance-management-system.git
cd attendance-management-system
```

### 2. Add the MySQL driver
Copy the Connector/J jar into the `lib` folder and rename it to `mysql-connector-j.jar`.

### 3. Make sure MySQL is running
The app creates the database `college_attendance` and its tables automatically.
(Optional: run `database/schema.sql` yourself in MySQL Workbench.)

### 4. Set your MySQL password
Windows (Command Prompt):
```
set DB_PASS=your_mysql_password
```
Mac / Linux:
```bash
export DB_PASS=your_mysql_password
```
Optional settings: `DB_USER` (default `root`) and `DB_URL`
(default `jdbc:mysql://localhost:3306/college_attendance?createDatabaseIfNotExist=true`).

### 5. Compile
```
javac -d out src/Server.java
```

### 6. Run
Windows:
```
java -cp out;lib/mysql-connector-j.jar Server
```
Mac / Linux:
```bash
java -cp out:lib/mysql-connector-j.jar Server
```

### 7. Open the app
Go to http://localhost:8080 and sign in with:

| Username | Password |
|----------|----------|
| admin | admin123 |

Run all commands from the project root folder (the one that contains `src` and `public`).

## API
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/login | Teacher login |
| GET / POST / DELETE | /api/students | List, add, remove students |
| GET / POST | /api/attendance | Load or save attendance for a date and subject |
| GET | /api/report | Attendance totals per student |

## Troubleshooting
| Problem | Fix |
|---------|-----|
| `Access denied for user 'root'` | `DB_PASS` is wrong or not set in this terminal |
| `Communications link failure` | MySQL service is not running |
| `No suitable driver` | Jar missing from `lib/` or misnamed |
| `Address already in use` | Port 8080 is taken; change it in `src/Server.java` |
| Page shows "Not found" | Run the command from the project root, not from inside `src` |

## Notes
The login is a single hardcoded account (edit `USER` and `PASS` in `src/Server.java`). This is intended as a college project, not for production use.
