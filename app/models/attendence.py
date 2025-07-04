from app.models.database import Database
from datetime import datetime

class Attendence(Database):
    def __init__(self):
        super().__init__()
    
    def punch_in(self, employee_id):
        date_str = datetime.now().strftime('%Y-%m-%d')
        now = datetime.now().isoformat()
        with self.conn:
            self.conn.execute('''
                INSERT INTO attendance (employee_id, punch_in, date)
                VALUES (?, ?, ?)
            ''', (employee_id, now, date_str))

    def punch_out(self, employee_id):
        date_str = datetime.now().strftime('%Y-%m-%d')
        now = datetime.now().isoformat()
        with self.conn:
            self.conn.execute('''
                UPDATE attendance SET punch_out = ?
                WHERE employee_id = ? AND date = ?
            ''', (now, employee_id, date_str))

    def manual_request(self, employee_id, data):
        with self.conn:
            self.conn.execute('''
                INSERT INTO attendance (employee_id, punch_in, punch_out, date, status, is_manual, approval_status,rejection_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                employee_id,
                data['punch_in'],
                data['punch_out'],
                data['date'],
                data.get('status', 'Manual Edit'),
                1,
                'Pending',
                data.get('reason', None)
            ))

    def approve_manual(self, record_id):
        with self.conn:
            self.conn.execute('''
                UPDATE attendance SET approval_status = 'Approved'
                WHERE id = ?
            ''', (record_id,))

    # def get_by_employee(self, employee_id):
    #     cur = self.conn.execute('''SELECT * FROM attendance WHERE employee_id = ?''', (employee_id,))
    #     return [dict(row) for row in cur.fetchall()]

    def get_pending_requests(self):
        cur = self.conn.execute('''SELECT * FROM attendance WHERE is_manual = 1 AND approval_status = 'Pending' ''')
        return [dict(row) for row in cur.fetchall()]
    
    def get_by_employee(self, employee_id, start_date=None, end_date=None, sort_by="punch_in", order="asc"):
        query = "SELECT * FROM attendance WHERE employee_id = ?"
        params = [employee_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        if sort_by not in ["punch_in", "punch_out", "date"]:
            sort_by = "punch_in"
        if order.lower() not in ["asc", "desc"]:
            order = "asc"

        query += f" ORDER BY {sort_by} {order.upper()}"

        cursor = self.conn.execute(query, tuple(params))
        return [dict(row) for row in cursor.fetchall()]
    
    def reject_request(self, record_id, reason):
        query = """
            UPDATE attendance
            SET status = 'Rejected',
                rejection_reason = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status = 'Pending'
        """
        self.conn.execute(query, (reason, record_id))
        self.conn.commit()

    def getAttendenceNameAndPeriod(self, name, start_date, end_date):
        query = """
            SELECT a.*, u.name 
            FROM 
            attendance a JOIN users u 
            ON 
            a.employee_id = u.employee_id
            WHERE u.name LIKE ? AND a.date BETWEEN ? AND ?
        """
        params = [f"%{name}%", start_date, end_date]
        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]



    

    

   