import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), 'backend', 'app.db')
    if not os.path.exists(db_path):
        print("Database not found. Make sure you are in the project root.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        # Check if already migrated
        cur.execute("PRAGMA table_info(tokens)")
        columns = [c[1] for c in cur.fetchall()]
        if 'is_offline' in columns:
            print("Database already migrated.")
            return

        print("Starting migration...")
        
        # 1. Create new table
        cur.execute('''
            CREATE TABLE tokens_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER, -- Nullable now
                doctor_id INTEGER NOT NULL,
                hospital_id INTEGER NOT NULL,
                token_number INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                booking_date DATE NOT NULL,
                reason TEXT,
                estimated_wait_minutes INTEGER DEFAULT 0,
                is_offline INTEGER DEFAULT 0,
                offline_name TEXT,
                offline_phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
                FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE
            )
        ''')

        # 2. Copy data
        cur.execute('''
            INSERT INTO tokens_new (id, user_id, doctor_id, hospital_id, token_number, status, booking_date, reason, estimated_wait_minutes, created_at, completed_at)
            SELECT id, user_id, doctor_id, hospital_id, token_number, status, booking_date, reason, estimated_wait_minutes, created_at, completed_at
            FROM tokens
        ''')

        # 3. Drop old and rename new
        cur.execute("DROP TABLE tokens")
        cur.execute("ALTER TABLE tokens_new RENAME TO tokens")

        conn.commit()
        print("Migration successful!")
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
