from flask import Blueprint, request, jsonify
from db import query_db
from middleware import require_auth, require_role

hospitals_bp = Blueprint('hospitals', __name__)

# ─── LIST ALL APPROVED HOSPITALS ────────────────────────────────────────────────
@hospitals_bp.route('/api/hospitals', methods=['GET'])
def list_hospitals():
    search = request.args.get('search', '')
    city = request.args.get('city', '')

    sql = '''
        SELECT h.*,
            COUNT(DISTINCT d.id) AS doctor_count,
            SUM(CASE WHEN b.status='available' THEN 1 ELSE 0 END) AS available_beds,
            COUNT(DISTINCT b.id) AS total_bed_count,
            SUM(CASE WHEN t.status='pending' THEN 1 ELSE 0 END) AS queue_count
        FROM hospitals h
        LEFT JOIN doctors d ON d.hospital_id = h.id AND d.is_available=1
        LEFT JOIN beds b ON b.hospital_id = h.id
        LEFT JOIN tokens t ON t.hospital_id = h.id AND t.booking_date = date('now')
        WHERE h.status = 'approved'
    '''
    params = []
    if search:
        sql += ' AND (h.name LIKE %s OR h.city LIKE %s OR h.address LIKE %s)'
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    if city:
        sql += ' AND h.city LIKE %s'
        params.append(f'%{city}%')
    sql += ' GROUP BY h.id ORDER BY h.name'

    hospitals = query_db(sql, params)
    for h in hospitals:
        h['available_beds'] = int(h['available_beds'] or 0)
        h['total_bed_count'] = int(h['total_bed_count'] or 0)
        h['queue_count'] = int(h['queue_count'] or 0)
        h['doctor_count'] = int(h['doctor_count'] or 0)
        h['location_lat'] = float(h['location_lat']) if h['location_lat'] else None
        h['location_lng'] = float(h['location_lng']) if h['location_lng'] else None
        # Remove sensitive fields
        h.pop('password_hash', None)
        h.pop('login_id', None)
    return jsonify(hospitals), 200

# ─── HOSPITAL DETAIL ─────────────────────────────────────────────────────────────
@hospitals_bp.route('/api/hospitals/<int:hospital_id>', methods=['GET'])
def hospital_detail(hospital_id):
    hospital = query_db(
        'SELECT * FROM hospitals WHERE id=%s AND status="approved"',
        (hospital_id,), one=True
    )
    if not hospital:
        return jsonify({'error': 'Hospital not found'}), 404
    hospital.pop('password_hash', None)
    hospital.pop('login_id', None)

    # Get doctors with today's queue count
    doctors = query_db(
        '''SELECT d.*,
                COUNT(CASE WHEN t.status='pending' AND t.booking_date=date('now') THEN 1 END) AS queue_count,
                MAX(CASE WHEN t.status='in_service' THEN t.token_number END) AS current_token
            FROM doctors d
            LEFT JOIN tokens t ON t.doctor_id = d.id
            WHERE d.hospital_id = %s
            GROUP BY d.id
            ORDER BY d.specialization''',
        (hospital_id,)
    )

    # Bed summary
    beds = query_db(
        '''SELECT ward_type,
                SUM(CASE WHEN status='available' THEN 1 ELSE 0 END) AS available,
                SUM(CASE WHEN status='occupied' THEN 1 ELSE 0 END) AS occupied,
                COUNT(*) AS total
            FROM beds WHERE hospital_id=%s GROUP BY ward_type''',
        (hospital_id,)
    )

    hospital['doctors'] = doctors
    hospital['bed_summary'] = beds
    hospital['location_lat'] = float(hospital['location_lat']) if hospital['location_lat'] else None
    hospital['location_lng'] = float(hospital['location_lng']) if hospital['location_lng'] else None
    return jsonify(hospital), 200

