
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "bugtrack-local-development-key"

DATABASE = "bugs.db"


# Connect to SQLite database
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create database table
def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT DEFAULT 'Open'
        )
    """)
    conn.commit()
    conn.close()


# Home page - display and search bugs
@app.route("/")
def index():
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    conn = get_db()

    query = "SELECT * FROM bugs WHERE 1=1"
    params = []

    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if status in ["Open", "In Progress", "Resolved"]:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY id DESC"

    bugs = conn.execute(query, params).fetchall()

    conn.close()

    return render_template(
        "index.html",
        bugs=bugs,
        search=search,
        selected_status=status
    )


# Add a new bug
@app.route("/add", methods=["POST"])
def add_bug():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    priority = request.form.get("priority", "").strip()

    if not title or not description or priority not in ["Low", "Medium", "High"]:
        flash("Please enter valid bug details.")
        return redirect(url_for("index"))

    conn = get_db()

    conn.execute(
        "INSERT INTO bugs (title, description, priority) VALUES (?, ?, ?)",
        (title, description, priority)
    )

    conn.commit()
    conn.close()

    flash("Bug reported successfully!")
    return redirect(url_for("index"))


# Update bug status
@app.route("/update/<int:bug_id>", methods=["POST"])
def update_bug(bug_id):
    status = request.form.get("status", "")

    if status not in ["Open", "In Progress", "Resolved"]:
        flash("Invalid status.")
        return redirect(url_for("index"))

    conn = get_db()

    conn.execute(
        "UPDATE bugs SET status = ? WHERE id = ?",
        (status, bug_id)
    )

    conn.commit()
    conn.close()

    flash("Bug status updated!")
    return redirect(url_for("index"))


# Delete a bug
@app.route("/delete/<int:bug_id>", methods=["POST"])
def delete_bug(bug_id):
    conn = get_db()

    conn.execute(
        "DELETE FROM bugs WHERE id = ?",
        (bug_id,)
    )

    conn.commit()
    conn.close()

    flash("Bug deleted successfully!")
    return redirect(url_for("index"))


# Start application
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
