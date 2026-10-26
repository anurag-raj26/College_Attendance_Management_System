
const $ = (id) => document.getElementById(id);

const loginPanel = $("loginPanel");
const dashboard = $("dashboard");
const logoutBtn = $("logoutBtn");
const messageBox = $("message");

let studentsCache = [];
let messageTimer;

function showMessage(message, type = "success") {
    messageBox.textContent = message;
    messageBox.className = `message show ${type}`;

    clearTimeout(messageTimer);
    messageTimer = setTimeout(() => {
        messageBox.className = "message";
    }, 5000);
}

async function api(url, options = {}) {
    const response = await fetch(url, {
        credentials: "same-origin",
        ...options,
        headers: {
            ...(options.body ? { "Content-Type": "application/json" } : {}),
            ...(options.headers || {})
        }
    });

    const contentType = response.headers.get("content-type") || "";
    let result;

    if (contentType.includes("application/json")) {
        result = await response.json();
    } else {
        result = await response.text();
    }

    if (!response.ok) {
        const error = typeof result === "object"
            ? result.error || "Request failed."
            : result || "Request failed.";

        if (response.status === 401 && url !== "/api/login") {
            setLoggedIn(false);
        }

        throw new Error(error);
    }

    return result;
}

function setLoggedIn(loggedIn) {
    loginPanel.classList.toggle("hidden", loggedIn);
    dashboard.classList.toggle("hidden", !loggedIn);
    logoutBtn.classList.toggle("hidden", !loggedIn);
}

function makeCell(text) {
    const cell = document.createElement("td");
    cell.textContent = text ?? "";
    return cell;
}

function makeRow(message, columnCount) {
    const row = document.createElement("tr");
    const cell = makeCell(message);
    cell.colSpan = columnCount;
    row.appendChild(cell);
    return row;
}

function localDateString() {
    const now = new Date();
    const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
    return local.toISOString().slice(0, 10);
}

async function loadStudents() {
    studentsCache = await api("/api/students");
    $("studentCount").textContent = studentsCache.length;

    const body = $("studentsBody");
    body.replaceChildren();

    if (studentsCache.length === 0) {
        body.appendChild(makeRow("No students yet. Add a student above.", 4));
    }

    for (const student of studentsCache) {
        const row = document.createElement("tr");
        row.append(
            makeCell(student.roll),
            makeCell(student.name),
            makeCell(student.course)
        );

        const actionCell = document.createElement("td");
        const button = document.createElement("button");
        button.textContent = "Delete";
        button.className = "delete-btn";
        button.type = "button";

        button.addEventListener("click", async () => {
            const confirmed = window.confirm(
                `Delete student ${student.name} (${student.roll})? ` +
                "Their attendance records will also be deleted."
            );

            if (!confirmed) return;

            try {
                await api(`/api/students/${encodeURIComponent(student.roll)}`, {
                    method: "DELETE"
                });

                showMessage("Student deleted.");
                await refreshAll();
            } catch (error) {
                showMessage(error.message, "error");
            }
        });

        actionCell.appendChild(button);
        row.appendChild(actionCell);
        body.appendChild(row);
    }

    renderAttendanceRows([]);
}

function renderAttendanceRows(savedRecords = []) {
    const body = $("attendanceBody");
    body.replaceChildren();

    if (studentsCache.length === 0) {
        body.appendChild(makeRow("Add students first.", 3));
        return;
    }

    const saved = new Map(savedRecords.map(item => [item.roll, item.status]));

    for (const student of studentsCache) {
        const row = document.createElement("tr");
        row.append(makeCell(student.roll), makeCell(student.name));

        const statusCell = document.createElement("td");
        const select = document.createElement("select");
        select.className = "status-select";
        select.dataset.roll = student.roll;
        select.setAttribute("aria-label", `Attendance for ${student.name}`);

        for (const [value, label] of [
            ["P", "Present"],
            ["A", "Absent"]
        ]) {
            const option = document.createElement("option");
            option.value = value;
            option.textContent = label;
            select.appendChild(option);
        }

        select.value = saved.get(student.roll) || "P";
        statusCell.appendChild(select);
        row.appendChild(statusCell);
        body.appendChild(row);
    }
}

