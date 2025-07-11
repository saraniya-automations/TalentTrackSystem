from app.models.database import Database

class EmployeeDashboard(Database):
    def __init__(self):
        super().__init__()

    def get_leave_balance_summary(self, employee_id):
        balance_cursor = self.conn.execute('''
            SELECT * FROM leave_balances WHERE employee_id = ?
        ''', (employee_id,))
        balance_row = balance_cursor.fetchone()
        if not balance_row:
            return []

        balance_dict = dict(balance_row)

        used_cursor = self.conn.execute('''
            SELECT leave_type, 
                SUM(julianday(end_date) - julianday(start_date) + 1) AS used
            FROM leaves
            WHERE employee_id = ? AND status = 'Approved'
            GROUP BY leave_type

        ''', (employee_id,))
        used_data = {row['leave_type'].capitalize(): row['used'] for row in used_cursor.fetchall()}

        leave_types = {
            'Annual': balance_dict.get('annual', 0),
            'Sick': balance_dict.get('sick', 0),
            'Casual': balance_dict.get('casual', 0),  # Assuming casual = emergency
        }

        summary = []
        for leave_type, remaining in leave_types.items():
            used = used_data.get(leave_type, 0)
            total = remaining + used
            summary.append({
                'type': leave_type,
                'total': total,
                'used': used
            })

        return summary
