from app.models.salary_model import SalaryModel

class SalaryService:
    def __init__(self):
        self.salary_model = SalaryModel()

    def add_salary_record(self, data):
        # Calculate net salary if not provided
        net_salary = data['basic_salary'] + data.get('bonus', 0) - data.get('deductions', 0)
        direct_deposit_amount = data.get('direct_deposit_amount', net_salary)

        self.salary_model.add_salary_record(
            employee_id=data['employee_id'],
            salary_month=data['salary_month'],
            basic=data['basic_salary'],
            bonus=data.get('bonus', 0),
            deductions=data.get('deductions', 0),
            net_salary=net_salary,
            currency=data.get('currency', 'NZD'),
            pay_frequency=data.get('pay_frequency', 'Monthly'),
            direct_deposit_amount=direct_deposit_amount
        )

    def get_salary_by_month(self, employee_id, month,page,per_page):
        # return self.salary_model.get_salary_by_month(employee_id, month)
        salaries = self.salary_model.get_salary_by_month(employee_id, month,page, per_page)
        if not salaries:
            return []   
        return {
            'items': salaries,
            'total': len(salaries),
            'page': page,
            'per_page': per_page,
        }
    
    def get_salary_by_month_payslip(self, employee_id, month):
        return self.salary_model.get_salary_by_month_payslip(employee_id, month)

    def get_all_salary(self, employee_id,page=1, per_page=10):
        # return self.salary_model.get_all_salary(employee_id)
        users = self.salary_model.get_all_salary(page, per_page,employee_id)
        total = self.salary_model.get_total_count()
        return {    
            'items': users,
            'total': total,
            'page': page,
            'per_page': per_page,
        }
       

    def get_filtered_salary_records(self, employee_id=None, month=None):
        return self.salary_model.fetch_salary_records(employee_id, month)
    

    def get_latest_salary(self, employee_id):
        return self.salary_model.get_latest_salary(employee_id)
    
    def get_all_employees_salary_records(self, page=1, per_page=10):
        salaries = self.salary_model.get_all(page, per_page)
        total = self.salary_model.get_total_count()
        return {
        'items': salaries,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    }