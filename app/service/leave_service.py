from app.models.database import Database
from datetime import datetime
from dateutil.parser import parse as parse_date
from dateutil.rrule import rrule, DAILY

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

        self.conn.execute('''
            INSERT INTO leaves (employee_id, leave_type, start_date, end_date, reason)
            VALUES (?, ?, ?, ?, ?)
        ''', (employee_id, leave_type, start_date, end_date, reason))

        self.conn.execute(f'''
            UPDATE leave_balances
            SET {column_name} = {column_name} - ?
            WHERE employee_id = ?
        ''', (leave_days, employee_id))

        self.conn.commit()

        return {"message": "Leave applied successfully", "days": leave_days}, 201

    def get_leave_balance(self, employee_id):
        cursor = self.conn.execute('SELECT * FROM leave_balances WHERE employee_id = ?', (employee_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