async function loadSavedAttendance() {
    const date = $("attendanceDate").value;
    const subject = $("subject").value.trim();

    if (!date || !subject) {
        throw new Error("Choose a date and enter a subject first.");
    }

    const query = new URLSearchParams({ date, subject });
    const saved = await api(`/api/attendance?${query.toString()}`);

    renderAttendanceRows(saved);
    showMessage("Saved attendance loaded.");
}

async function loadReport() {
    const rows = await api("/api/report");
    const body = $("reportBody");
    body.replaceChildren();

    let totalPresent = 0;
    let totalAbsent = 0;

    if (rows.length === 0) {
        body.appendChild(makeRow("No report data yet.", 7));
    }

    for (const item of rows) {
        totalPresent += Number(item.present);
        totalAbsent += Number(item.absent);

        const row = document.createElement("tr");
        row.append(
            makeCell(item.roll),
            makeCell(item.name),
            makeCell(item.course),
            makeCell(item.total),
            makeCell(item.present),
            makeCell(item.absent),
            makeCell(`${Number(item.percentage).toFixed(2)}%`)
        );
        body.appendChild(row);
    }

    $("presentCount").textContent = totalPresent;
    $("absentCount").textContent = totalAbsent;
}

async function refreshAll() {
    await loadStudents();
    await loadReport();
}

$("loginForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
        await api("/api/login", {
            method: "POST",
            body: JSON.stringify({
                username: $("username").value.trim(),
                password: $("password").value
            })
        });

        $("password").value = "";
        setLoggedIn(true);
        $("attendanceDate").value = localDateString();

        await refreshAll();
        showMessage("Login successful.");
    } catch (error) {
        setLoggedIn(false);
        showMessage(error.message, "error");
    }
});

logoutBtn.addEventListener("click", async () => {
    try {
        await api("/api/logout", { method: "POST" });
        setLoggedIn(false);
        showMessage("You have logged out.");
    } catch (error) {
        showMessage(error.message, "error");
    }
});

$("studentForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
        await api("/api/students", {
            method: "POST",
            body: JSON.stringify({
                roll: $("roll").value.trim(),
                name: $("studentName").value.trim(),
                course: $("course").value.trim()
            })
        });

        $("studentForm").reset();
        showMessage("Student added successfully.");
        await refreshAll();
    } catch (error) {
        showMessage(error.message, "error");
    }
});

$("attendanceForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const records = Array.from(
        document.querySelectorAll("#attendanceBody .status-select")
    ).map(select => ({
        roll: select.dataset.roll,
        status: select.value
    }));

    try {
        await api("/api/attendance", {
            method: "POST",
            body: JSON.stringify({
                date: $("attendanceDate").value,
                subject: $("subject").value.trim(),
                records
            })
        });

        showMessage("Attendance saved successfully.");
        await loadReport();
    } catch (error) {
        showMessage(error.message, "error");
    }
});

$("loadAttendance").addEventListener("click", async () => {
    try {
        await loadSavedAttendance();
    } catch (error) {
        showMessage(error.message, "error");
    }
});

$("refreshStudents").addEventListener("click", async () => {
    try {
        await loadStudents();
        showMessage("Student list refreshed.");
    } catch (error) {
        showMessage(error.message, "error");
    }
});

$("refreshReport").addEventListener("click", async () => {
    try {
        await loadReport();
        showMessage("Report refreshed.");
    } catch (error) {
        showMessage(error.message, "error");
    }
});

async function initialize() {
    $("attendanceDate").value = localDateString();

    try {
        const state = await api("/api/session");
        setLoggedIn(state.logged_in);

        if (state.logged_in) {
            await refreshAll();
        }
    } catch (error) {
        setLoggedIn(false);
        showMessage(error.message, "error");
    }
}

initialize();
