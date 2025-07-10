from app.models.performance import Performance

performance_model = Performance()

class PerformanceService:
    def __init__(self):
        self.performance_model = Performance()  # ✅ Fix: instantiate model

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

    def get_pending_reviews(self, page, per_page):
        items = self.performance_model.get_pending_submissions(page, per_page)
        total = self.performance_model.get_pending_submissions_count()
        return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

    def review_submission(self, submission_id, data, admin_id):
        # Fetch the submission to check who submitted it
        submissions = performance_model.get_all_submissions()
        submission = next((s for s in submissions if s['id'] == submission_id), None)

        if not submission:
            raise ValueError("Submission not found.")

        if submission['employee_id'] == admin_id:
            raise PermissionError("Admins cannot review their own submissions.")
        performance_model.review_submission(
            submission_id=submission_id,
            status=data['status'],
            rating=data['rating'],
            comment=data['admin_comment'],
            admin_id=admin_id
        )

    def get_all_submissions(self, page, per_page):
        items = self.performance_model.get_all_submissions(page, per_page)
        total = self.performance_model.get_all_submissions_count()
        return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

    def get_rating_distribution(self, page, per_page):
        items = self.performance_model.get_rating_distribution(page, per_page)
        total = self.performance_model.get_rating_distribution_count()
        return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }

    def get_completion_by_department(self, page, per_page):
        items = self.performance_model.get_completion_by_department(page, per_page)
        total = self.performance_model.get_completion_by_department_count()
        return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }


    def get_submissions_by_employee(self, employee_id, page, per_page):
        submissions = self.performance_model.get_submissions_by_employee(employee_id, page, per_page)
        total = self.performance_model.get_submissions_by_employee_count(employee_id)
        return {
            "items": submissions,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }

performance_service = PerformanceService()