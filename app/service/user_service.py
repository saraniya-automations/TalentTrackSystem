from werkzeug.security import generate_password_hash
from app.models.user import User
from app.utils.logger import logger
import sqlite3
from app.models.database import Database  # ✅ required for leave balance
from app.models.performance import Performance
performance_model = Performance()

user_model = User()

def create_user(data):
    try:
        if user_model.get_by_email(data['email']):
            return {"error":"User with this email already exists."}
        
        password_hash = generate_password_hash(data['password'])
        status = data.get('status', 'Active')
        employee = user_model.add(
            name=data['name'],
            email=data['email'].lower() ,
            phone=data['phone'],
            department=data['department'],
            role=data['role'],
            password_hash=password_hash,
            status=status
        )

        # ✅ After creating user, initialize leave balances
        db = Database()
        db.conn.execute('INSERT INTO leave_balances (employee_id) VALUES (?)', (employee[1],))
        db.conn.commit()

        # Automatically assign department-specific course
        performance_model.assign_course_to_user_if_exists(employee[1], data['department'])
        
        # return {"employee": employee}, 201
        return employee, 201
    except sqlite3.IntegrityError as e:
        logger.error(f"Create user failed due to IntegrityError: {e}")
        return {"error": "Email already exists"}, 400 
    except Exception as e:
        logger.error(f"Create user failed: {e}")
        raise


# In services/user_service.py
def get_users(page=1, per_page=10):
    users = user_model.get_all(page, per_page)
    total = user_model.get_total_count()
    return {
        'items': users,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    }

def search_users(name):
    return user_model.search(name)

def update_user(employee_id, data):
    user_model.update(
        employee_id,
        name=data['name'],
        email=data['email'],
        phone=data['phone'],
        department=data['department'],
        role=data['role'],
        # password_hash=generate_password_hash(data['password']) if 'password' in data else None,
        status=data.get('status')
    )


def inactive_user(employee_id):
    user_model.inactive(employee_id)

def hard_delete_user(employee_id):
    user_model.hard_delete_by_employee_id(employee_id)

def get_by_email(email):
    return user_model.get_by_email(email)

def get_by_employee_id(employee_id):
    return user_model.get_by_employee_id(employee_id)

def store_reset_token(employee_id, token):
    user_model.save_reset_token(employee_id, token)

def get_user_id_by_token(token):
    return user_model.get_user_id_by_token(token)

def update_password(employee_id, new_password):
    password_hash = generate_password_hash(new_password)
    user_model.update_password(employee_id, password_hash)

