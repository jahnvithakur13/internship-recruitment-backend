from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from src.config.database import get_db

def get_current_user():
    user_id = get_jwt_identity()
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    db.close()
    return user

def jwt_required_custom(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception as e:
            return jsonify({"success": False, "message": "Missing or invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception:
                return jsonify({"success": False, "message": "Missing or invalid token"}), 401
            user = get_current_user()
            if not user or user["role"] not in roles:
                return jsonify({"success": False, "message": f"Access denied. Required role: {', '.join(roles)}"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
