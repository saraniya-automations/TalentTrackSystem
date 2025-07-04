# app/models/performance.py
from datetime import datetime
from app.models.database import Database

DEPARTMENT_COURSE_MAP = {
    "IT": "Cybersecurity",
    "Operations": "Compliance",
    "HR": "Onboarding",
    "Finance": "Role-Based Training",
    "Sales and Marketing": "Ethics & Conduct"
}

class Performance(Database):
    def __init__(self):
        super().__init__()

    def get_course_by_department(self, department):
        cursor = self.conn.execute('''
            SELECT course_name FROM courses WHERE department = ?
        ''', (department,))
        row = cursor.fetchone()
        return row['course_name'] if row else None

    def assign_course_to_department(self, department, course_name):
        self.conn.execute('''
            INSERT OR IGNORE INTO courses (department, course_name)
            VALUES (?, ?)
        ''', (department, course_name))
        self.conn.commit()

    def seed_default_courses(self):
        for dept, course in DEPARTMENT_COURSE_MAP.items():
            self.assign_course_to_department(dept, course)

    def assign_course_to_user_if_exists(self, employee_id, department):
        course = self.get_course_by_department(department)
        if course:
            self.conn.execute('''
                INSERT INTO course_submissions (
                    employee_id, department, course_name, status
                ) VALUES (?, ?, ?, 'Pending')
            ''', (employee_id, department, course))
            self.conn.commit()

    def submit_completion(self, employee_id, department, course_name, note, file_path, date):
        self.conn.execute('''
            INSERT INTO course_submissions (
                employee_id, department, course_name, completion_note,
                file_path, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (employee_id, department, course_name, note, file_path, date))
        self.conn.commit()

    def get_submissions_by_employee(self, employee_id):
        cursor = self.conn.execute('''
            SELECT * FROM course_submissions WHERE employee_id = ?
        ''', (employee_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_pending_submissions(self):
        cursor = self.conn.execute('''
            SELECT * FROM course_submissions WHERE status = 'Pending'
        ''')
        return [dict(row) for row in cursor.fetchall()]

    def review_submission(self, submission_id, status, rating, comment, admin_id):
        self.conn.execute('''
            UPDATE course_submissions
            SET status = ?, rating = ?, admin_comment = ?, reviewed_by = ?, reviewed_at = ?
            WHERE id = ?
        ''', (status, rating, comment, admin_id, datetime.now().isoformat(), submission_id))
        self.conn.commit()

    def get_all_submissions(self):
        cursor = self.conn.execute('SELECT * FROM course_submissions')
        return [dict(row) for row in cursor.fetchall()]

    def get_rating_distribution(self):
        cursor = self.conn.execute('''
            SELECT rating, COUNT(*) as count FROM course_submissions
            WHERE rating IS NOT NULL GROUP BY rating
        ''')
        return [dict(row) for row in cursor.fetchall()]

    def get_completion_by_department(self):
        cursor = self.conn.execute('''
            SELECT department, COUNT(*) as completed FROM course_submissions
            WHERE status = 'Approved' GROUP BY department
        ''')
        return [dict(row) for row in cursor.fetchall()]
