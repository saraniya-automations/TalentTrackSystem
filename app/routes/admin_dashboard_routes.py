from app.utils.auth import role_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.service.admin_dashboard_service import AdminDashboardService
from flask import Blueprint, request, jsonify

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
@role_required('Admin')
def get_dashboard_stats():
    service = AdminDashboardService()
    stats = service.get_dashboard_stats()
    return jsonify(stats), 200

@admin_bp.route('/attendance/weekly-chart', methods=['GET'])
@jwt_required()
@role_required('Admin')
def get_weekly_attendance_chart():
    department = request.args.get('department')  
    service = AdminDashboardService()
    data = service.get_weekly_attendance_for_chart(department)
    return jsonify(data), 200

@admin_bp.route('/dashboard/employee-growth', methods=['GET'])
@jwt_required()
@role_required('Admin')
def get_employee_growth():
    """Get employee growth data (monthly only)"""
    try:
        limit = int(request.args.get('limit', default=12))
        service = AdminDashboardService()
        growth_data = service.get_employee_growth_data(limit=limit)
        
        return jsonify({
            'success': True,
            'data': growth_data,
            'timeframe': 'monthly'  # Now hardcoded to monthly
        }), 200

    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Invalid limit parameter - must be a number'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@admin_bp.route('/dashboard/department-counts', methods=['GET'])
@jwt_required()
@role_required('Admin')
def get_department_counts():
    """
    Get employee counts grouped by department
    Returns:
        {
            "success": true,
            "data": {
                "HR": 5,
                "IT": 12,
                "Finance": 8
            }
        }
    """
    try:
        service = AdminDashboardService()
        department_counts = service.get_employee_counts_by_department()
        
        return jsonify({
            'success': True,
            'data': department_counts
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500