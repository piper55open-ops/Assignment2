import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database

class TripModel:
    def __init__(self):
        self.db = Database()

    def create_table(self):
        """Create or update the trips table with new columns."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT,
                destination TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                budget REAL,
                ai_plan TEXT,
                status TEXT DEFAULT 'planned',
                description TEXT,
                cover_image TEXT,
                google_maps_url TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

    def add_trip(self, user_id, destination, start_date, end_date, budget, title=None, status='planned',
                 description=None, cover_image=None, google_maps_url=None, ai_plan=None):
        self.db.execute("""
            INSERT INTO trips
            (user_id, title, destination, start_date, end_date, budget, status, description, cover_image, google_maps_url, ai_plan)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, title, destination, start_date, end_date, budget, status, description, cover_image, google_maps_url, ai_plan))

    def get_trips_by_user(self, user_id):
        return self.db.fetchall("SELECT * FROM trips WHERE user_id = ?", (user_id,))

    def get_trip_by_id(self, trip_id):
        return self.db.fetchone("SELECT * FROM trips WHERE id = ?", (trip_id,))

    def update_trip(self, trip_id, destination=None, start_date=None, end_date=None, budget=None,
                    title=None, status=None, description=None, cover_image=None, google_maps_url=None, ai_plan=None):
        # Build dynamic update query
        columns = []
        values = []

        if title is not None:
            columns.append("title=?")
            values.append(title)
        if destination is not None:
            columns.append("destination=?")
            values.append(destination)
        if start_date is not None:
            columns.append("start_date=?")
            values.append(start_date)
        if end_date is not None:
            columns.append("end_date=?")
            values.append(end_date)
        if budget is not None:
            columns.append("budget=?")
            values.append(budget)
        if status is not None:
            columns.append("status=?")
            values.append(status)
        if description is not None:
            columns.append("description=?")
            values.append(description)
        if cover_image is not None:
            columns.append("cover_image=?")
            values.append(cover_image)
        if google_maps_url is not None:
            columns.append("google_maps_url=?")
            values.append(google_maps_url)
        if ai_plan is not None:
            columns.append("ai_plan=?")
            values.append(ai_plan)

        values.append(trip_id)
        sql = f"UPDATE trips SET {', '.join(columns)} WHERE id=?"
        self.db.execute(sql, tuple(values))

    def delete_trip(self, trip_id):
        self.db.execute("DELETE FROM trips WHERE id=?", (trip_id,))
        
   