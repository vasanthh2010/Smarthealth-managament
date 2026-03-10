from functools import wraps
from flask import request, jsonify
import jwt
from config import Config

def get_current_user():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None, 'No token provided'
    token = auth_header.split(' ', 1)[1]
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, 'Token expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user, err = get_current_user()
        if err:
            return jsonify({'error': err}), 401
        return f(*args, current_user=user, **kwargs)
    return decorated

def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user, err = get_current_user()
            if err:
                return jsonify({'error': err}), 401
            if user.get('role') not in roles:
                return jsonify({'error': 'Access denied'}), 403
            return f(*args, current_user=user, **kwargs)
        return decorated
    return decorator
