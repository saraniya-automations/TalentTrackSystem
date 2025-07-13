# app/seed.py
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash
from app.models.user import User
from app.models.employee_profile import EmployeeProfile
from app.models.salary_model import SalaryModel
from app.models.performance import Performance
from app.models.leave import Leave
from app.models.attendence import Attendence



def seed_database():
    """Seed all database tables with dummy data"""
    print("\n=== Seeding Database ===")
    print("\n=== Checking if seeding is needed ===")
    user_model = User()
    
    existing_users = user_model.get_all()
    if existing_users and len(existing_users) > 3:
        print("ℹ️ Database already seeded. Skipping seeding.\n")
        return  
    
    # 1. Seed Admin (keep your existing logic)
    insert_dummy_admin()
    
    # 2. Seed Regular Employees
    seed_employees()
    
    # 3. Seed Other Data
    seed_leaves()
    seed_attendance()
    # seed_performance_reviews()
    seed_payroll()
    # seed_courses()
    # seed_course_submissions()
    print("=== Database Seeding Complete ===\n")

from app.models.performance import Performance
from werkzeug.security import generate_password_hash

def insert_dummy_admin():
    """Your existing admin seeding function"""
    user_model = User()
    profile_model = EmployeeProfile()

    existing = user_model.get_by_email("admin@example.com")
    if existing:
        print("ℹ️ Dummy admin user already exists.")
        return existing['employee_id']  # Return admin ID for reference

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
    return user['employee_id']

# def seed_employees():
#     """Seed 10 regular employees"""
#     departments = ["IT", "HR"]
#     roles = ["Admin", "Employee"]
    
#     employees = [
#         {
#             "name": f"Employee {i}",
#             "email": f"employee{i}@example.com",
#             "phone": f"021{random.randint(1000000, 9999999)}",
#             "department": random.choice(departments),
#             "role": random.choice(roles),
#             "password": "password123"
#         }
#         for i in range(1, 5)
#     ]
    
#     user_model = User()
#     profile_model = EmployeeProfile()
    
#     for emp in employees:
#         if not user_model.get_by_email(emp["email"]):
#             user_model.add(
#                 name=emp["name"],
#                 email=emp["email"],
#                 phone=emp["phone"],
#                 department=emp["department"],
#                 role=emp["role"],
#                 password_hash=generate_password_hash(emp["password"])
#             )
            
#             user = user_model.get_by_email(emp["email"])
#             profile_model.create_profile(user['employee_id'], {
#                 "personal_details": {
#                     "first_name": emp["name"].split()[0],
#                     "last_name": emp["name"].split()[1],
#                     "dob": f"199{random.randint(0,9)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
#                     "gender": random.choice(["Male", "Female", "Other"])
#                 },
#                 "contact_details": {
#                     "address": f"{random.randint(1,999)} {random.choice(['Main', 'Oak', 'Pine'])} St"
#                 }
#             })
    
#     print(f"✅ Seeded {len(employees)} employees")

def seed_employees():
    """Seed specific number of HR and IT employees"""
    employees = [
        {
            "name": f"HR Employee {i}",
            "email": f"hr_employee{i}@example.com",
            "phone": f"021{random.randint(1000000, 9999999)}",
            "department": "HR",
            "role": "Admin",
            "password": "password123"
        }
        for i in range(1, 1)  # 2 HR employees
    ] + [
        {
            "name": f"IT Employee {i}",
            "email": f"it_employee{i}@example.com",
            "phone": f"022{random.randint(1000000, 9999999)}",
            "department": "IT",
            "role": "Employee",
            "password": "password123"
        }
        for i in range(1, 2)  # 3 IT employees
    ]

    user_model = User()
    profile_model = EmployeeProfile()

    for emp in employees:
        if not user_model.get_by_email(emp["email"]):
            user_model.add(
                name=emp["name"],
                email=emp["email"],
                phone=emp["phone"],
                department=emp["department"],
                role=emp["role"],
                password_hash=generate_password_hash(emp["password"])
            )

            user = user_model.get_by_email(emp["email"])
            profile_model.create_profile(user['employee_id'], {
                "personal_details": {
                    "first_name": emp["name"].split()[0],
                    "last_name": emp["name"].split()[1],
                    "dob": f"199{random.randint(0, 9)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                    "gender": random.choice(["Male", "Female", "Other"])
                },
                "contact_details": {
                    "address": f"{random.randint(1, 999)} {random.choice(['Main', 'Oak', 'Pine'])} St"
                }
            })
             # ✅ Insert leave balance after profile creation
            leave_model = Leave()
            leave_model.insert_leave_balance(user['employee_id'])

    print(f"✅ Seeded {len(employees)} employees (2 HR, 3 IT)")

def seed_leaves():
    """Seed leave records"""
    user_model = User()
    leave_model = Leave()
    
    employees = user_model.get_all()
    leave_types = ["annual", "casual", "sick", "maternity"]
    statuses = ["Approved", "Pending", "Rejected"]
    
    for emp in employees:
        for _ in range(random.randint(0, 3)):  # 0-3 leaves per employee
            start_date = datetime.now() - timedelta(days=random.randint(1, 180))
            end_date = start_date + timedelta(days=random.randint(1, 14))
            
            leave_model.apply_leave(
                employee_id=emp['employee_id'],
                leave_type=random.choice(leave_types),
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                reason=random.choice(["Family event", "Medical", "Vacation", "Personal"]),
                # status=random.choice(statuses)
            )
    
    print(f"✅ Seeded leave records")

