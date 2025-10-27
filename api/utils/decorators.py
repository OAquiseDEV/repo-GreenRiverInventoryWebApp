from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def role_required(*allowed_role_ids):
    """
    Decorator to restrict access to specific roles.

    Usage:
        @role_required(1, 2)  # Allow Administrador and Oficina
        def some_endpoint():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            current_user = get_jwt_identity()

            if not current_user or 'role_id' not in current_user:
                return jsonify({"error": "Sin permisos"}), 403

            if current_user['role_id'] not in allowed_role_ids:
                return jsonify({"error": "Sin permisos"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator

def jwt_optional_with_qr_fallback():
    """
    Decorator for endpoints that can be accessed either with JWT or with QR code validation.
    Used for public manifest verification pages.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Try to verify JWT, but don't fail if it's not present
            try:
                verify_jwt_in_request(optional=True)
            except:
                pass
            return fn(*args, **kwargs)
        return wrapper
    return decorator
