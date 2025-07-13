# app/models/employee_profile.py
import sqlite3
from app.config import Config
from datetime import datetime
import json
from app.models.database import Database

class EmployeeProfile(Database):

    def __init__(self):
        super().__init__()
        
    # def __init__(self):
    #     self.conn = sqlite3.connect(Config.DATABASE, check_same_thread=False)
    #     self.conn.row_factory = sqlite3.Row
    #     self.create_table()

    # def create_table(self):
    #     with self.conn:
    #         self.conn.execute('''
    #             CREATE TABLE IF NOT EXISTS employee_profiles (
    #                 id INTEGER PRIMARY KEY,
    #                 user_id INTEGER UNIQUE NOT NULL,
    #                 middle_name TEXT,
    #                 nickname TEXT,
    #                 other_id TEXT,
    #                 license_number TEXT,
    #                 license_expiry_date TEXT,
    #                 nationality TEXT,
    #                 marital_status TEXT,
    #                 date_of_birth TEXT,
    #                 gender TEXT,
    #                 created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    #                 updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    #                 FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    #             )
    #         ''')

    # def create_profile(self, user_id, data):
    #     with self.conn:
    #         self.conn.execute('''
    #             INSERT INTO employee_profiles (
    #                 user_id, middle_name, nickname, other_id, license_number,
    #                 license_expiry_date, nationality, marital_status, date_of_birth, gender
    #             ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    #         ''', (
    #             user_id,
    #             data.get('middle_name'),
    #             data.get('nickname'),
    #             data.get('other_id'),
    #             data.get('license_number'),
    #             data.get('license_expiry_date'),
    #             data.get('nationality'),
    #             data.get('marital_status'),
    #             data.get('date_of_birth'),
    #             data.get('gender')
    #         ))

    def get_by_employee_id(self, employee_id):
        cursor = self.conn.execute('''
            SELECT ep.*, u.employee_id, u.name, u.email FROM employee_profiles ep
            JOIN users u ON ep.user_id = u.employee_id
            WHERE u.employee_id = ?
        ''', (employee_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # def get_profile(self, user_id):
    #     cursor = self.conn.execute("SELECT * FROM employee_profiles WHERE user_id = ?", (user_id,))
    #     row = cursor.fetchone()
    #     if not row:
    #         return None
    #     return {
    #         key: json.loads(row[key]) if key != "id" and key != "user_id" else row[key]
    #         for key in row.keys()
    #     }
    
    # def update_profile(self, user_id, data):
    #     fields = []
    #     values = []

    #     for field in ['middle_name', 'nickname', 'other_id', 'license_number',
    #                   'license_expiry_date', 'nationality', 'marital_status',
    #                   'date_of_birth', 'gender']:
    #         if field in data:
    #             fields.append(f"{field} = ?")
    #             values.append(data[field])

    #     fields.append("updated_at = ?")
    #     values.extend([datetime.now().isoformat(), user_id])

        # with self.conn:
        #     self.conn.execute(
        #         f"UPDATE employee_profiles SET {', '.join(fields)} WHERE user_id = ?",
        #         tuple(values)
        #     )

    def update_profile(self, user_id, data):
        fields = []
        values = []

        for key in ['personal_details', 'contact_details', 'emergency_contacts', 'dependents',
                    'job_details', 'salary_details', 'report_to', 'qualifications']:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(json.dumps(data[key]))

        fields.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(user_id)

        self.conn.execute(
            f"UPDATE employee_profiles SET {', '.join(fields)} WHERE user_id = ?",
            tuple(values)
        )
        self.conn.commit()

    def create_profile(self, user_id, data):
        now = datetime.now().isoformat()
        self.conn.execute('''
            INSERT INTO employee_profiles (
                user_id, personal_details, contact_details, emergency_contacts, 
                dependents, job_details, salary_details, report_to, qualifications,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            json.dumps(data.get('personal_details', {})),
            json.dumps(data.get('contact_details', {})),
            json.dumps(data.get('emergency_contacts', [])),
            json.dumps(data.get('dependents', [])),
            json.dumps(data.get('job_details', {})),
            json.dumps(data.get('salary_details', {})),
            json.dumps(data.get('report_to', {})),
            json.dumps(data.get('qualifications', [])),
            now, now
        ))
        self.conn.commit()

    def get_all(self, limit, offset, key=''):
        key = key.strip().lower() 
        query = '''
            SELECT ep.*, u.employee_id, u.name, u.department, u.role FROM employee_profiles ep
            JOIN users u ON ep.user_id = u.employee_id
        '''
        params = []
        
        if key:
            query += ' WHERE u.name LIKE ?'
            params.append(f'%{key}%')
        
        query += ' LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor = self.conn.execute(query, tuple(params))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_total_profile_count(self):
        cursor = self.conn.execute('SELECT COUNT(*) FROM employee_profiles')
        return cursor.fetchone()[0]