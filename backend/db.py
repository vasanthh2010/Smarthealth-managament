import sqlite3
import os

def get_db():
    """Get a new database connection."""
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    conn = sqlite3.connect(db_path)
    # Return rows as dictionaries to match PyMySQL behavior
    conn.row_factory = sqlite3.Row
    return conn

def query_db(sql, args=(), one=False, commit=False):
    """Helper to run a query and return results."""
    # Convert MySQL %s parameter placeholder to SQLite ? placeholder automatically
    sql = sql.replace('%s', '?')
    
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(sql, args)
        if commit:
            conn.commit()
            return cur.lastrowid
        rv = cur.fetchall()
        # Convert sqlite3.Row objects to standard Python dicts
        rv = [dict(r) for r in rv]
        return (rv[0] if rv else None) if one else rv
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
