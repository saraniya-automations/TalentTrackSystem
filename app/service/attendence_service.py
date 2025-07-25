# --- services/attendance_service.py ---
from app.models.attendence import Attendence

attendance_model = Attendence()

def punch_in(employee_id):
    attendance_model.punch_in(employee_id)

def punch_out(employee_id):
    attendance_model.punch_out(employee_id)

def manual_request(employee_id, data):
    attendance_model.manual_request(employee_id, data)

def approve_request(record_id,approver_id):
   return attendance_model.approve_manual(record_id,approver_id)

def reject_request(record_id, reason,approver_id):
    return attendance_model.reject_request(record_id, reason,approver_id)

def get_employee_attendance(employee_id, start_date=None, end_date=None, sort_by="punch_in", order="asc"):
    return attendance_model.get_by_employee(employee_id, start_date, end_date, sort_by, order)


def get_pending_requests(page=1, per_page=10):
    all_attendance = attendance_model.get_pending_requests(page, per_page)
    total = attendance_model.get_pending_count()
    return {
        "items": all_attendance,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
        }


def get_attendance_by_name_and_period(name, start_date, end_date):
    return attendance_model.getAttendenceNameAndPeriod(name, start_date, end_date)

# def get_all_employee_attendance(employee_id):
#     return attendance_model.get_all_employee_records(employee_id)

def get_all_employee_attendance(employee_id, page=1, per_page=10):
    # items, total = attendance_model.get_all_employee_records(employee_id, page, per_page)
    items = attendance_model.get_all_employee_records(employee_id, page, per_page)
    total = attendance_model.get_all_employee_records_of_employee(employee_id)
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1)
    }

