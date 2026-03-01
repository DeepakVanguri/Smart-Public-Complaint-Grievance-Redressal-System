"""
Fix: Insert missing staff accounts into existing database
"""
import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "complaints.db")

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

staff_to_add = [
    ("Water Dept Staff",      "water@smartgov.in",      "9000000001", "Staff@123", "staff", "Water Supply"),
    ("Electricity Staff",     "electric@smartgov.in",   "9000000002", "Staff@123", "staff", "Electricity"),
    ("Sanitation Staff",      "sanitation@smartgov.in", "9000000003", "Staff@123", "staff", "Sanitation"),
    ("Infrastructure Staff",  "infra@smartgov.in",      "9000000004", "Staff@123", "staff", "Infrastructure"),
]

inserted = 0
skipped = 0

for name, email, phone, password, role, dept in staff_to_add:
    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cur.fetchone():
        print(f"  SKIP (already exists): {email}")
        skipped += 1
    else:
        cur.execute("""
            INSERT INTO users (full_name, email, phone, password_hash, role, department)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, phone, hash_password(password), role, dept))
        print(f"  ADDED: {email} | dept={dept}")
        inserted += 1

conn.commit()
conn.close()

print(f"\nDone! Inserted: {inserted}, Skipped: {skipped}")
print("\nAll users now in DB:")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT id, full_name, email, role, department FROM users ORDER BY id")
for r in cur.fetchall():
    print(f"  ID:{r['id']} | {r['role']:8} | {r['email']:35} | {r['department']}")
conn.close()
