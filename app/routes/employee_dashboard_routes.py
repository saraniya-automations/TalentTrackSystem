from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.service.employee_dashboard_service import EmployeeDashboardService

employee_dashboard_bp = Blueprint('employee_dashboard_routes', __name__)
dashboard_service = EmployeeDashboardService()

@employee_dashboard_bp.route('/employee/dashboard/summary', methods=['GET'])
@jwt_required()
def get_employee_dashboard_summary():
    identity = get_jwt_identity()
    employee_id = identity.get('employee_id')
    if not employee_id:
        return jsonify({"error": "Invalid token: employee_id missing"}), 401

    summary = dashboard_service.get_employee_summary(employee_id)
    return jsonify(summary), 200