# ─── HOSPITAL ADMIN: UPDATE OWN HOSPITAL ─────────────────────────────────────────
@hospitals_bp.route('/api/hospitals/my', methods=['GET'])
@require_role('hospital_admin')
def get_my_hospital(current_user):
    hospital_id = current_user['hospital_id']
    hospital = query_db('SELECT * FROM hospitals WHERE id=%s', (hospital_id,), one=True)
    if not hospital:
        return jsonify({'error': 'Not found'}), 404
    hospital.pop('password_hash', None)

    doctors = query_db('SELECT * FROM doctors WHERE hospital_id=%s ORDER BY specialization', (hospital_id,))
    beds_summary = query_db(
        '''SELECT ward_type,
            SUM(CASE WHEN status="available" THEN 1 ELSE 0 END) AS available,
            SUM(CASE WHEN status="occupied" THEN 1 ELSE 0 END) AS occupied,
            COUNT(*) AS total
            FROM beds WHERE hospital_id=%s GROUP BY ward_type''',
        (hospital_id,)
    )
    today_tokens = query_db(
        '''SELECT t.*, u.full_name AS patient_name, u.phone AS patient_phone,
                d.name AS doctor_name
            FROM tokens t
            JOIN users u ON u.id = t.user_id
            JOIN doctors d ON d.id = t.doctor_id
            WHERE t.hospital_id=%s AND t.booking_date=date('now')
            ORDER BY t.token_number''',
        (hospital_id,)
    )

    hospital['doctors'] = doctors
    hospital['bed_summary'] = beds_summary
    hospital['today_tokens'] = today_tokens
    return jsonify(hospital), 200

@hospitals_bp.route('/api/hospitals/my', methods=['PUT'])
@require_role('hospital_admin')
def update_my_hospital(current_user):
    hospital_id = current_user['hospital_id']
    data = request.get_json()

    fields = ['name', 'address', 'city', 'state', 'pincode', 'phone', 'email', 'description', 'location_lat', 'location_lng']
    updates = []
    params = []

    for field in fields:
        if field in data:
            updates.append(f"{field}=%s")
            params.append(data[field])

    if not updates:
        return jsonify({'error': 'No fields provided for update'}), 400

    sql = f"UPDATE hospitals SET {', '.join(updates)} WHERE id=%s"
    params.append(hospital_id)

    query_db(sql, params, commit=True)

    # Get updated hospital for broadcasting
    updated_hosp = query_db('SELECT * FROM hospitals WHERE id=%s', (hospital_id,), one=True)
    updated_hosp.pop('password_hash', None)
    updated_hosp.pop('login_id', None)

    # Emit WebSocket event
    from app import socketio
    socketio.emit('hospital_update', updated_hosp)

    return jsonify({'message': 'Profile updated successfully', 'hospital': updated_hosp}), 200

@hospitals_bp.route('/api/hospitals/my/stats', methods=['GET'])
@require_role('hospital_admin')
def get_hospital_stats(current_user):
    hospital_id = current_user['hospital_id']
    stats = query_db(
        '''SELECT
            (SELECT COUNT(*) FROM doctors WHERE hospital_id=%s) AS total_doctors,
            (SELECT COUNT(*) FROM doctors WHERE hospital_id=%s AND is_available=1) AS available_doctors,
            (SELECT COUNT(*) FROM beds WHERE hospital_id=%s) AS total_beds,
            (SELECT COUNT(*) FROM beds WHERE hospital_id=%s AND status="available") AS available_beds,
            (SELECT COUNT(*) FROM tokens WHERE hospital_id=%s AND booking_date=date('now')) AS today_patients,
            (SELECT COUNT(*) FROM tokens WHERE hospital_id=%s AND booking_date=date('now') AND status="completed") AS completed_today,
            (SELECT COUNT(*) FROM tokens WHERE hospital_id=%s AND booking_date=date('now') AND status="pending") AS pending_today
        ''',
        (hospital_id, hospital_id, hospital_id, hospital_id, hospital_id, hospital_id, hospital_id),
        one=True
    )
    return jsonify(stats), 200
