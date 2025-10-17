import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database

class TripModel:
    def __init__(self):
        self.db = Database()

    def create_table(self):
        """Create the trips table."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                destination TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                budget REAL,
                ai_plan TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

    def add_trip(self, user_id, destination, start_date, end_date, budget, ai_plan=None):
        self.db.execute("""
            INSERT INTO trips (user_id, destination, start_date, end_date, budget, ai_plan)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, destination, start_date, end_date, budget, ai_plan))

    def get_trips_by_user(self, user_id):
        return self.db.fetchall("SELECT * FROM trips WHERE user_id = ?", (user_id,))

    def get_trip_by_id(self, trip_id):
        return self.db.fetchone("SELECT * FROM trips WHERE id = ?", (trip_id,))

    def update_trip(self, trip_id, destination, start_date, end_date, budget, ai_plan=None):
        self.db.execute("""
            UPDATE trips
            SET destination=?, start_date=?, end_date=?, budget=?, ai_plan=?
            WHERE id=?
        """, (destination, start_date, end_date, budget, ai_plan, trip_id))

    def delete_trip(self, trip_id):
        self.db.execute("DELETE FROM trips WHERE id=?", (trip_id,))
