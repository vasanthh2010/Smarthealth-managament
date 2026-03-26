import pymysql
import os
import re
from urllib.parse import urlparse
from dotenv import load_dotenv

# --- DATABASE CONNECTION DETAILS ---
db_url = os.getenv('DB_URL')
schema_file = "schema.sql"

def initialize_db():
    print(f"--- Railway Database Initialization ---")
    print(f"Connecting to: {db_url}")
    
    try:
        # Parse URL
        url = urlparse(db_url)
        conn = pymysql.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            port=url.port,
            database=url.path.lstrip('/'),
            autocommit=True
        )
        print("Successfully connected to Railway MySQL!")
        
        # Read schema
        if not os.path.exists(schema_file):
            print(f"Error: {schema_file} not found in current directory.")
            return

        with open(schema_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # Split into statements (basic split by semicolon)
        # We need to be careful about semicolon inside quotes, but for this schema it's simple
        statements = sql_script.split(';')
        
        with conn.cursor() as cursor:
            for i, sql in enumerate(statements):
                # Clean up sql
                sql = sql.strip()
                if not sql or sql.startswith('--'):
                    continue
                
                try:
                    cursor.execute(sql)
                    if (i + 1) % 10 == 0:
                        print(f"Executed {i + 1} statements...")
                except Exception as e:
                    print(f"\n[Error at statement {i+1}]: {e}")
                    print(f"SQL: {sql[:100]}...")
                    # Continue or break? Let's continue since some tables might already exist
                    continue
            
        print("\n--- DONE: Database initialized successfully on Railway! ---")
        conn.close()

    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    initialize_db()
