import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database


class BlogModel:
    def __init__(self):
        self.db = Database()

    def create_table(self):
        """Create the blogs table with author and date columns."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS blogs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                date TEXT,
                short_description TEXT,
                full_description TEXT,
                image TEXT
            )
        """)

    def add_blog(self, title, author, date, short_description, full_description, image):
        """Insert a new blog entry."""
        self.db.execute(
            """
            INSERT INTO blogs (title, author, date, short_description, full_description, image)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (title, author, date, short_description, full_description, image)
        )

    def get_all_blogs(self):
        """Fetch all blog entries."""
        return self.db.fetchall("SELECT * FROM blogs ORDER BY id DESC")

    def get_blog_by_id(self, blog_id):
        """Fetch a single blog by its ID."""
        return self.db.fetchone("SELECT * FROM blogs WHERE id = ?", (blog_id,))

    def count_blogs(self):
        """Return the total number of blogs."""
        result = self.db.fetchone("SELECT COUNT(*) as count FROM blogs")
        return result["count"] if result else 0

    def delete_blog(self, blog_id):
        """Delete a blog by its ID."""
        self.db.execute("DELETE FROM blogs WHERE id = ?", (blog_id,))

    def update_blog(self, blog_id, title, author, date, short_description, full_description, image):
        """Update an existing blog."""
        self.db.execute(
            """
            UPDATE blogs
            SET title = ?, author = ?, date = ?, short_description = ?, full_description = ?, image = ?
            WHERE id = ?
            """,
            (title, author, date, short_description, full_description, image, blog_id)
        )

    def drop_table(self):
        """Drop blogs table if it exists."""
        self.db.execute("DROP TABLE IF EXISTS blogs")



