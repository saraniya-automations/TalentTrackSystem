import sqlite3
from app.config import Config

class User:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DATABASE, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    role TEXT NOT NULL
                )
            ''')

    def add(self, name, email, role):
        with self.conn:
            cursor = self.conn.execute(
                'INSERT INTO users (name, email, role) VALUES (?, ?, ?)',
                (name, email, role)
            )
        return cursor.lastrowid

    def get_all(self):
        cursor = self.conn.execute('SELECT * FROM users')
        return [dict(row) for row in cursor.fetchall()]

    def search(self, name):
        search_pattern = f"%{name}%"
        cursor = self.conn.execute('SELECT * FROM users WHERE name LIKE ?', (search_pattern,))
        return [dict(row) for row in cursor.fetchall()]

    def update(self, user_id, name, email, role):
        with self.conn:
            self.conn.execute(
                'UPDATE users SET name=?, email=?, role=? WHERE id=?',
                (name, email, role, user_id)
            )

    def delete(self, user_id):
        with self.conn:
            self.conn.execute('DELETE FROM users WHERE id=?', (user_id,))
