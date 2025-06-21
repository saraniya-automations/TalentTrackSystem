# app/config.py
import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE = os.path.join(BASE_DIR, '..', 'employees.db')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
