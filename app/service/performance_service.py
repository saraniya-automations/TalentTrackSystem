# --- app/services/performance_service.py ---

from app.models.performance import Performance
from app.models.user import User

performance_model = Performance()
user_model = User()

def get_department_courses(employee_id):
    """
    Returns all mandatory courses assigned to the department of the logged-in user.
    """
    user = user_model.get_by_employee_id(employee_id)
    if not user:
        raise LookupError("User not found")
    
    department = user.get('department')
    return performance_model.get_courses_by_department(department)

def submit_course(employee_id, course_id, notes):
    """
    Allows the logged-in employee to submit course completion for a given course ID.
    """
    return performance_model.submit_course_completion(employee_id, course_id, notes)

def get_my_submissions(employee_id):
    """
    Returns all submissions (completed courses) by the logged-in employee.
    """
    return performance_model.get_my_submissions(employee_id)

def get_pending_submissions():
    """
    Returns all course submissions that are still pending review.
    Admins can use this to view what needs approval.
    """
    return performance_model.get_pending_submissions()

def review_submission(submission_id, status, comment, reviewer_id):
    """
    Admin reviews and approves/rejects a course submission.
    - Cannot approve own submissions.
    - Only Admins can approve/reject.
    """
    submission = performance_model.get_submission_by_id(submission_id)
    if not submission:
        raise LookupError("Submission not found")

    applicant = user_model.get_by_employee_id(submission['employee_id'])
    reviewer = user_model.get_by_employee_id(reviewer_id)

    if not applicant or not reviewer:
        raise LookupError("User or reviewer not found")

    if reviewer['employee_id'] == applicant['employee_id']:
        raise PermissionError("Admins cannot approve their own submissions")

    if reviewer['role'].lower() != "admin":
        raise PermissionError("Only admins can approve submissions")

    if status not in ["Approved", "Rejected"]:
        raise ValueError("Invalid status. Must be Approved or Rejected")

    performance_model.update_submission_status(
        submission_id=submission_id,
        status=status,
        comment=comment,
        reviewer_id=reviewer_id
    )
