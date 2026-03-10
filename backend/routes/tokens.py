from flask import Blueprint, request, jsonify
from db import query_db
from middleware import require_role
from datetime import date

tokens_bp = Blueprint('tokens', __name__)

# ─── BOOK TOKEN ──────────────────────────────────────────────────────────────────
@tokens_bp.route('/api/tokens/book', methods=['POST'])
@require_role('patient')
def book_token(current_user):
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    reason = data.get('reason', '')

    if not doctor_id:
        return jsonify({'error': 'doctor_id is required'}), 400

    doctor = query_db('SELECT * FROM doctors WHERE id=%s AND is_available=1', (doctor_id,), one=True)
    if not doctor:
        return jsonify({'error': 'Doctor not available or not found'}), 404

    today = date.today().isoformat()
    # Check if already booked today
    existing = query_db(
        'SELECT id FROM tokens WHERE user_id=%s AND doctor_id=%s AND booking_date=%s AND status IN ("pending","in_service")',
        (current_user['user_id'], doctor_id, today), one=True
    )
    if existing:
        return jsonify({'error': 'You already have an active token for this doctor today'}), 409

    # Get next token number for this doctor today
    last = query_db(
        'SELECT MAX(token_number) AS max_token FROM tokens WHERE doctor_id=%s AND booking_date=%s',
        (doctor_id, today), one=True
    )
    token_number = (last['max_token'] or 0) + 1

    # Get queue length
    pending_count = query_db(
        'SELECT COUNT(*) AS cnt FROM tokens WHERE doctor_id=%s AND booking_date=%s AND status="pending"',
        (doctor_id, today), one=True
    )
    wait_minutes = pending_count['cnt'] * doctor['avg_consultation_minutes']

    token_id = query_db(
        '''INSERT INTO tokens (user_id, doctor_id, hospital_id, token_number, booking_date, reason, estimated_wait_minutes)
           VALUES (%s,%s,%s,%s,%s,%s,%s)''',
        (current_user['user_id'], doctor_id, doctor['hospital_id'],
         token_number, today, reason, wait_minutes),
        commit=True
    )
    return jsonify({
        'message': 'Token booked successfully',
        'token_id': token_id,
        'token_number': token_number,
        'doctor_name': doctor['name'],
        'estimated_wait_minutes': wait_minutes,
        'hospital_id': doctor['hospital_id']
    }), 201

# ─── LIVE TOKEN STATUS ────────────────────────────────────────────────────────────
@tokens_bp.route('/api/tokens/live/<int:token_id>', methods=['GET'])
@require_role('patient')
def live_token(token_id, current_user):
    token = query_db(
        '''SELECT t.*, d.name AS doctor_name, d.avg_consultation_minutes,
                h.name AS hospital_name
            FROM tokens t
            JOIN doctors d ON d.id = t.doctor_id
            JOIN hospitals h ON h.id = t.hospital_id
            WHERE t.id=%s AND t.user_id=%s''',
        (token_id, current_user['user_id']), one=True
    )
    if not token:
        return jsonify({'error': 'Token not found'}), 404

    # Current serving token
    current_serving = query_db(
        '''SELECT token_number FROM tokens
            WHERE doctor_id=%s AND booking_date=%s AND status="in_service"
            ORDER BY token_number DESC LIMIT 1''',
        (token['doctor_id'], token['booking_date']), one=True
    )
    current_token = current_serving['token_number'] if current_serving else 0

    tokens_ahead = max(0, token['token_number'] - current_token - 1)
    wait_minutes = tokens_ahead * token['avg_consultation_minutes']

    return jsonify({
        'token_id': token['id'],
        'token_number': token['token_number'],
        'current_token': current_token,
        'tokens_ahead': tokens_ahead,
        'estimated_wait_minutes': wait_minutes,
        'status': token['status'],
        'doctor_name': token['doctor_name'],
        'hospital_name': token['hospital_name'],
        'booking_date': str(token['booking_date'])
    }), 200

# ─── MY TOKENS (Patient's history) ───────────────────────────────────────────────
@tokens_bp.route('/api/tokens/my', methods=['GET'])
@require_role('patient')
def my_tokens(current_user):
    tokens = query_db(
        '''SELECT t.*, d.name AS doctor_name, d.specialization,
                h.name AS hospital_name
            FROM tokens t
            JOIN doctors d ON d.id = t.doctor_id
            JOIN hospitals h ON h.id = t.hospital_id
            WHERE t.user_id=%s
            ORDER BY t.created_at DESC LIMIT 20''',
        (current_user['user_id'],)
    )
    result = []
    for t in tokens:
        t['booking_date'] = str(t['booking_date'])
        t['created_at'] = str(t['created_at'])
        t['completed_at'] = str(t['completed_at']) if t['completed_at'] else None
        result.append(t)
    return jsonify(result), 200

# ─── ADMIN: COMPLETE/UPDATE TOKEN STATUS ─────────────────────────────────────────
@tokens_bp.route('/api/tokens/<int:token_id>/status', methods=['PUT'])
@require_role('hospital_admin')
def update_token_status(token_id, current_user):
    data = request.get_json()
    new_status = data.get('status')
    if new_status not in ['pending', 'in_service', 'completed', 'cancelled']:
        return jsonify({'error': 'Invalid status'}), 400

    token = query_db(
        'SELECT * FROM tokens WHERE id=%s AND hospital_id=%s',
        (token_id, current_user['hospital_id']), one=True
    )
    if not token:
        return jsonify({'error': 'Token not found or not your hospital'}), 404

    if new_status == 'completed':
        query_db('UPDATE tokens SET status=%s, completed_at=CURRENT_TIMESTAMP WHERE id=%s',
                 (new_status, token_id), commit=True)
    else:
        query_db('UPDATE tokens SET status=%s WHERE id=%s',
                 (new_status, token_id), commit=True)

    return jsonify({'message': f'Token status updated to {new_status}'}), 200

# ─── ADMIN: TODAY'S QUEUE ─────────────────────────────────────────────────────────
@tokens_bp.route('/api/tokens/hospital/today', methods=['GET'])
@require_role('hospital_admin')
def hospital_today_tokens(current_user):
    doctor_id = request.args.get('doctor_id')
    sql = '''SELECT t.*, u.full_name AS patient_name, u.phone AS patient_phone,
                u.blood_group, d.name AS doctor_name, d.specialization
            FROM tokens t
            JOIN users u ON u.id = t.user_id
            JOIN doctors d ON d.id = t.doctor_id
            WHERE t.hospital_id=%s AND t.booking_date=date('now')'''
    params = [current_user['hospital_id']]
    if doctor_id:
        sql += ' AND t.doctor_id=%s'
        params.append(doctor_id)
    sql += ' ORDER BY t.doctor_id, t.token_number'

    tokens = query_db(sql, params)
    result = []
    for t in tokens:
        t['booking_date'] = str(t['booking_date'])
        t['created_at'] = str(t['created_at'])
        result.append(t)
    return jsonify(result), 200
