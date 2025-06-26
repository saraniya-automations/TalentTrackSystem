from flask import Blueprint, request, jsonify
from app.service.leave_service import LeaveService
from app.service import manager_service
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.auth import role_required

leave_bp = Blueprint('leave_routes', __name__)
leave_service = LeaveService()

# Employee applies for leave
@leave_bp.route('/leave/apply', methods=['POST'])
@jwt_required()
def apply_leave():
    data = request.get_json()
    identity = get_jwt_identity()

    required_fields = ['leave_type', 'start_date', 'end_date', 'reason']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    result, code = leave_service.apply_leave(
        employee_id=identity['employee_id'],
        leave_type=data['leave_type'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        reason=data['reason']
    )
    return jsonify(result), code

# Employee checks leave balance
@leave_bp.route('/leave/balance', methods=['GET'])
@jwt_required()
def get_balance():
    identity = get_jwt_identity()
    balance = leave_service.get_leave_balance(identity['employee_id'])
    if not balance:
        return jsonify({'error': 'Balance not found'}), 404
    return jsonify(balance), 200

# Manager Approves or Rejects leave
@leave_bp.route('/leave/<int:leave_id>/status', methods=['PUT'])
@jwt_required()
@role_required('Manager')
def update_leave_status(leave_id):
    data = request.get_json()
    status = data.get('status')

    if status not in ['Approved', 'Rejected']:
        return jsonify({'error': 'Invalid status. Must be "Approved" or "Rejected".'}), 400

    try:
        result = manager_service.update_leave_status(leave_id, status)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Manager views all pending leave requests
@leave_bp.route('/leave/pending', methods=['GET'])
@jwt_required()
@role_required('Manager')
def get_pending_leaves():
    identity = get_jwt_identity()
    manager_id = identity['employee_id']
    pending = manager_service.get_pending_leaves(manager_id)
    return jsonify(pending), 200
