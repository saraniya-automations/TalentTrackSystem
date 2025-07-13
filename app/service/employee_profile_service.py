# app/service/employee_profile_service.py
from app.models.employee_profile import EmployeeProfile

profile_model = EmployeeProfile()

def create_profile(user_id, data):
    profile_model.create_profile(user_id, data)

def get_profile_by_employee_id(employee_id):
    return profile_model.get_by_employee_id(employee_id)

def update_profile(user_id, data):
    profile_model.update_profile(user_id, data)

def get_all_profiles(limit=50, offset=1,key=''):
    profiles = profile_model.get_all(limit, offset,key)
    total = profile_model.get_total_profile_count()
    return {
        'items': profiles,
        'total': total,
        'page': offset // limit + 1,
        'per_page': limit,
        'total_pages': (total + limit - 1) // limit
    }
    # return profile_model.get_all(limit, offset,key)
