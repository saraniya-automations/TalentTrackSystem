# app/routes/employee_profile_routes.py
from flask import Blueprint, request, jsonify
from app.service import employee_profile_service, user_service
from app.schemas.employee_profile_schema import EmployeeProfileSchema
from flask_jwt_extended import jwt_required
from app.utils.auth import role_required

profile_bp = Blueprint('profile_routes', __name__)
profile_schema = EmployeeProfileSchema()

@profile_bp.route('/profile/<string:employee_id>', methods=['GET'])
def get_profile(employee_id):
    if profile := employee_profile_service.get_profile_by_employee_id(
        employee_id
    ):
        return jsonify(profile), 200
    else:
        return jsonify({'error': 'Profile not found'}), 404

@profile_bp.route('/profile/<string:employee_id>', methods=['PUT'])
def update_profile(employee_id):
    data = request.get_json()
    if (errors := profile_schema.validate(data)):
        return jsonify({'errors': errors}), 400

    user = user_service.get_by_employee_id(employee_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if existing_profile := employee_profile_service.get_profile_by_employee_id(
        employee_id
    ):
        employee_profile_service.update_profile(user['employee_id'], data)
        return jsonify({'message': 'Profile updated successfully'}), 200
    else:
        employee_profile_service.create_profile(user['employee_id'], data)
        return jsonify({'message': 'Profile created successfully'}), 201

@profile_bp.route('/profiles', methods=['GET'])
@jwt_required()
@role_required("Admin")
def get_all_profiles():
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        key = request.args.get('key', '').strip()
        
        profiles = employee_profile_service.get_all_profiles(limit, offset, key)

        # No field removal — return full profile info
        return jsonify(profiles), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
