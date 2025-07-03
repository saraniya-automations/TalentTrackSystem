import sqlite3
from app.config import Config

class Database:

    def __init__(self):
        self.conn = sqlite3.connect(Config.DATABASE, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_table()

    def create_table(self):
        self.conn.execute("PRAGMA foreign_keys = ON")

        if self.conn.execute("PRAGMA database_list").fetchone()[2] == ":memory:":
            tables = [
                'performance_reviews','users', 'reset_tokens', 'leaves', 'leave_balances', 'employee_profiles',
                'attendance', 'payroll_records', 'courses', 'course_submissions'
            ]
            for table in tables:
                self.conn.execute(f'DROP TABLE IF EXISTS {table}')

        with self.conn:
            # --- USERS TABLE ---
            self.conn.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                employee_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                department TEXT,
                role TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                status TEXT DEFAULT 'Active',
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )''')

            # --- RESET TOKENS TABLE ---
            self.conn.execute('''CREATE TABLE IF NOT EXISTS reset_tokens (
                user_id INTEGER,
                token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )''')

            # --- LEAVES TABLE ---
            self.conn.execute('''CREATE TABLE IF NOT EXISTS leaves (
                id INTEGER PRIMARY KEY,
                employee_id TEXT NOT NULL,
                leave_type TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_by TEXT,
                reviewed_at TIMESTAMP,
                FOREIGN KEY(employee_id) REFERENCES users(employee_id) ON DELETE CASCADE
            )''')

            # --- LEAVE BALANCES ---
            self.conn.execute('''CREATE TABLE IF NOT EXISTS leave_balances (
                employee_id TEXT PRIMARY KEY,
                annual INTEGER DEFAULT 21,
                casual INTEGER DEFAULT 10,
                sick INTEGER DEFAULT 8,
                maternity INTEGER DEFAULT 90,
                FOREIGN KEY(employee_id) REFERENCES users(employee_id) ON DELETE CASCADE
            )''')

            # --- PERFORMANCE REVIEWS ---
            self.conn.execute('''CREATE TABLE IF NOT EXISTS performance_reviews (
                id INTEGER PRIMARY KEY,
                employee_id TEXT NOT NULL,
                rating INTEGER NOT NULL,
                comments TEXT NOT NULL,
                reviewer_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(employee_id) REFERENCES users(employee_id) ON DELETE CASCADE,
                FOREIGN KEY(reviewer_id) REFERENCES users(employee_id) ON DELETE CASCADE

            )''')

            # --- EMPLOYEE PROFILES ---
            self.conn.execute('''CREATE TABLE IF NOT EXISTS employee_profiles (
                id INTEGER PRIMARY KEY,
                user_id TEXT UNIQUE NOT NULL,
                personal_details TEXT,
                contact_details TEXT,
                emergency_contacts TEXT,
                dependents TEXT,
                job_details TEXT,
                salary_details TEXT,
                report_to TEXT,
                qualifications TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(employee_id) ON DELETE CASCADE
            )''')

            # --- ATTENDANCE ---
            self.conn.execute('''CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY,
                employee_id TEXT NOT NULL,
                punch_in TEXT NOT NULL,
                punch_out TEXT,
                date TEXT NOT NULL,
                status TEXT DEFAULT 'On Time',
                is_manual INTEGER DEFAULT 0,
                approval_status TEXT DEFAULT 'Approved',
                rejection_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES users(employee_id) ON DELETE CASCADE
            )''')

            # --- PAYROLL ---
            self.conn.execute('''CREATE TABLE IF NOT EXISTS payroll_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                salary_month TEXT NOT NULL,
                basic_salary REAL NOT NULL,
                bonus REAL DEFAULT 0,
                deductions REAL DEFAULT 0,
                net_salary REAL NOT NULL,
                currency TEXT DEFAULT 'NZD',
                pay_frequency TEXT DEFAULT 'Monthly',
                direct_deposit_amount REAL,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(employee_id) REFERENCES users(employee_id) ON DELETE CASCADE
            )''')

            # --- COURSES TABLE ---
            self.conn.execute('''CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT CHECK(type IN ('Mandatory', 'Optional')) NOT NULL DEFAULT 'Mandatory',
                department TEXT NOT NULL,
                target_role TEXT DEFAULT 'Employee',
                deadline TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # ✅ Seed courses if not already present
            existing = self.conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
            if existing == 0:
                departments = [
                    "Information Technology (IT)", "Operations", "Human Resources (HR)",
                    "Finance and Accounting", "Sales and Marketing"
                ]
                topics = ['Cybersecurity', 'Compliance', 'Onboarding', 'Role-Based Training', 'Ethics & Conduct']
                for dept in departments:
                    for topic in topics:
                        self.conn.execute(
                            "INSERT INTO courses (name, description, type, department) VALUES (?, ?, 'Mandatory', ?)",
                            (f"{dept} - {topic}", f"{topic} course tailored for {dept}", dept)
                        )
                self.conn.commit()

            # --- COURSE SUBMISSIONS TABLE ---
            self.conn.execute('''CREATE TABLE IF NOT EXISTS course_submissions (
                id INTEGER PRIMARY KEY,
                employee_id TEXT NOT NULL,
                course_id INTEGER NOT NULL,
                completion_notes TEXT,
                status TEXT DEFAULT 'Pending',
                reviewer_comment TEXT,
                reviewed_by TEXT,
                reviewed_at TEXT,
                submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(employee_id) REFERENCES users(employee_id) ON DELETE CASCADE,
                FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
            )''')


