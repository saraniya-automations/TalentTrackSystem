from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.performance_schema import CourseSubmissionSchema
from app.service.performance_service import (
    get_department_courses,
    submit_course,
    get_my_submissions,
    get_pending_submissions,
    review_submission
)
from app.utils.auth import role_required

performance_bp = Blueprint('performance', __name__)

# ✅ Get all department-specific mandatory courses
@performance_bp.route('/courses', methods=['GET'])
@jwt_required()
def list_department_courses():
    identity = get_jwt_identity()
    employee_id = identity['employee_id']
    try:
        courses = get_department_courses(employee_id)
        return jsonify(courses), 200
    except LookupError as e:
        return jsonify({"error": str(e)}), 404

# ✅ Employee submits a completed course
@performance_bp.route('/courses/<int:course_id>/submit', methods=['POST'])
@jwt_required()
def submit_completion(course_id):
    data = request.get_json()
    notes = data.get("completion_notes", "")
    identity = get_jwt_identity()
    employee_id = identity["employee_id"]

    submission_id = submit_course(employee_id, course_id, notes)
    return jsonify({
        "message": "Submission sent",
        "submission_id": submission_id
    }), 201

# ✅ Employee views their submitted courses
@performance_bp.route('/my-submissions', methods=['GET'])
@jwt_required()
def my_submissions():
    identity = get_jwt_identity()
    employee_id = identity["employee_id"]
    submissions = get_my_submissions(employee_id)
    return jsonify(submissions), 200

# ✅ Admin views all pending course submissions
@performance_bp.route('/submissions/pending', methods=['GET'])
@jwt_required()
@role_required("Admin")
def pending_submissions():
    submissions = get_pending_submissions()
    return jsonify(submissions), 200

# ✅ Admin approves or rejects a course submission with comment
@performance_bp.route('/submissions/<int:submission_id>/status', methods=['PUT'])
@jwt_required()
@role_required("Admin")
def update_status(submission_id):
    data = request.get_json()
    status = data.get('status')
    comment = data.get('reviewer_comment', '')
    identity = get_jwt_identity()
    reviewer_id = identity["employee_id"]

    try:
        review_submission(submission_id, status, comment, reviewer_id)
        return jsonify({"message": f"Submission {status.lower()}"}), 200
    except LookupError as le:
        return jsonify({"error": str(le)}), 404
    except PermissionError as pe:
        return jsonify({"error": str(pe)}), 403
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
