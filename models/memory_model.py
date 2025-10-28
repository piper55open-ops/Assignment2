import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database

class MemoryModel:
    def __init__(self):
        self.db = Database()

    def create_table(self):
        """Create the travel_memories table."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS travel_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                story TEXT,
                date TEXT,
                image TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

    def add_memory(self, user_id, title, story, date, image=None):
        self.db.execute("""
            INSERT INTO travel_memories (user_id, title, story, date, image)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, title, story, date, image))

    def get_memories_by_user(self, user_id):
        return self.db.fetchall("SELECT * FROM travel_memories WHERE user_id = ?", (user_id,))

    def get_memory_by_id(self, memory_id):
        return self.db.fetchone("SELECT * FROM travel_memories WHERE id = ?", (memory_id,))

    def update_memory(self, memory_id, title, story, date, image=None):
        self.db.execute("""
            UPDATE travel_memories
            SET title=?, story=?, date=?, image=?
            WHERE id=?
        """, (title, story, date, image, memory_id))

    def delete_memory(self, memory_id):
        self.db.execute("DELETE FROM travel_memories WHERE id=?", (memory_id,))
        
    def get_recent_memories(self, limit=4):
        """Fetch the most recent traveller memories with user info."""
        return self.db.fetchall("""
            SELECT tm.*, u.username 
            FROM travel_memories tm
            JOIN users u ON tm.user_id = u.id
            ORDER BY tm.created_date DESC
            LIMIT ?
        """, (limit,))