def seed_attendance():
    """Seed attendance records for past 30 days"""
    user_model = User()
    attendance_model = Attendence()
    employees = user_model.get_all()

    # Select 20% of employees to be on leave today (at least 1)
    employees_on_leave_today = random.sample(
        employees, 
        k=max(1, int(len(employees) * 0.2))
    )
    approval_toggle = 0
    for emp in employees:
        for day in range(1, 31):  # Last 30 days
            date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
            is_today = (day == 1) # Most recent day is "today"
            
            # Handle employees on leave today
            if is_today and emp in employees_on_leave_today:
                try:
                    # For leave days, set punch_in/punch_out to standard times
                    attendance_model.manual_request(
                        employee_id=emp['employee_id'],
                        data={
                            'punch_in': f"09:00",  # Set default times
                            'punch_out': f"05:00",
                            'date': date,
                            'status': 'Leave',
                            'is_manual': 1,
                            'approval_status': 'Approved',
                            'reason': 'Scheduled leave'
                        }
                    )
                except Exception as e:
                    print(f"Error seeding leave for {emp['employee_id']} on {date}: {str(e)}")
                continue
            
            # Rest of your existing attendance seeding logic...
            # Skip weekends (20% chance)
            if random.random() < 0.2:
                continue
                
            # Create punch_in datetime
            punch_in_dt = datetime.strptime(date, '%Y-%m-%d').replace(
                hour=random.randint(8, 10),
                minute=random.randint(0, 59)
            )
            punch_in = punch_in_dt.isoformat()
            
            # Calculate punch_out by adding hours to punch_in datetime
            punch_out_dt = punch_in_dt + timedelta(
                hours=random.randint(6, 9),
                minutes=random.randint(0, 59)
            )
            punch_out = punch_out_dt.isoformat()
            
            status = random.choices(
                ["On Time", "Late"],
                weights=[0.7, 0.2]
            )[0]
            # approval_status = "Approved" if approval_toggle % 2 == 0 else "Pending"
            approval_status = random.choices(
                ["Approved", "Pending", "Rejected"],
                weights=[0.7, 0.2, 0.1]
            )[0]

            approval_toggle += 1
            attendance_model.manual_request(
                employee_id=emp['employee_id'],
                data={
                    'punch_in': f'09:30',
                    'punch_out': f'17:30',
                    'date': date,
                    'status': status,
                    'reason': None,
                    'is_manual': 1,
                    # 'approval_status': 'Approved' if random.random() < 0.5 else 'Pending'
                    'approval_status': approval_status
                }
            )
    
    print(f"✅ Seeded attendance records with:")
    print(f"- {len(employees_on_leave_today)} employees on leave today")
    print("- Random approval status for manual requests")

def seed_payroll():
    """Seed payroll records using your SalaryModel"""
    user_model = User()
    salary_model = SalaryModel()
    employees = user_model.get_all()
    
    print("\nSeeding payroll records...")
    
    for emp in employees:
        # Generate base salary based on role
        # if emp['role'] == 'Admin':
        base_range = (80000, 120000)
        # elif emp['role'] == 'Manager':
        #     base_range = (60000, 90000)
        # else:
        #     base_range = (30000, 60000)
        
        base_salary = random.randint(*base_range)
        
        # Generate records for past 12 months with progression
        for month in range(1, 13):
            salary_month = (datetime.now() - timedelta(days=30*month)).strftime('%Y-%m')
            
            # Salary components with realistic variations
            basic = round(base_salary * 0.5, 2)
            
            # Bonus logic - higher chance and amount for managers/admin
            # if emp['role'] in ['Admin', 'Manager']:
            bonus = round(random.uniform(0.1, 0.25) * base_salary, 2) if random.random() > 0.2 else 0
            # else:
            #     bonus = round(random.uniform(0, 0.15) * base_salary, 2) if random.random() > 0.3 else 0
            
            # Deductions - progressive based on salary
            deductions = round(random.uniform(0.05, 0.15) * base_salary, 2)
            
            # Small salary increment over time
            if month % 3 == 0:  # Every quarter
                base_salary *= 1 + random.uniform(0.01, 0.03)
            
            net_salary = round(basic + bonus - deductions, 2)
            
            try:
                salary_model.add_salary_record(
                    employee_id=emp['employee_id'],
                    salary_month=salary_month,
                    basic=basic,
                    bonus=bonus,
                    deductions=deductions,
                    net_salary=net_salary,
                    direct_deposit_amount=net_salary  # Assuming full deposit
                )
                
                # Occasionally add a second payment in same month (bonus, adjustment)
                if random.random() < 0.1:  # 10% chance
                    adjustment = round(random.uniform(-0.1, 0.2) * base_salary, 2)
                    salary_model.add_salary_record(
                        employee_id=emp['employee_id'],
                        salary_month=salary_month,
                        basic=0,
                        bonus=adjustment,
                        deductions=0,
                        net_salary=adjustment,
                        currency='NZD',
                        pay_frequency='Adjustment'
                    )
                    
            except Exception as e:
                print(f"Error seeding payroll for {emp['employee_id']} ({emp['name']}) for {salary_month}: {str(e)}")
    
    print(f"✅ Seeded payroll records for {len(employees)} employees")
    print(f"- 12 months of records per employee")
    print(f"- Role-based salary ranges")
    print(f"- Progressive salary increases")
    print(f"- Occasional adjustment payments")

# Add similar functions for performance_reviews, courses, etc.

if __name__ == "__main__":
    seed_database()

def insert_default_courses():
    p = Performance()

    # ✅ Check if courses table already has entries
    result = p.conn.execute('SELECT COUNT(*) FROM courses').fetchone()
    course_count = result[0] if result else 0

    if course_count == 0:
        p.seed_default_courses()
