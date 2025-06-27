# app/service/employee_profile_service.py
from app.models.employee_profile import EmployeeProfile

profile_model = EmployeeProfile()

def create_profile(user_id, data):
    profile_model.create_profile(user_id, data)

def get_profile_by_employee_id(employee_id):
    return profile_model.get_by_employee_id(employee_id)

def update_profile(user_id, data):
    profile_model.update_profile(user_id, data)

def get_all_profiles(limit=50, offset=0,key=''):
    return profile_model.get_all(limit, offset,key)
