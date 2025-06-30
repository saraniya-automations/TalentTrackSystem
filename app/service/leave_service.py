from app.models.database import Database
from datetime import datetime
from dateutil.parser import parse as parse_date
from dateutil.rrule import rrule, DAILY
from app.models.user import User  # For checking roles and identities

class LeaveService(Database):
    def __init__(self):
        super().__init__()

    def apply_leave(self, employee_id, leave_type, start_date, end_date, reason):
        leave_days = len(list(rrule(DAILY, dtstart=parse_date(start_date), until=parse_date(end_date))))

        column_map = {
            'annual': 'annual',
            'casual': 'casual',
            'sick': 'sick',
            'maternity': 'maternity'
        }
        column_name = column_map.get(leave_type)
        if not column_name:
            return {"error": f"Unsupported leave type: {leave_type}"}, 400

        cursor = self.conn.execute(f'''
            SELECT {column_name} FROM leave_balances WHERE employee_id = ?
        ''', (employee_id,))
        row = cursor.fetchone()
        if not row:
            return {"error": "Leave balance not found"}, 404

        balance = row[0]
        if leave_days > balance:
            return {"error": f"Insufficient {leave_type} balance"}, 400

        insert_cursor = self.conn.execute('''
            INSERT INTO leaves (employee_id, leave_type, start_date, end_date, reason)
            VALUES (?, ?, ?, ?, ?)
        ''', (employee_id, leave_type, start_date, end_date, reason))

        leave_id = insert_cursor.lastrowid

        self.conn.execute(f'''
            UPDATE leave_balances
            SET {column_name} = {column_name} - ?
            WHERE employee_id = ?
        ''', (leave_days, employee_id))

        self.conn.commit()

        return {"message": "Leave applied successfully", "days": leave_days, "leave_id": leave_id}, 201

    def get_leave_balance(self, employee_id):
        cursor = self.conn.execute('SELECT * FROM leave_balances WHERE employee_id = ?', (employee_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_leave_by_id(self, leave_id):
        cursor = self.conn.execute('SELECT * FROM leaves WHERE id = ?', (leave_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_leave_status(self, leave_id, status, approver_id):
        user_model = User()
        leave = self.get_leave_by_id(leave_id)
        approver = user_model.get_by_employee_id(approver_id)

        if not leave:
            return {"error": "Leave request not found"}, 404
        
        if not approver:
            return {"error": "Approver not found"}, 404

        if approver["role"] != "Admin":
            return {"error": "Only admins can approve/reject leaves"}, 403

        if leave["employee_id"] == approver_id:
            return {"error": "Admins cannot approve their own leave requests"}, 403
        
        # Check if the leave belongs to an Admin — only another Admin can approve it
        applicant = user_model.get_by_employee_id(leave["employee_id"])
        if applicant and applicant["role"] == "admin" and approver_id == leave["employee_id"]:
           return {"error": "Admins cannot approve their own leave"}, 403

        if status not in ["Approved", "Rejected"]:
            return {"error": "Invalid status. Must be Approved or Rejected"}, 400

        self.conn.execute('''
            UPDATE leaves SET status = ?, reviewed_by = ?, reviewed_at = ?
            WHERE id = ?
        ''', (status, approver_id, datetime.now().isoformat(), leave_id))

        self.conn.commit()
        return {"message": f"Leave {status.lower()} successfully."}, 200

    def get_pending_leaves(self):
        cursor = self.conn.execute('''
            SELECT l.*, u.name, u.email, u.role
            FROM leaves l
            JOIN users u ON l.employee_id = u.employee_id
            WHERE l.status IS NULL OR l.status = 'Pending'
            ORDER BY l.start_date ASC
        ''')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
