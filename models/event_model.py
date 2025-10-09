import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database


class EventModel:
    def __init__(self):
        self.db = Database()
        
        
    def create_table(self):
        self.db.execute("""
            CREATE TABLE events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                date TEXT NOT NULL,
                image TEXT NOT NULL,
                location TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def get_all_events(self):
        return self.db.fetchall("SELECT * FROM events ORDER BY date")

    def get_event_by_id(self, event_id):
        return self.db.fetchone("SELECT * FROM events WHERE id=?", (event_id,))

    def add_event(self, title, description, date, image, location):
        self.db.execute(
            "INSERT INTO events (title, description, date, image, location) VALUES (?, ?, ?, ?, ?)",
            (title, description, date, image, location)
        )

    def update_event(self, event_id, title, description, date, image, location):
        self.db.execute(
            "UPDATE events SET title=?, description=?, date=?, image=?, location=? WHERE id=?",
            (title, description, date, image, location, event_id)
        )

    def delete_event(self, event_id):
        self.db.execute("DELETE FROM events WHERE id=?", (event_id,))
        
    
    def count_events(self):
        result = self.db.fetchone("SELECT COUNT(*) as count FROM events")
        return result["count"] if result else 0

