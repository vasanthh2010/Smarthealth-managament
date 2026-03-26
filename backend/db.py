import os
import sqlite3
import pymysql
from pymysql.cursors import DictCursor
from config import Config

def get_db():
    """Get a new database connection (MySQL if DB_URL is present, else SQLite)."""
    if Config.DB_URL:
        conn = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            cursorclass=DictCursor,
            autocommit=True
        )
        return conn
    else:
        # Fallback to local SQLite for development
        db_path = os.path.join(os.path.dirname(__file__), 'app.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

def query_db(sql, args=(), one=False, commit=False):
    """Helper to run a query and return results."""
    conn = get_db()
    
    # Handle SQLite placeholder differences
    is_sqlite = isinstance(conn, sqlite3.Connection)
    if is_sqlite:
        sql = sql.replace('%s', '?')
    
    try:
        cur = conn.cursor()
        cur.execute(sql, args)
        
        if commit:
            if not is_sqlite:
                # pymysql uses commit() but we have autocommit=True
                pass
            else:
                conn.commit()
            return cur.lastrowid
        
        rv = cur.fetchall()
        
        # Convert sqlite3.Row objects to standard Python dicts if using SQLite
        if is_sqlite:
            rv = [dict(r) for r in rv]
            
        return (rv[0] if rv else None) if one else rv
    except Exception as e:
        if is_sqlite:
            conn.rollback()
        raise e
    finally:
        conn.close()
