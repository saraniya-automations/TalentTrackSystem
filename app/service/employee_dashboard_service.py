from app.models.employee_dashboard import EmployeeDashboard

class EmployeeDashboardService:
    def __init__(self):
        self.dashboard_model = EmployeeDashboard()

    def get_employee_summary(self, employee_id):
        summary = self.dashboard_model.get_leave_balance_summary(employee_id)
        return summary
