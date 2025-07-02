import sqlite3
from datetime import datetime
from app.models.database import Database

class Performance(Database):
    def __init__(self):
        super().__init__()

    # ✅ Get all mandatory courses for a given department
    def get_courses_by_department(self, department):
        cursor = self.conn.execute('''
            SELECT * FROM courses
            WHERE type = 'Mandatory' AND department = ?
            ORDER BY created_at DESC
        ''', (department,))
        return [dict(row) for row in cursor.fetchall()]

    # ✅ Employee submits course completion with notes
    def submit_course_completion(self, employee_id, course_id, notes):
        cursor = self.conn.execute('''
            INSERT INTO course_submissions (employee_id, course_id, completion_notes)
            VALUES (?, ?, ?)
        ''', (employee_id, course_id, notes))
        self.conn.commit()
        return cursor.lastrowid

    # ✅ Get all course submissions for a specific employee
    def get_my_submissions(self, employee_id):
        cursor = self.conn.execute('''
            SELECT cs.*, c.name AS course_name
            FROM course_submissions cs
            JOIN courses c ON cs.course_id = c.id
            WHERE cs.employee_id = ?
            ORDER BY cs.submitted_at DESC
        ''', (employee_id,))
        return [dict(row) for row in cursor.fetchall()]

    # ✅ Get all submissions that are pending (for admin review)
    def get_pending_submissions(self):
        cursor = self.conn.execute('''
            SELECT cs.*, u.name AS employee_name, u.department, c.name AS course_name
            FROM course_submissions cs
            JOIN users u ON cs.employee_id = u.employee_id
            JOIN courses c ON cs.course_id = c.id
            WHERE cs.status = 'Pending'
            ORDER BY cs.submitted_at ASC
        ''')
        return [dict(row) for row in cursor.fetchall()]

    # ✅ Get one submission by ID (for review purposes)
    def get_submission_by_id(self, submission_id):
        cursor = self.conn.execute('SELECT * FROM course_submissions WHERE id = ?', (submission_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # ✅ Admin updates submission status (Approve/Reject) with reviewer notes
    def update_submission_status(self, submission_id, status, comment, reviewer_id):
        self.conn.execute('''
            UPDATE course_submissions
            SET status = ?, reviewer_comment = ?, reviewed_by = ?, reviewed_at = ?
            WHERE id = ?
        ''', (
            status,
            comment,
            reviewer_id,
            datetime.now().isoformat(),
            submission_id
        ))
        self.conn.commit()
