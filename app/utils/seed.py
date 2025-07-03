# app/seed.py

from app.models.user import User
from app.models.employee_profile import EmployeeProfile
from werkzeug.security import generate_password_hash

def insert_dummy_admin():
    user_model = User()
    profile_model = EmployeeProfile()

    existing = user_model.get_by_email("admin@example.com")
    if existing:
        print("ℹ️ Dummy admin user already exists.")
        return

    user_model.add(
        name="Test Admin",
        email="admin@example.com",
        phone="9999999999",
        department="HR",
        role="Admin",
        password_hash=generate_password_hash("admin")
    )

    profile_data = {
        "personal_details": {
            "first_name": "Jane",
            "middle_name": "K",
            "last_name": "Doe",
            "dob": "1992-05-10",
            "gender": "Female"
        },
        "contact_details": {
            "email": "admin@example.com",
            "phone": "2223334444",
            "address": "456 Main Street"
        },
        "emergency_contacts": [],
        "dependents": [],
        "job_details": {},
        "salary_details": {},
        "report_to": {},
        "qualifications": []
    }

    user = user_model.get_by_email("admin@example.com")
    profile_model.create_profile(user['employee_id'], profile_data)

    print("✅ Dummy admin user created successfully.")
