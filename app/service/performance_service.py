from app.models.performance import Performance

performance_model = Performance()

class PerformanceService:
    def get_course_by_department(self, department):
        return performance_model.get_course_by_department(department)

    def assign_course_to_user_if_exists(self, employee_id, department):
        performance_model.assign_course_to_user_if_exists(employee_id, department)

    def submit_completion(self, employee_id, data):
        performance_model.submit_completion(
            employee_id=employee_id,
            department=data['department'],
            course_name=data['course_name'],
            note=data.get('completion_note'),
            file_path=data.get('file_path'),
            date=data['completed_at']
        )

    def get_pending_reviews(self):
        return performance_model.get_pending_submissions()

    def review_submission(self, submission_id, data, admin_id):
        performance_model.review_submission(
            submission_id=submission_id,
            status=data['status'],
            rating=data['rating'],
            comment=data['admin_comment'],
            admin_id=admin_id
        )

    def get_all_submissions(self):
        return performance_model.get_all_submissions()

    def get_rating_distribution(self):
        return performance_model.get_rating_distribution()

    def get_completion_by_department(self):
        return performance_model.get_completion_by_department()

    def get_submissions_by_employee(self, employee_id):
        return performance_model.get_submissions_by_employee(employee_id)

performance_service = PerformanceService()