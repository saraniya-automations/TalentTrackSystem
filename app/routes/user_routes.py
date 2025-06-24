from flask import Blueprint, request, jsonify
from app.service import user_service
from app.schemas.user_schema import UserSchema
from app.utils.logger import logger
from werkzeug.security import check_password_hash
from app.utils.token_util import generate_token

user_bp = Blueprint('user_routes', __name__)
user_schema = UserSchema()

@user_bp.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    if (errors := user_schema.validate(data)):
        return jsonify({'errors': errors}), 400

    try:
        employee_id = user_service.create_user(data)
        return jsonify({'message': 'User created', 'id': employee_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users', methods=['GET'])
def get_all_users():
    users = user_service.get_users()
    for user in users:
        user.pop('password_hash', None)
    return jsonify(users)

@user_bp.route('/users/search', methods=['GET'])
def search_user():
    name = request.args.get('name', '')
    users = user_service.search_users(name)
    
    # Remove password_hash from each user dict
    for user in users:
        user.pop('password_hash', None)
    
    return jsonify(users)


@user_bp.route('/users/<string:employee_id>', methods=['PUT'])
def update_user(employee_id):
    data = request.get_json()

    if (errors := user_schema.validate(data)):
        return jsonify({'errors': errors}), 400

    # Find user by employee_id first
    user = user_service.get_by_employee_id(employee_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        user_service.update_user(user['id'], data)  # use numeric id internally
        return jsonify({'message': 'User updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<string:employee_id>', methods=['DELETE'])
def delete_user(employee_id):
    try:
        user_service.delete_user(employee_id)
        return jsonify({'message': 'User deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = user_service.get_by_email(email)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid email or password'}), 401

    return jsonify({
        'message': 'Login successful',
        'employee_id': user['employee_id'],
        'role': user['role'],
        'status': user['status']
    }), 200


@user_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    user = user_service.get_by_email(email)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    token = generate_token()
    user_service.store_reset_token(user['id'], token)

    # Simulate email (just return token in response for now)
    return jsonify({
        'message': 'Password reset token generated',
        'reset_token': token  
    }), 200

@user_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('new_password')

    employee_id = user_service.get_user_id_by_token(token)
    if not employee_id:
        return jsonify({'error': 'Invalid or expired token'}), 400

    user_service.update_password(employee_id, new_password)
    return jsonify({'message': 'Password updated successfully'}), 200

