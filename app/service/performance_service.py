# --- services/performance_service.py ---
from app.models.performance import Performance

performance_model = Performance()

def create_course(data):
    return performance_model.create_course(data)

def get_all_courses():
    return performance_model.get_all_courses()

def submit_course(employee_id, course_id, notes):
    return performance_model.submit_course_completion(employee_id, course_id, notes)

def get_my_submissions(employee_id):
    return performance_model.get_my_submissions(employee_id)

def get_pending_submissions():
    return performance_model.get_pending_submissions()

def review_submission(submission_id, status, comment, reviewer_id):
    submission = performance_model.get_submission_by_id(submission_id)
    if not submission:
        raise LookupError("Submission not found")
    if status not in ["Approved", "Rejected"]:
        raise ValueError("Invalid status. Must be Approved or Rejected")
    performance_model.update_submission_status(submission_id, status, comment, reviewer_id)
