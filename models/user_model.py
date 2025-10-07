import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database

class UserModel:
    def __init__(self):
        self.db = Database()
        self.create_table()

    def create_table(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('tourist', 'provider', 'admin')),
                image TEXT
            )
        """)

    def add_user(self, username, email, password, role, image=None):
        self.db.execute(
            "INSERT INTO users (username, email, password, role, image) VALUES (?, ?, ?, ?, ?)",
            (username, email, password, role, image)
        )

    def get_user_by_email(self, email):
        return self.db.fetchone("SELECT * FROM users WHERE email = ?", (email,))
    
    def count_users_by_role(self, role):
        result = self.db.fetchone("SELECT COUNT(*) as count FROM users WHERE role=?", (role,))
        return result["count"] if result else 0

    def get_all_users(self):
        return self.db.fetchall("SELECT * FROM users")
    
    def get_user_by_id(self, user_id):
        return self.db.fetchone("SELECT * FROM users WHERE id = ?", (user_id,))

