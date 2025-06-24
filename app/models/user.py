import sqlite3
from app.config import Config
from datetime import datetime

class User:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DATABASE, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
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
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS reset_tokens (
                    user_id INTEGER,
                    token TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')

    def generate_employee_id(self):
        cursor = self.conn.execute('SELECT MAX(id) FROM users')
        row = cursor.fetchone()
        next_id = (row[0] or 0) + 1
        return f"EMP{next_id:04d}"

    def add(self, name, email, phone, department, role, password_hash, status='Active'):
        employee_id = self.generate_employee_id()
        with self.conn:
            cursor = self.conn.execute('''
                INSERT INTO users (
                    employee_id, name, email, phone, department,
                    role, password_hash, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (employee_id, name, email, phone, department, role, password_hash, status))
        return cursor.lastrowid, employee_id

    def get_all(self):
        cursor = self.conn.execute('SELECT * FROM users')
        return [dict(row) for row in cursor.fetchall()]

    def search(self, name):
        search_pattern = f"%{name}%"
        cursor = self.conn.execute('SELECT * FROM users WHERE name LIKE ?', (search_pattern,))
        return [dict(row) for row in cursor.fetchall()]

    def get_by_field(self, field, value):
        cursor = self.conn.execute(f'SELECT * FROM users WHERE {field} = ?', (value,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_by_email(self, email):
        return self.get_by_field('email', email)

    def get_by_id(self, user_id):
        return self.get_by_field('id', user_id)
    
    def get_by_employee_id(self, employee_id):
        return self.get_by_field('employee_id', employee_id)

    def update(self, user_id, name, email, phone, department, role, password_hash=None, status=None):
        fields = []
        values = []

        for field, value in [('name', name), ('email', email), ('phone', phone),
                             ('department', department), ('role', role)]:
            fields.append(f"{field} = ?")
            values.append(value)

        if password_hash:
            fields.append("password_hash = ?")
            values.append(password_hash)
        if status:
            fields.append("status = ?")
            values.append(status)

        fields.append("updated_at = ?")
        values.extend([datetime.now().isoformat(), user_id])
        with self.conn:
            self.conn.execute(
                f'''UPDATE users SET {', '.join(fields)} WHERE id = ?''',
                tuple(values)
            )

    def delete(self, employee_id):
        with self.conn:
            self.conn.execute(
            'UPDATE users SET status = ?, updated_at = ? WHERE employee_id = ?',
            ('Inactive', datetime.now().isoformat(), employee_id)
        )

    # ✅ These were outside the class — moved inside
    def save_reset_token(self, user_id, token):
        with self.conn:
            self.conn.execute(
                'INSERT INTO reset_tokens (user_id, token) VALUES (?, ?)',
                (user_id, token)
            )

    def get_user_id_by_token(self, token):
        cursor = self.conn.execute(
            'SELECT user_id FROM reset_tokens WHERE token = ?',
            (token,)
        )
        row = cursor.fetchone()
        return row['user_id'] if row else None

    def update_password(self, user_id, password_hash):
        with self.conn:
            self.conn.execute(
                'UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?',
                (password_hash, datetime.now().isoformat(), user_id)
            )
