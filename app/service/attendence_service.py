# --- services/attendance_service.py ---
from app.models.attendence import Attendence

attendance_model = Attendence()

def punch_in(employee_id):
    attendance_model.punch_in(employee_id)

def punch_out(employee_id):
    attendance_model.punch_out(employee_id)

def manual_request(employee_id, data):
    attendance_model.manual_request(employee_id, data)

def approve_request(record_id):
    attendance_model.approve_manual(record_id)

def reject_request(record_id, reason):
    attendance_model.reject_request(record_id, reason)

def get_employee_attendance(employee_id, start_date=None, end_date=None, sort_by="punch_in", order="asc"):
    return attendance_model.get_by_employee(employee_id, start_date, end_date, sort_by, order)


def get_pending_requests():
    return attendance_model.get_pending_requests()

def get_attendance_by_name_and_period(name, start_date, end_date):
    return attendance_model.getAttendenceNameAndPeriod(name, start_date, end_date)