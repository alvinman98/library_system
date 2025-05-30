from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User
from functools import wraps
from flask import jsonify

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = int(get_jwt_identity())  # convert back to int if needed
        user = User.query.get(user_id)
        if user.role.name != "admin":
            return jsonify({"error": "Admin only"}), 403
        return fn(*args, **kwargs)
    return wrapper
