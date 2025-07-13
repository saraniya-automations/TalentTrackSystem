# Kiwi HRM System (Backend)

## 📝 Project Overview
Kiwi HRM is a Human Resource Management System developed using Flask, SQLite, and JWT. The system includes core HR functionalities such as user management, employee profiles, leave management, salary & payroll processing, performance reviews, and attendance tracking. The application ensures secure access for both admins and employees with role-based permissions.



## 🛠️ Tech Stack
- **Backend**: Python (Flask)
- **Database**: SQLite
- **Authentication**: JWT (JSON Web Tokens)
- **Testing Tools**: pytest, unittest, Postman, curl

## 🚀 Deployment Instructions

### Prerequisites:
- Python 3.8+
- pip (Python package manager)

### Steps:
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/kiwi-hrm.git](https://github.com/saraniya-automations/TalentTrackSystem.git
   cd kiwi-hrm
2. Install Dependencies:
   ```bash
   pip install -r requirements.txt
   
3. Run the application:
   ```bash
   python run.py
4. Access the application at:
   ```bash
   http://localhost:5000

### Folder Structure
```
TalentTrackSystem/
│
├── app/                             
│   ├── models/                      
│   │   ├── admin_dashboard.py
│   │   ├── attendance.py
│   │   ├── database.py
│   │   ├── employee_dashboard.py
│   │   ├── employee_profile
│   │   ├── leave.py
│   │   ├── performance.py
│   │   ├── salary.py
│   │   ├── user.py
│   │
│   ├── routes/
│   │   ├── admin_dashboard_routes.py
│   │   ├── employee_dashboard_routes.py    
│   │   ├── attendance_routes.py
│   │   ├── employee_profile_routes.py
│   │   ├── leave_routes.py
│   │   ├── performance_routes.py
│   │   ├── salary_routes.py
│   │   └── user_routes.py
│   │
│   ├── schemas/                     
│   │   ├── attendance_schema.py
│   │   ├── leave_schema.py
│   │   ├── employee_profile_schema.py
│   │   ├── performance_schema.py
│   │   ├── salary_schema.py
│   │   └── user_schema.py
│   │
│   ├── services/
│   │   ├── admin_dashboard_service.py
│   │   ├── attendance_service.py
│   │   ├── employee_dashboard_service.py
│   │   ├── employee_profile.py
│   │   ├── leave_service.py
│   │   ├── performance_service.py
│   │   ├── salary_service.py
│   │   └── user_service.py
│
├── utils/
│   |   ├── auth.py
│   │   ├── logger.py
│   │   ├── seed.py
│   │   └── token_util.py
│
├── config.py
├── __init__.py
├── run.py                           
├── requirements.txt
├── employees.db
└── README.md                        

```

### 🔐  Admin Login Credentials:
- Email: admin@example.com
- Password: admin

### 🧪 Sample Data
When the program lauch for the first time seed.py will get automatically get triggered and mock data will be created

### Authors
Authors: M. Saraniya Sathisvari, Bhagya Hettiarachchi









