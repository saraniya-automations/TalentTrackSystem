from app.models.database import Database
from typing import List, Dict

class AdminDashboard(Database):
    def __init__(self):
        super().__init__()

    # Returns active users
    def get_total_active_employees(self):
        cur = self.conn.execute('SELECT COUNT(*) as total FROM users WHERE status = "Active"')
        return cur.fetchone()['total']

    def get_pending_attendance_requests(self):
        cur = self.conn.execute('SELECT COUNT(*) as total FROM attendance WHERE is_manual = 1 AND approval_status = "Pending"')
        return cur.fetchone()['total']

    def get_approved_attendance_requests(self):
        cur = self.conn.execute('SELECT COUNT(*) as total FROM attendance WHERE is_manual = 1 AND approval_status = "Approved"')
        return cur.fetchone()['total']
    
    def get_employees_on_leave_today(self):
        cur = self.conn.execute('''
            SELECT COUNT(*) as total FROM attendance 
            WHERE status = 'Leave' AND date = DATE('now')
        ''')
        return cur.fetchone()['total']
    
    def get_employees_present_today(self):
        """Get count of employees who are present today (not on leave)"""
        cur = self.conn.execute('''
            SELECT COUNT(*) as present 
            FROM employees e
            WHERE NOT EXISTS (
                SELECT 1 FROM attendance 
                WHERE employee_id = e.id 
                AND status = 'Leave' 
                AND date = DATE('now')
            )
        ''')
        return cur.fetchone()['present']
    
    def get_weekly_attendance_for_chart(self, department: str = None) -> List[Dict[str, any]]:
        """
        Get weekly attendance data formatted for frontend charts
        Args:
            department: Optional department filter
        Returns:
            List of dictionaries with:
            - name: Day name (Mon-Sun)
            - present: Count of present employees
            - absent: Count of absent/leave employees
        """
        # Base query - gets last 7 days including today
        query = """
            SELECT 
                strftime('%w', a.date) as day_num,
                strftime('%Y-%m-%d', a.date) as date,
                COUNT(CASE WHEN a.status = 'Present' THEN 1 END) as present,
                COUNT(CASE WHEN a.status IN ('Absent', 'Leave') THEN 1 END) as absent
            FROM attendance a
            JOIN users u ON a.employee_id = u.employee_id
            WHERE a.date >= date('now', '-6 days')
            AND a.date <= date('now')
            AND u.status = 'Active'
        """
        
        params = []
        if department:
            query += " AND u.department = ?"
            params.append(department)
        
        query += " GROUP BY a.date ORDER BY a.date"
        
        cur = self.conn.execute(query, params)
        db_results = [dict(row) for row in cur.fetchall()]
        
        # Day mapping (SQLite %w returns 0=Sunday to 6=Saturday)
        day_map = {
            '0': {'name': 'Sun', 'order': 6},
            '1': {'name': 'Mon', 'order': 0},
            '2': {'name': 'Tue', 'order': 1},
            '3': {'name': 'Wed', 'order': 2},
            '4': {'name': 'Thu', 'order': 3},
            '5': {'name': 'Fri', 'order': 4},
            '6': {'name': 'Sat', 'order': 5}
        }
        
        # Process results
        chart_data = []
        for result in db_results:
            day_info = day_map[result['day_num']]
            chart_data.append({
                'name': day_info['name'],
                'present': result['present'],
                'absent': result['absent'],
                'date': result['date'],
                '_order': day_info['order']  # For sorting
            })
        
        # Ensure all 7 days are present (fill missing days with zeros)
        full_week = []
        for day_num in ['1', '2', '3', '4', '5', '6', '0']:  # Mon-Sun order
            day_info = day_map[day_num]
            existing_day = next((d for d in chart_data if d['name'] == day_info['name']), None)
            
            if existing_day:
                full_week.append(existing_day)
            else:
                # Create empty day record
                full_week.append({
                    'name': day_info['name'],
                    'present': 0,
                    'absent': 0,
                    'date': '',  # No date for missing days
                    '_order': day_info['order']
                })
        
        # Sort by weekday order (Mon-Sun)
        full_week.sort(key=lambda x: x['_order'])
        
        # Remove temporary sorting key
        for day in full_week:
            day.pop('_order', None)
        
        return full_week
    
    def get_monthly_employee_counts(self) -> Dict[str, int]:
        """
        Get raw employee counts by month (Model Layer)
        Returns:
            {'2023-01': 5, '2023-02': 8, ...}
        """
        query = """
            SELECT 
                strftime('%Y-%m', created_at) as month,
                COUNT(*) as count
            FROM users
            WHERE role != 'Admin'
            AND status = 'Active'
            GROUP BY month
        """
        cur = self.conn.execute(query)
        return {row['month']: row['count'] for row in cur.fetchall()}
    
    def get_employee_growth_data(self) -> List[Dict[str, any]]:
        """
        Get raw employee growth data sorted by creation date
        Returns:
            List of dictionaries with:
            - date: Employee creation date (YYYY-MM-DD)
            - employee_id: Unique employee identifier
        """
        cur = self.conn.execute('''
            SELECT 
                strftime('%Y-%m-%d', created_at) as date,
                employee_id
            FROM users 
            WHERE role != 'Admin' 
            AND status = 'Active'
            ORDER BY created_at ASC
        ''')
        return [dict(row) for row in cur.fetchall()]
    
    def get_employee_counts_by_department(self) -> Dict[str, int]:
        """
        Get employee counts grouped by department
        Returns:
            Dictionary with department names as keys and employee counts as values
            Example: {'HR': 5, 'IT': 12, 'Finance': 8}
        """
        cur = self.conn.execute('''
            SELECT department, COUNT(*) as count 
            FROM users 
            WHERE status = 'Active' 
            AND role != 'Admin'
            GROUP BY department
        ''')
        return {row['department']: row['count'] for row in cur.fetchall()}