from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room
import os

from config import Config

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
    socketio.run(app, host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
