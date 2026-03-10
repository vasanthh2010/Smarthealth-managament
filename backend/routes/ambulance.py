from flask import Blueprint, request, jsonify
from db import query_db
from middleware import require_role

ambulance_bp = Blueprint('ambulance', __name__)

# ─── BOOK AMBULANCE ───────────────────────────────────────────────────────────────
@ambulance_bp.route('/api/ambulance/request', methods=['POST'])
@require_role('patient')
def request_ambulance(current_user):
    data = request.get_json()
    required = ['patient_name', 'patient_phone', 'pickup_address']
    for f in required:
        if not data.get(f):
            return jsonify({'error': f'{f} is required'}), 400

    # Find nearest hospital with available beds (simplistic: pick first approved hospital with available bed)
    nearest = query_db(
        '''SELECT h.id, h.name, h.address, h.phone,
                COUNT(b.id) AS available_beds
            FROM hospitals h
            JOIN beds b ON b.hospital_id = h.id AND b.status='available'
            WHERE h.status='approved'
            GROUP BY h.id
            ORDER BY available_beds DESC LIMIT 1''',
        one=True
    )
    hospital_id = nearest['id'] if nearest else None

    req_id = query_db(
        '''INSERT INTO ambulance_requests
           (user_id, patient_name, patient_phone, pickup_address, pickup_lat, pickup_lng,
            hospital_id, emergency_type, notes)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
        (current_user['user_id'], data['patient_name'], data['patient_phone'],
         data['pickup_address'], data.get('pickup_lat'), data.get('pickup_lng'),
         hospital_id, data.get('emergency_type', 'General'), data.get('notes', '')),
        commit=True
    )

    response = {
        'message': 'Ambulance requested successfully',
        'request_id': req_id,
        'status': 'requested'
    }
    if nearest:
        response['assigned_hospital'] = {
            'id': nearest['id'],
            'name': nearest['name'],
            'address': nearest['address'],
            'phone': nearest['phone'],
            'available_beds': int(nearest['available_beds'])
        }
    return jsonify(response), 201

# ─── GET NEAREST HOSPITAL WITH BEDS ──────────────────────────────────────────────
@ambulance_bp.route('/api/ambulance/nearest', methods=['GET'])
def nearest_hospital():
    hospitals = query_db(
        '''SELECT h.id, h.name, h.address, h.city, h.phone,
                h.location_lat, h.location_lng,
                COUNT(b.id) AS available_beds
            FROM hospitals h
            JOIN beds b ON b.hospital_id = h.id AND b.status='available'
            WHERE h.status='approved'
            GROUP BY h.id
            HAVING available_beds > 0
            ORDER BY available_beds DESC LIMIT 5''',
    )
    result = []
    for h in hospitals:
        result.append({
            'id': h['id'],
            'name': h['name'],
            'address': h['address'],
            'city': h['city'],
            'phone': h['phone'],
            'location_lat': float(h['location_lat']) if h['location_lat'] else None,
            'location_lng': float(h['location_lng']) if h['location_lng'] else None,
            'available_beds': int(h['available_beds'])
        })
    return jsonify(result), 200

# ─── MY AMBULANCE REQUESTS ────────────────────────────────────────────────────────
@ambulance_bp.route('/api/ambulance/my', methods=['GET'])
@require_role('patient')
def my_requests(current_user):
    requests_list = query_db(
        '''SELECT a.*, h.name AS hospital_name, h.phone AS hospital_phone
            FROM ambulance_requests a
            LEFT JOIN hospitals h ON h.id = a.hospital_id
            WHERE a.user_id=%s ORDER BY a.created_at DESC LIMIT 10''',
        (current_user['user_id'],)
    )
    result = []
    for r in requests_list:
        r['created_at'] = str(r['created_at'])
        result.append(r)
    return jsonify(result), 200
