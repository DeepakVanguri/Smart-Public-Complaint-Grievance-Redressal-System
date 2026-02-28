"""
Database configuration and initialization for Smart Public Complaint System
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "complaints.db")


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize database with all tables"""
    conn = get_db()
    cursor = conn.cursor()

    # Users table (Citizens, Admins, Department Staff)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'citizen',  -- citizen | admin | staff
            department TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            last_login TEXT
        )
    """)

    # Complaints table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_number TEXT UNIQUE NOT NULL,
            citizen_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,  -- water | electricity | sanitation | infrastructure | other
            department TEXT NOT NULL,
            location TEXT NOT NULL,
            priority TEXT DEFAULT 'medium',  -- low | medium | high | urgent
            status TEXT DEFAULT 'submitted',  -- submitted | acknowledged | in_progress | resolved | closed | rejected
            assigned_to INTEGER,
            attachment_path TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            resolved_at TEXT,
            resolution_notes TEXT,
            FOREIGN KEY (citizen_id) REFERENCES users(id),
            FOREIGN KEY (assigned_to) REFERENCES users(id)
        )
    """)

    # Complaint timeline / audit trail
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaint_timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            old_status TEXT,
            new_status TEXT,
            notes TEXT,
            updated_by INTEGER NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (complaint_id) REFERENCES complaints(id),
            FOREIGN KEY (updated_by) REFERENCES users(id)
        )
    """)

    # Ratings / feedback table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER UNIQUE NOT NULL,
            citizen_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,  -- 1-5
            comment TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (complaint_id) REFERENCES complaints(id),
            FOREIGN KEY (citizen_id) REFERENCES users(id)
        )
    """)

    # Notifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            complaint_id INTEGER,
            message TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (complaint_id) REFERENCES complaints(id)
        )
    """)

    conn.commit()

    # Seed default admin user
    cursor.execute("SELECT id FROM users WHERE email = 'admin@smartgov.in'")
    if not cursor.fetchone():
        import hashlib
        admin_hash = hashlib.sha256("Admin@123".encode()).hexdigest()
        cursor.execute("""
            INSERT INTO users (full_name, email, phone, password_hash, role, department)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("System Administrator", "admin@smartgov.in", "9000000000", admin_hash, "admin", "Administration"))

        # Seed department staff
        staff_data = [
            ("Water Dept Staff", "water@smartgov.in", "9000000001", "Staff@123", "staff", "Water Supply"),
            ("Electricity Staff", "electric@smartgov.in", "9000000002", "Staff@123", "staff", "Electricity"),
            ("Sanitation Staff", "sanitation@smartgov.in", "9000000003", "Staff@123", "staff", "Sanitation"),
            ("Infrastructure Staff", "infra@smartgov.in", "9000000004", "Staff@123", "staff", "Infrastructure"),
        ]
        for s in staff_data:
            h = hashlib.sha256(s[3].encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (full_name, email, phone, password_hash, role, department)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (s[0], s[1], s[2], h, s[4], s[5]))

        # Seed a demo citizen
        citizen_hash = hashlib.sha256("Citizen@123".encode()).hexdigest()
        cursor.execute("""
            INSERT INTO users (full_name, email, phone, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
        """, ("Demo Citizen", "citizen@demo.in", "9876543210", citizen_hash, "citizen"))

        conn.commit()

    conn.close()
    print(f"[DB] Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_db()
