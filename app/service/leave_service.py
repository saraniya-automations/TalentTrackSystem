# app/service/leave_service.py

from app.models.leave import Leave
from app.models.user import User
from dateutil.rrule import rrule, DAILY
from dateutil.parser import parse as parse_date
from datetime import datetime

class LeaveService:
    def __init__(self):
        self.leave_model = Leave()
        self.user_model = User()

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

        balance = self.leave_model.get_leave_balance(employee_id, column_name)
        if balance is None:
            return {"error": "Leave balance not found"}, 404
        if leave_days > balance:
            return {"error": f"Insufficient {leave_type} balance"}, 400

        leave_id = self.leave_model.apply_leave(employee_id, leave_type, start_date, end_date, reason)
        self.leave_model.deduct_leave_balance(employee_id, column_name, leave_days)

        return {"message": "Leave applied successfully", "days": leave_days, "leave_id": leave_id}, 201

    def get_leave_balance(self, employee_id):
        return self.leave_model.get_balance_by_employee(employee_id)

    def get_leave_by_id(self, leave_id):
        return self.leave_model.get_by_id(leave_id)

    def update_leave_status(self, leave_id, status, approver_id):
        leave = self.leave_model.get_by_id(leave_id)
        approver = self.user_model.get_by_employee_id(approver_id)

        if not leave:
            return {"error": "Leave request not found"}, 404
        if not approver:
            return {"error": "Approver not found"}, 404
        if approver["role"].lower() != "admin":
            return {"error": "Only admins can approve/reject leaves"}, 403
        if leave["employee_id"] == approver_id:
            return {"error": "Admins cannot approve their own leave requests"}, 403

        applicant = self.user_model.get_by_employee_id(leave["employee_id"])
        if applicant and applicant["role"].lower() == "admin" and approver_id == leave["employee_id"]:
            return {"error": "Admins cannot approve their own leave"}, 403
        if status not in ["Approved", "Rejected"]:
            return {"error": "Invalid status. Must be Approved or Rejected"}, 400

        self.leave_model.update_status(leave_id, status, approver_id)
        return {"message": f"Leave {status.lower()} successfully."}, 200

    def get_pending_leaves(self):
        return self.leave_model.get_pending()
