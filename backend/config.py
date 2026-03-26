import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database URL Parsing
    DB_URL = os.getenv('DB_URL')
    
    if DB_URL:
        from urllib.parse import urlparse
        url = urlparse(DB_URL)
        DB_HOST = url.hostname
        DB_USER = url.username
        DB_PASSWORD = url.password
        DB_PORT = url.port or 3306
        DB_NAME = url.path.lstrip('/')
    else:
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
    PORT = int(os.getenv('PORT', 5000))



