# --- routes/performance_routes.py ---
from flask import Blueprint, request, jsonify
from app.schemas.performance_schema import CourseSchema, CourseSubmissionSchema
from app.services.performance_service import (
    create_course,
    get_all_courses,
    submit_course,
    get_my_submissions,
    get_pending_submissions,
    review_submission
)
from flask_jwt_extended import jwt_required, get_jwt_identity

performance_bp = Blueprint('performance', __name__)

@performance_bp.route('/courses', methods=['GET'])
@jwt_required()
def list_courses():
    courses = get_all_courses()
    return jsonify(courses), 200

@performance_bp.route('/courses', methods=['POST'])
@jwt_required()
def add_course():
    data = request.get_json()
    course_schema = CourseSchema()
    errors = course_schema.validate(data)
    if errors:
        return jsonify(errors), 400
    course_id = create_course(data)
    return jsonify({"message": "Course created successfully", "course_id": course_id}), 201

@performance_bp.route('/courses/<int:course_id>/submit', methods=['POST'])
@jwt_required()
def submit_completion(course_id):
    data = request.get_json()
    notes = data.get("completion_notes", "")
    employee_id = get_jwt_identity()
    submission_id = submit_course(employee_id, course_id, notes)
    return jsonify({"message": "Submission sent", "submission_id": submission_id}), 201

@performance_bp.route('/my-submissions', methods=['GET'])
@jwt_required()
def my_submissions():
    employee_id = get_jwt_identity()
    submissions = get_my_submissions(employee_id)
    return jsonify(submissions), 200

@performance_bp.route('/submissions/pending', methods=['GET'])
@jwt_required()
def pending_submissions():
    submissions = get_pending_submissions()
    return jsonify(submissions), 200

@performance_bp.route('/submissions/<int:submission_id>/status', methods=['PUT'])
@jwt_required()
def update_status(submission_id):
    data = request.get_json()
    status = data.get('status')
    comment = data.get('reviewer_comment', '')
    reviewer_id = get_jwt_identity()
    try:
        review_submission(submission_id, status, comment, reviewer_id)
        return jsonify({"message": f"Submission {status.lower()}"}), 200
    except LookupError as le:
        return jsonify({"error": str(le)}), 404
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
