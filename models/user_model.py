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
