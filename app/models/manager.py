from app.models.database import Database
from datetime import datetime
from dateutil.parser import parse
from dateutil.rrule import rrule, DAILY

class Manager(Database):
    def __init__(self):
        super().__init__()

    def update_leave_status(self, leave_id, status):
        if status not in ['Approved', 'Rejected']:
            raise ValueError("Invalid status")

        #Fetch leave request
        leave = self.conn.execute(
            'SELECT * FROM leaves WHERE id = ?', (leave_id,)
        ).fetchone()

        if not leave:
            return {'error': 'Leave not found'}

        #If status is Approved, calculate duration and deduct balance
        if status == 'Approved':
            start = parse(leave['start_date'])
            end = parse(leave['end_date'])
            leave_days = len(list(rrule(DAILY, dtstart=start, until=end)))

            #Leave type to column mapping
            column_map = {
                'Annual Leaves': 'annual_leaves',
                'Casual Leaves': 'casual_leaves',
                'Sick Leaves': 'sick_leaves',
                'Maternity Leave': 'maternity_leave'
            }
            column_name = column_map.get(leave['leave_type'])
            if not column_name:
                return {"error": f"Unsupported leave type: {leave['leave_type']}"}

            #Deduct from leave balance
            self.conn.execute(f'''
                UPDATE leave_balances
                SET {column_name} = {column_name} - ?
                WHERE employee_id = ?
            ''', (leave_days, leave['employee_id']))

        #Update leave status
        self.conn.execute('''
            UPDATE leaves
            SET status = ?, updated_at = ?
            WHERE id = ?
        ''', (status, datetime.now().isoformat(), leave_id))

        self.conn.commit()
        return {"message": f"Leave {status.lower()} successfully"}

    def get_pending_leaves(self, manager_id):
        #Extend this to filter by manager if needed
        cursor = self.conn.execute('''
            SELECT * FROM leaves
            WHERE status = 'Pending'
        ''')
        return [dict(row) for row in cursor.fetchall()]

    def get_employees_under_manager(self, manager_id):
        cursor = self.conn.execute('''
            SELECT * FROM users
            WHERE report_to = ?
        ''', (manager_id,))
        return [dict(row) for row in cursor.fetchall()]

    def add_performance_review(self, data):
        self.conn.execute('''
            INSERT INTO performance_reviews (
                employee_id, rating, comments, reviewer_id
            ) VALUES (?, ?, ?, ?)
        ''', (
            data['employee_id'],
            data['rating'],
            data['comments'],
            data['reviewer_id']
        ))
        self.conn.commit()
        return {"message": "Review submitted"}

    def get_performance_reviews(self, employee_id):
        cursor = self.conn.execute('''
            SELECT * FROM performance_reviews
            WHERE employee_id = ?
        ''', (employee_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_leave_history(self, employee_id):
        cursor = self.conn.execute('''
            SELECT * FROM leaves
            WHERE employee_id = ?
        ''', (employee_id,))
        return [dict(row) for row in cursor.fetchall()]
