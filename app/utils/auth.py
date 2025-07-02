from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from functools import wraps
from flask import jsonify

# def role_required(required_role):
#     def wrapper(fn):
#         @wraps(fn)
#         def decorator(*args, **kwargs):
#             verify_jwt_in_request()
#             identity = get_jwt_identity()
#             if identity["role"] != required_role:
#                 return jsonify({"error": "Unauthorized access"}), 403
#             return fn(*args, **kwargs)
#         return decorator
#     return wrapper
def role_required(required_role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()

            if not identity or not isinstance(identity, dict):
                return jsonify({"error": "Invalid token identity"}), 401

            role = identity.get("role")
            if role != required_role:
                return jsonify({"error": "Unauthorized access"}), 403

            return fn(*args, **kwargs)
        return decorator
    return wrapper
