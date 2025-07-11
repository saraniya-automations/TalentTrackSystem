# --- routes/attendance_routes.py ---
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.service import attendence_service
from app.schemas.attendence_schema import ManualAttendanceSchema
from app.utils.auth import role_required

attendance_bp = Blueprint('attendance_bp', __name__)

@attendance_bp.route('/attendance/punch-in', methods=['POST'])
@jwt_required()
def punch_in():
    user = get_jwt_identity()
    attendence_service.punch_in(user["employee_id"])
    return jsonify({"message": "Punch in recorded"}), 200

@attendance_bp.route('/attendance/punch-out', methods=['POST'])
@jwt_required()
def punch_out():
    user = get_jwt_identity()
    attendence_service.punch_out(user["employee_id"])
    return jsonify({"message": "Punch out recorded"}), 200

@attendance_bp.route('/attendance/manual', methods=['POST'])
@jwt_required()
def manual_attendance():
    user = get_jwt_identity()
    print("JWT Identity:", user) 
    schema = ManualAttendanceSchema()
    data = request.get_json()
    if (errors := schema.validate(data)):
        return jsonify({"errors": errors}), 400
    attendence_service.manual_request(user["employee_id"], data)
    return jsonify({"message": "Manual attendance request submitted"}), 201

@attendance_bp.route('/attendance/my-records', methods=['GET'])
@jwt_required()
def my_attendance():
    user = get_jwt_identity()
    employee_id = user["employee_id"]

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    sort_by = request.args.get("sort_by", "punch_in")  # default sort by punch_in
    order = request.args.get("order", "asc")  # asc or desc

    records = attendence_service.get_employee_attendance(
        employee_id, start_date, end_date, sort_by, order
    )
    return jsonify(records), 200

@attendance_bp.route('/attendance/all-my-records', methods=['GET'])
@jwt_required()
def all_my_attendance():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    user = get_jwt_identity()
    employee_id = user["employee_id"]
    records = attendence_service.get_all_employee_attendance(employee_id,page, per_page)
    return jsonify(records), 200

@attendance_bp.route('/attendance/requests', methods=['GET'])
@jwt_required()
@role_required("Admin")
def get_requests():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    records = attendence_service.get_pending_requests(page, per_page)
    return jsonify(records), 200

@attendance_bp.route('/attendance/approve/<int:record_id>', methods=['PUT'])
@jwt_required()
@role_required("Admin")
def approve_attendance(record_id):
    identity = get_jwt_identity()
    approver_id = identity.get('employee_id')

    if not approver_id:
        return jsonify({'error': 'Invalid token: employee_id missing'}), 401
    
    try: 
        res = attendence_service.approve_request(record_id,approver_id)
        return res
    except Exception as e:  
        return jsonify({"error": str(e)}), 400
    # if not approver_id:
    #     return jsonify({'error': 'Invalid token: employee_id missing'}), 401
    # return jsonify({"message": "Attendance request approved"}), 200

@attendance_bp.route('/attendance/reject/<int:record_id>', methods=['PUT'])
@jwt_required()
@role_required("Admin")
def reject_attendance(record_id):
    identity = get_jwt_identity()
    approver_id = identity.get('employee_id')

    if not approver_id:
        return jsonify({'error': 'Invalid token: employee_id missing'}), 401
    
    data = request.get_json()
    reason = data.get("rejection_reason", "No reason provided") 
    try: 
        res = attendence_service.reject_request(record_id, reason,approver_id)
        return res
    except Exception as e:
        # return jsonify({"message": "Attendance request rejected"}), 200
        return jsonify({"error": str(e)}), 400

@attendance_bp.route('/attendance/search', methods=['GET'])
@jwt_required()
@role_required("Admin")
def search_attendance_by_name_and_period():
    name = request.args.get("name")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not name or not start_date or not end_date:
        return jsonify({"error": "Missing 'name', 'start', or 'end' query parameter"}), 400

    try:
        records = attendence_service.get_attendance_by_name_and_period(name, start_date, end_date)
        return jsonify(records), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500