# app/models/performance.py
from datetime import datetime
from app.models.database import Database

DEPARTMENT_COURSE_MAP = {
    "IT": "Cybersecurity",
    "Operations": "Compliance",
    "HR": "Onboarding",
    "Finance": "Role-Based Training",
    "Sales": "Ethics & Conduct"
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

    # def submit_completion(self, employee_id, department, course_name, note, file_path, date):
    #     self.conn.execute('''
    #         INSERT INTO course_submissions (
    #             employee_id, department, course_name, completion_note,
    #             file_path, completed_at
    #         ) VALUES (?, ?, ?, ?, ?, ?)
    #     ''', (employee_id, department, course_name, note, file_path, date))
    #     self.conn.commit()

    def submit_completion(self, employee_id, department, course_name, note, file_path, date):
    # Check how many times the user has submitted this course
        cursor = self.conn.execute('''
            SELECT COUNT(*) as count FROM course_submissions
            WHERE employee_id = ? AND LOWER(course_name) = LOWER(?)
        ''', (employee_id, course_name.strip()))
    
        result = cursor.fetchone()
        if result['count'] >= 2:
            raise Exception("You have already submitted this course. No more submissions allowed.")

    # Proceed to insert new submission
        self.conn.execute('''
            INSERT INTO course_submissions (
                employee_id, department, course_name, completion_note,
                file_path, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (employee_id, department, course_name.strip(), note, file_path, date))
        self.conn.commit()


    def get_submissions_by_employee(self, employee_id, page, per_page):
        offset = (page - 1) * per_page
        cursor = self.conn.execute('''
        SELECT * FROM course_submissions 
        WHERE employee_id = ?
        LIMIT ? OFFSET ?
        ''', (employee_id, per_page, offset))  # ✅ No ORDER BY
        return [dict(row) for row in cursor.fetchall()]


    
    def get_submissions_by_employee_count(self, employee_id):
        cursor = self.conn.execute('''
        SELECT COUNT(*) FROM course_submissions WHERE employee_id = ?
        ''', (employee_id,))
        return cursor.fetchone()[0]

    def get_pending_submissions(self, page=1, per_page=10):
        offset = (page - 1) * per_page
        cursor = self.conn.execute('''
        SELECT * FROM course_submissions 
        WHERE status = 'Pending'
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        ''', (per_page, offset))
        return [dict(row) for row in cursor.fetchall()]

    
    def get_pending_submissions_count(self):
        cursor = self.conn.execute('''
        SELECT COUNT(*) FROM course_submissions WHERE status = 'Pending'
        ''')
        return cursor.fetchone()[0]

    def review_submission(self, submission_id, status, rating, comment, admin_id):
        self.conn.execute('''
            UPDATE course_submissions
            SET status = ?, rating = ?, admin_comment = ?, reviewed_by = ?, reviewed_at = ?
            WHERE id = ?
        ''', (status, rating, comment, admin_id, datetime.now().isoformat(), submission_id))
        self.conn.commit()

    def get_all_submissions(self, page=1, per_page=10):
        offset = (page - 1) * per_page
        cursor = self.conn.execute('''
        SELECT * FROM course_submissions
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        ''', (per_page, offset))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_submissions_count(self):
        cursor = self.conn.execute('SELECT COUNT(*) FROM course_submissions')
        return cursor.fetchone()[0]

    def get_rating_distribution(self, page=1, per_page=10):
        offset = (page - 1) * per_page
        cursor = self.conn.execute('''
        SELECT rating, COUNT(*) as count
        FROM course_submissions
        WHERE rating IS NOT NULL
        GROUP BY rating
        LIMIT ? OFFSET ?
        ''', (per_page, offset))
        return [dict(row) for row in cursor.fetchall()]

    def get_rating_distribution_count(self):
        cursor = self.conn.execute('''
        SELECT COUNT(DISTINCT rating)
        FROM course_submissions
        WHERE rating IS NOT NULL
        ''')
        return cursor.fetchone()[0]


    def get_completion_by_department(self, page=1, per_page=10):
        offset = (page - 1) * per_page
        cursor = self.conn.execute('''
        SELECT department, COUNT(*) as completed
        FROM course_submissions
        WHERE status = 'Approved'
        GROUP BY department
        LIMIT ? OFFSET ?
        ''', (per_page, offset))
        return [dict(row) for row in cursor.fetchall()]

    def get_completion_by_department_count(self):
        cursor = self.conn.execute('''
        SELECT COUNT(DISTINCT department)
        FROM course_submissions
        WHERE status = 'Approved'
        ''')
        return cursor.fetchone()[0]
    
    def has_already_submitted_course(self, employee_id, course_name):
        cursor = self.conn.execute('''
            SELECT status FROM course_submissions
            WHERE employee_id = ? AND LOWER(course_name) = LOWER(?)
            ORDER BY id DESC LIMIT 1
        ''', (employee_id, course_name.strip()))
        
        result = cursor.fetchone()
        return result['status'] if result else None
