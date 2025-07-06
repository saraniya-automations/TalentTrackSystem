# app/models/leave.py

from app.models.database import Database
from datetime import datetime

class Leave(Database):
    def __init__(self):
        super().__init__()

    def apply_leave(self, employee_id, leave_type, start_date, end_date, reason):
        cursor = self.conn.execute('''
            INSERT INTO leaves (employee_id, leave_type, start_date, end_date, reason)
            VALUES (?, ?, ?, ?, ?)
        ''', (employee_id, leave_type, start_date, end_date, reason))
        self.conn.commit()
        return cursor.lastrowid

    def get_by_id(self, leave_id):
        cursor = self.conn.execute('SELECT * FROM leaves WHERE id = ?', (leave_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_status(self, leave_id, status, reviewed_by):
        self.conn.execute('''
            UPDATE leaves
            SET status = ?, reviewed_by = ?, reviewed_at = ?
            WHERE id = ?
        ''', (status, reviewed_by, datetime.now().isoformat(), leave_id))
        self.conn.commit()

    def get_pending(self):
        cursor = self.conn.execute('''
            SELECT l.*, u.name, u.email, u.role
            FROM leaves l
            JOIN users u ON l.employee_id = u.employee_id
            WHERE l.status IS NULL OR l.status = 'Pending'
            ORDER BY l.start_date ASC
        ''')
        return [dict(row) for row in cursor.fetchall()]

    def get_leave_balance(self, employee_id, leave_type):
        cursor = self.conn.execute(f'''
            SELECT {leave_type} FROM leave_balances WHERE employee_id = ?
        ''', (employee_id,))
        row = cursor.fetchone()
        return row[0] if row else None

    def deduct_leave_balance(self, employee_id, leave_type, days):
        self.conn.execute(f'''
            UPDATE leave_balances
            SET {leave_type} = {leave_type} - ?
            WHERE employee_id = ?
        ''', (days, employee_id))
        self.conn.commit()

    def get_balance_by_employee(self, employee_id):
        cursor = self.conn.execute(
            'SELECT * FROM leave_balances WHERE employee_id = ?',
            (employee_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_leaves_by_employee_name_and_date(self, name, start_date, end_date):
        cursor = self.conn.execute('''
            SELECT l.leave_type, l.start_date, l.end_date, l.reason, u.name
            FROM leaves l
            JOIN users u ON l.employee_id = u.employee_id
            WHERE u.name LIKE ?
            AND l.start_date >= ? AND l.end_date <= ?
            ORDER BY l.start_date ASC
        ''', (f'%{name}%', start_date, end_date))
        return [dict(row) for row in cursor.fetchall()]

