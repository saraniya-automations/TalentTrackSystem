
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
            tables = ['performance_reviews', 'employee_profiles', 'leave_balances',
                  'leaves', 'reset_tokens', 'users']
            for table in tables:
                self.conn.execute(f'DROP TABLE IF EXISTS {table}')

        with self.conn:
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

            self.conn.execute('''CREATE TABLE IF NOT EXISTS reset_tokens (
                user_id INTEGER,
                token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )''')

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
                FOREIGN KEY(employee_id) REFERENCES users(employee_id)
            )''')  

            #Leave Balance Table
            self.conn.execute('''CREATE TABLE IF NOT EXISTS leave_balances (
                employee_id TEXT PRIMARY KEY,
                annual INTEGER DEFAULT 21,
                casual INTEGER DEFAULT 10,
                sick INTEGER DEFAULT 8,
                maternity INTEGER DEFAULT 90,
                FOREIGN KEY(employee_id) REFERENCES users(employee_id)
            )''')

            self.conn.execute('''CREATE TABLE IF NOT EXISTS performance_reviews (
                id INTEGER PRIMARY KEY,
                employee_id TEXT NOT NULL,
                rating INTEGER NOT NULL,
                comments TEXT NOT NULL,
                reviewer_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(employee_id) REFERENCES users(employee_id),
                FOREIGN KEY(reviewer_id) REFERENCES users(employee_id)
            )''')

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


            # # Add manager_id column to users table if not exists
            # cursor = self.conn.execute('PRAGMA table_info(users)')
            # columns = [column[1] for column in cursor.fetchall()]  # Now using cursor
            # if 'manager_id' not in columns:
            #     self.conn.execute('ALTER TABLE users ADD COLUMN manager_id TEXT')