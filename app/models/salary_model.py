from app.models.database import Database

class SalaryModel(Database):
    def __init__(self):
        super().__init__()

    def add_salary_record(self, employee_id, salary_month, basic, bonus, deductions, net_salary,
                          currency='NZD', pay_frequency='Monthly', direct_deposit_amount=None):
        with self.conn:
            self.conn.execute('''
                INSERT INTO payroll_records (
                    employee_id, salary_month, basic_salary, bonus, deductions, net_salary,
                    currency, pay_frequency, direct_deposit_amount
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                employee_id, salary_month, basic, bonus, deductions, net_salary,
                currency, pay_frequency, direct_deposit_amount
            ))

    def get_salary_by_month(self, employee_id, month):
        cur = self.conn.execute('''
            SELECT * FROM payroll_records WHERE employee_id = ? AND salary_month = ?
            ''', (employee_id, month))
        # row = cur.fetchone()
        rows = cur.fetchall()
        return [dict(row) for row in rows]
        # return dict(row) if row else None
    
    def get_salary_by_month_payslip(self, employee_id, month):
        cur = self.conn.execute('''
            SELECT * FROM payroll_records WHERE employee_id = ? AND salary_month = ?
            ''', (employee_id, month))
        row = cur.fetchone()
        return dict(row) if row else None

    # def get_all_salary(self, employee_id):
    #     cur = self.conn.execute('''
    #         SELECT * FROM payroll_records WHERE employee_id = ?
    #         ORDER BY salary_month DESC
    #     ''', (employee_id,))
    #     return [dict(row) for row in cur.fetchall()]

    def get_all_salary(self, page=1, per_page=10,employee_id=None):
        offset = (page - 1) * per_page
        cursor = self.conn.execute('''SELECT * FROM payroll_records WHERE employee_id = ? 
                                   ORDER BY salary_month DESC 
                                   LIMIT ? OFFSET ?
                                   ''',(employee_id,per_page, offset)
        )
        return [dict(row) for row in cursor.fetchall()]

    def fetch_salary_records(self, employee_id=None, month=None):
        query = '''
            SELECT p.*, u.name
            FROM payroll_records p
            JOIN users u ON p.employee_id = u.employee_id
            WHERE 1=1
        '''
        params = []

        if employee_id:
            query += ' AND p.employee_id = ?'
            params.append(employee_id)

        if month:
            query += ' AND p.salary_month = ?'
            params.append(month)

        cur = self.conn.execute(query, tuple(params))
        rows = cur.fetchall()
        return [dict(row) for row in rows]


    def get_latest_salary(self, employee_id):
        cur = self.conn.execute('''
            SELECT * FROM payroll_records 
            WHERE employee_id = ? 
            ORDER BY salary_month DESC 
            LIMIT 1
        ''', (employee_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    
    def get_all(self, page=1, per_page=10):
        offset = (page - 1) * per_page
        cursor = self.conn.execute(
            'SELECT * FROM payroll_records ORDER BY generated_at LIMIT ? OFFSET ?',
            (per_page, offset)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_total_count(self):
        cursor = self.conn.execute('SELECT COUNT(*) FROM payroll_records')
        return cursor.fetchone()[0]