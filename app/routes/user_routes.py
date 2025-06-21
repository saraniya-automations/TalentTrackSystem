from flask import Blueprint, request, jsonify
from app.service import user_service
from app.schemas.user_schema import UserSchema
from app.utils.logger import logger

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
        user_id = user_service.create_user(data)
        return jsonify({'message': 'User created', 'id': user_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users', methods=['GET'])
def get_all_users():
    users = user_service.get_users()
    return jsonify(users)

@user_bp.route('/users/search', methods=['GET'])
def search_user():
    name = request.args.get('name', '')
    return jsonify(user_service.search_users(name))

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    if (errors := user_schema.validate(data)):
        return jsonify({'errors': errors}), 400

    try:
        user_service.update_user(user_id, data)
        return jsonify({'message': 'User updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user_service.delete_user(user_id)
        return jsonify({'message': 'User deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
