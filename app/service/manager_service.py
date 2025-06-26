from app.models.manager import Manager

manager_model = Manager()

def get_pending_leaves(manager_id):
    return manager_model.get_pending_leaves(manager_id)

def update_leave_status(leave_id, status):
    return manager_model.update_leave_status(leave_id, status)

def add_performance_review(data):
    return manager_model.add_performance_review(data)

def get_employees_under_manager(manager_id):
    return manager_model.get_employees_under_manager(manager_id)

def get_performance_reviews(employee_id):
    return manager_model.get_performance_reviews(employee_id)

def get_leave_history(employee_id):
    return manager_model.get_leave_history(employee_id)

def update_leave_status(leave_id, status):
    return manager_model.update_leave_status(leave_id, status) #For leave feature