import sqlite3
import os

def init_db():
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    schema_path = os.path.join(os.path.dirname(__file__), 'schema_sqlite.sql')
    
    if os.path.exists(db_path):
        print("Database already exists. Skipping initialization.")
        return

    # Create the database and execute schema
    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    
    conn.commit()
    conn.close()
    print("SQLite database successfully initialized!")

if __name__ == '__main__':
    init_db()
