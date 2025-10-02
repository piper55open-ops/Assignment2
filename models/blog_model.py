from models.database import Database

class BlogModel:
    def __init__(self):
        self.db = Database()

    def create_table(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                short_description TEXT,
                full_description TEXT,
                image TEXT
            )
        """)

    def add_blog(self, title, short_description, full_description, image):
        self.db.execute(
            "INSERT INTO blogs (title, short_description, full_description, image) VALUES (?, ?, ?, ?)",
            (title, short_description, full_description, image)
        )

    def get_all_blogs(self):
        return self.db.fetchall("SELECT * FROM blogs")

    def get_blog_by_id(self, blog_id):
        return self.db.fetchone("SELECT * FROM blogs WHERE id = ?", (blog_id,))

