# app/routes/leave_routes.py

from flask import Blueprint, request, jsonify
from app.service.leave_service import LeaveService
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.auth import role_required
from app.schemas.leave_schema import LeaveApplySchema, LeaveStatusUpdateSchema

leave_bp = Blueprint('leave_routes', __name__)
leave_service = LeaveService()

@leave_bp.route('/leave/apply', methods=['POST'])
@jwt_required()
def apply_leave():
    identity = get_jwt_identity()
    employee_id = identity.get('employee_id')
    if not employee_id:
        return jsonify({'error': 'Invalid token: employee_id missing'}), 401

    data = request.get_json()
    schema = LeaveApplySchema()
    if (errors := schema.validate(data)):
        return jsonify({'errors': errors}), 400

    result, code = leave_service.apply_leave(
        employee_id,
        data['leave_type'],
        str(data['start_date']),
        str(data['end_date']),
        data['reason']
    )
    return jsonify(result), code

@leave_bp.route('/leave/balance', methods=['GET'])
@jwt_required()
def get_balance():
    identity = get_jwt_identity()
    employee_id = identity.get('employee_id')
    if not employee_id:
        return jsonify({'error': 'Invalid token: employee_id missing'}), 401

    balance = leave_service.get_leave_balance(employee_id)
    if not balance:
        return jsonify({'error': 'Balance not found'}), 404
    return jsonify(balance), 200

@leave_bp.route('/leave/my', methods=['GET'])
@jwt_required()
def get_my_leaves():
    identity = get_jwt_identity()
    employee_id = identity.get('employee_id')
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    result, code = leave_service.get_user_leave_details(employee_id, page, per_page)
    return jsonify(result), code


@leave_bp.route('/leave/<int:leave_id>/status', methods=['PUT'])
@jwt_required()
@role_required('Admin')
def update_leave_status(leave_id):
    identity = get_jwt_identity()
    approver_id = identity.get('employee_id')
    if not approver_id:
        return jsonify({'error': 'Invalid token: employee_id missing'}), 401

    data = request.get_json()
    schema = LeaveStatusUpdateSchema()
    if (errors := schema.validate(data)):
        return jsonify({'errors': errors}), 400

    result, code = leave_service.update_leave_status(leave_id, data['status'], approver_id)
    return jsonify(result), code

@leave_bp.route('/leave/pending', methods=['GET'])
@jwt_required()
@role_required('Admin')
def get_pending_leaves():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    result, code = leave_service.get_pending_leaves(page, per_page)
    return jsonify(result), code


@leave_bp.route('/leave/search', methods=['GET'])
@jwt_required()
@role_required('Admin')
def search_employee_leaves():
    name = request.args.get('name')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    if not name or not start_date or not end_date:
        return jsonify({'error': 'name, start_date, and end_date are required'}), 400

    result, code = leave_service.get_employee_leave_details(
        name, start_date, end_date, page, per_page
    )
    return jsonify(result), code

