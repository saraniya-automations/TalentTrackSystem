# app/models/employee_profile.py
import sqlite3
from app.config import Config
from datetime import datetime

class EmployeeProfile:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DATABASE, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS employee_profiles (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL,
                    middle_name TEXT,
                    nickname TEXT,
                    other_id TEXT,
                    license_number TEXT,
                    license_expiry_date TEXT,
                    nationality TEXT,
                    marital_status TEXT,
                    date_of_birth TEXT,
                    gender TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')

    def create_profile(self, user_id, data):
        with self.conn:
            self.conn.execute('''
                INSERT INTO employee_profiles (
                    user_id, middle_name, nickname, other_id, license_number,
                    license_expiry_date, nationality, marital_status, date_of_birth, gender
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                data.get('middle_name'),
                data.get('nickname'),
                data.get('other_id'),
                data.get('license_number'),
                data.get('license_expiry_date'),
                data.get('nationality'),
                data.get('marital_status'),
                data.get('date_of_birth'),
                data.get('gender')
            ))

    def get_by_employee_id(self, employee_id):
        cursor = self.conn.execute('''
            SELECT ep.*, u.employee_id FROM employee_profiles ep
            JOIN users u ON ep.user_id = u.id
            WHERE u.employee_id = ?
        ''', (employee_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def update_profile(self, user_id, data):
        fields = []
        values = []

        for field in ['middle_name', 'nickname', 'other_id', 'license_number',
                      'license_expiry_date', 'nationality', 'marital_status',
                      'date_of_birth', 'gender']:
            if field in data:
                fields.append(f"{field} = ?")
                values.append(data[field])

        fields.append("updated_at = ?")
        values.extend([datetime.now().isoformat(), user_id])

        with self.conn:
            self.conn.execute(
                f"UPDATE employee_profiles SET {', '.join(fields)} WHERE user_id = ?",
                tuple(values)
            )
