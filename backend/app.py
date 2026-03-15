from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room
import os

from config import Config

# ─── APPLY DB PERFORMANCE INDEXES ON STARTUP ─────────────────────────────────
def apply_db_indexes():
    """Ensure performance indexes exist on the SQLite database."""
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')
    if not os.path.exists(db_path):
        print(f"[DB] Database not found at {db_path}. Run init_db.py first.")
        return
    try:
        conn = sqlite3.connect(db_path)
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_hospitals_status ON hospitals(status)",
            "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_beds_status ON beds(status)",
            "CREATE INDEX IF NOT EXISTS idx_beds_hospital ON beds(hospital_id)",
            "CREATE INDEX IF NOT EXISTS idx_tokens_booking_date ON tokens(booking_date)",
            "CREATE INDEX IF NOT EXISTS idx_tokens_hospital ON tokens(hospital_id)",
            "CREATE INDEX IF NOT EXISTS idx_tokens_status ON tokens(status)",
            "CREATE INDEX IF NOT EXISTS idx_ambulance_created ON ambulance_requests(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_registrations_status ON hospital_registrations(status)",
            "CREATE INDEX IF NOT EXISTS idx_doctors_hospital ON doctors(hospital_id)",
        ]
        for sql in indexes:
            conn.execute(sql)
        conn.commit()
        conn.close()
        print("[DB] Performance indexes applied.")
    except Exception as e:
        print(f"[DB] Index creation warning: {e}")

apply_db_indexes()


app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.secret_key = Config.SECRET_KEY

CORS(app, resources={r"/api/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization"]}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ─── REGISTER BLUEPRINTS ──────────────────────────────────────────────────────────
from routes.auth import auth_bp
from routes.hospitals import hospitals_bp
from routes.tokens import tokens_bp
from routes.beds import beds_bp
from routes.ambulance import ambulance_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(hospitals_bp)
app.register_blueprint(tokens_bp)
app.register_blueprint(beds_bp)
app.register_blueprint(ambulance_bp)
app.register_blueprint(admin_bp)

# ─── WEBSOCKET EVENTS ─────────────────────────────────────────────────────────────
@socketio.on('connect')
def on_connect():
    print('Client connected')

@socketio.on('disconnect')
def on_disconnect():
    print('Client disconnected')

@socketio.on('join_hospital')
def on_join_hospital(data):
    room = f"hospital_{data.get('hospital_id')}"
    join_room(room)
    print(f'Client joined room {room}')

@socketio.on('leave_hospital')
def on_leave_hospital(data):
    room = f"hospital_{data.get('hospital_id')}"
    leave_room(room)

# ─── SERVE FRONTEND ───────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    full = os.path.join(app.static_folder, path)
    if os.path.exists(full):
        return send_from_directory(app.static_folder, path)
    return send_from_directory('../frontend', 'index.html')

# ─── HEALTH CHECK ─────────────────────────────────────────────────────────────────
@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Smart Hospital API running'}), 200

# ─── DOCTORS (for hospital admin & public) ────────────────────────────────────────
from routes.doctors import doctors_bp
app.register_blueprint(doctors_bp)

if __name__ == '__main__':
    print(f"--- Smart Hospital Backend Starting ---")
    print(f"--- Port: {Config.PORT} ---")
    socketio.run(app, host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
