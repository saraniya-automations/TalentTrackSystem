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


@attendance_bp.route('/attendance/requests', methods=['GET'])
@jwt_required()
@role_required("Admin")
def get_requests():
    records = attendence_service.get_pending_requests()
    return jsonify(records), 200

@attendance_bp.route('/attendance/approve/<int:record_id>', methods=['PUT'])
@jwt_required()
@role_required("Admin")
def approve_attendance(record_id):
    attendence_service.approve_request(record_id)
    return jsonify({"message": "Attendance request approved"}), 200

@attendance_bp.route('/attendance/reject/<int:record_id>', methods=['PUT'])
@jwt_required()
@role_required("Admin")
def reject_attendance(record_id):
    data = request.get_json()
    reason = data.get("rejection_reason", "No reason provided")  # Optional
    attendence_service.reject_request(record_id, reason)
    return jsonify({"message": "Attendance request rejected"}), 200