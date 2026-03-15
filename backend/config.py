import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'smart_hospital')
    DB_PORT = int(os.getenv('DB_PORT', 3306))

    # JWT
    JWT_SECRET = os.getenv('JWT_SECRET', 'smart_hospital_super_secret_key_2024')
    JWT_EXPIRY_HOURS = 24

    # App
    SECRET_KEY = os.getenv('SECRET_KEY', 'flask_secret_key_2024')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    PORT = int(os.getenv('PORT', 5001))


