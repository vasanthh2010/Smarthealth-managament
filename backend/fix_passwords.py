import sqlite3
import bcrypt
import os

db_path = os.path.join(os.path.dirname(__file__), 'app.db')
conn = sqlite3.connect(db_path)
pw_hash = bcrypt.hashpw(b"Admin@123", bcrypt.gensalt()).decode()

conn.execute("UPDATE super_admins SET password_hash = ?", (pw_hash,))
conn.execute("UPDATE hospitals SET password_hash = ? WHERE login_id = 'HOSP001'", (pw_hash,))
conn.commit()
conn.close()
print("Passwords updated!")
