from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.service.performance_service import performance_service
from app.utils.auth import role_required

performance_bp = Blueprint('performance_routes', __name__)


# 1. Employee views their mandatory course based on department
@performance_bp.route('/performance/my-course', methods=['GET'])
@jwt_required()
def get_my_mandatory_course():
    identity = get_jwt_identity()
    department = identity.get("department")
    course = performance_service.get_course_by_department(department)
    if course:
        return jsonify({'department': department, 'mandatory_course': course}), 200
    return jsonify({'message': 'No course assigned for this department'}), 404


# # 2. Employee submits course completion details
# @performance_bp.route('/performance/submit', methods=['POST'])
# @jwt_required()
# def submit_course_completion():
#     identity = get_jwt_identity()

#     if identity.get("role") not in ["Employee", "Admin"]:
#         return jsonify({"error": "Unauthorized role"}), 403

#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "No input provided"}), 400

#     try:
#         employee_id = identity['employee_id']
#         performance_service.submit_completion(employee_id, data)
#         return jsonify({'message': 'Course completion submitted successfully'}), 201
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

@performance_bp.route('/performance/submit', methods=['POST'])
@jwt_required()
def submit_course_completion():
    identity = get_jwt_identity()

    if identity.get("role") not in ["Employee", "Admin"]:
        return jsonify({"error": "Unauthorized role"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "No input provided"}), 400

    try:
        employee_id = identity['employee_id']
        performance_service.submit_completion(employee_id, data)
        return jsonify({'message': 'Course completion submitted successfully'}), 201
    except Exception as e:
        error_msg = str(e)
        if "already submitted this course" in error_msg:
            return jsonify({'error': error_msg}), 409
        return jsonify({'error': error_msg}), 500


# 3. Employee views their own course submission history
@performance_bp.route('/performance/my-submissions', methods=['GET'])
@jwt_required()
def view_my_submissions():
    identity = get_jwt_identity()
    employee_id = identity['employee_id']
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    result = performance_service.get_submissions_by_employee(employee_id, page, per_page)
    return jsonify(result), 200


# 4. Admin views pending course submissions
@performance_bp.route('/performance/submissions/pending', methods=['GET'])
@jwt_required()
@role_required("Admin")
def view_pending_submissions():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    result = performance_service.get_pending_reviews(page, per_page)
    return jsonify(result), 200


# 5. Admin reviews (approve/reject) a specific submission
@performance_bp.route('/performance/submissions/<int:submission_id>/review', methods=['PUT'])
@jwt_required()
@role_required("Admin")
def review_submission(submission_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    admin_id = get_jwt_identity()['employee_id']
    try:
        performance_service.review_submission(submission_id, data, admin_id)
        return jsonify({'message': 'Review submitted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 6. Admin views all submissions (reviewed or not)
@performance_bp.route('/performance/submissions/all', methods=['GET'])
@jwt_required()
@role_required("Admin")
def view_all_submissions():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    result = performance_service.get_all_submissions(page, per_page)
    return jsonify(result), 200


# 7. Admin report: Completion rates by department
@performance_bp.route('/performance/reports/completion', methods=['GET'])
@jwt_required()
@role_required("Admin")
def report_completion_rates():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    try:
        report = performance_service.get_completion_by_department(page, per_page)
        return jsonify(report), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 8. Admin report: Ratings distribution across employees
@performance_bp.route('/performance/reports/ratings', methods=['GET'])
@jwt_required()
@role_required("Admin")
def report_ratings_distribution():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    try:
        ratings = performance_service.get_rating_distribution(page, per_page)
        return jsonify(ratings), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 9. Admin report: All submissions that are still pending review
@performance_bp.route('/performance/reports/pending', methods=['GET'])
@jwt_required()
@role_required("Admin")
def report_pending_reviews():
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)
    try:
        pending = performance_service.get_pending_reviews(page, per_page)
        return jsonify(pending), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500