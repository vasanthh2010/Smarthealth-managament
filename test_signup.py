import requests
import json
import sqlite3
import os

BASE_URL = "http://localhost:5000"

def test_signup():
    payload = {
        "full_name": "Test Patient",
        "email": "test@example.com",
        "phone": "1234567890",
        "password": "Password123",
        "date_of_birth": "1990-01-01",
        "age": 34,
        "blood_group": "O+",
        "address": "123 Test St",
        "gender": "male"
    }
    
    # Try to signup
    print(f"Signing up {payload['email']}...")
    try:
        r = requests.post(f"{BASE_URL}/api/auth/patient/signup", json=payload)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
    except Exception as e:
        print(f"Error calling API: {e}")
        return

    # Check DB
    db_path = os.path.join("backend", "app.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (payload['email'],))
        user = cur.fetchone()
        if user:
            print(f"User found in DB: {user}")
        else:
            print("User NOT found in DB!")
        conn.close()
    else:
        print("DB file not found!")

if __name__ == "__main__":
    test_signup()
