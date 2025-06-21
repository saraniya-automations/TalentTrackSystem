from app.models.user import User
from app.utils.logger import logger

user_model = User()

def create_user(data):
    try:
        return user_model.add(data['name'], data['email'], data['role'])
    except Exception as e:
        logger.error(f"Create user failed: {e}")
        raise

def get_users():
    return user_model.get_all()

def search_users(name):
    return user_model.search(name)

def update_user(user_id, data):
    user_model.update(user_id, data['name'], data['email'], data['role'])

def delete_user(user_id):
    user_model.delete(user_id)
