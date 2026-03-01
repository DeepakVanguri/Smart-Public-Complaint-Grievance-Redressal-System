import sqlite3
conn = sqlite3.connect('complaints.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute('SELECT id, full_name, email, role, department FROM users ORDER BY id')
for r in cur.fetchall():
    print(f"ID:{r['id']} | {r['role']:8} | {r['email']:35} | {r['department']}")
conn.close()
