import sqlite3
import bcrypt
import os

def reset_passwords():
    db_path = os.path.join(os.path.dirname(__file__), 'backend', 'app.db')
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    new_password = b"Admin@123"
    salt = bcrypt.gensalt()
    new_hash = bcrypt.hashpw(new_password, salt).decode()

    print(f"New Hash: {new_hash}")

    # Update Super Admin
    cur.execute("UPDATE super_admins SET password_hash = ? WHERE username = 'superadmin'", (new_hash,))
    
    # Update Sample Hospital
    cur.execute("UPDATE hospitals SET password_hash = ? WHERE login_id = 'HOSP001'", (new_hash,))

    conn.commit()
    conn.close()
    print("Passwords successfully reset to 'Admin@123'!")

if __name__ == '__main__':
    reset_passwords()
