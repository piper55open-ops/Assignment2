import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database
import json
from datetime import datetime

class JourneyModel:
    def __init__(self):
        self.db = Database()
        self.create_table()

    def create_table(self):
        """Create journeys table if it doesn't exist"""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS journeys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT,
                lat REAL,
                lng REAL,
                images TEXT,  -- JSON string of image URLs
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

    def add_journey(self, user_id, title, description, location=None, lat=None, lng=None, images=None):
        """
        Add a new journey
        images: list of image URLs
        """
        images_json = json.dumps(images) if images else None
        self.db.execute(
            """
            INSERT INTO journeys (user_id, title, description, location, lat, lng, images)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, title, description, location, lat, lng, images_json)
        )

    def get_journeys_by_user(self, user_id):
        """Get all journeys for a specific user"""
        cursor = self.db.execute("SELECT * FROM journeys WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get_all_journeys(self):
        return self.db.fetchall("""
            SELECT j.*, u.username 
            FROM journeys j 
            JOIN users u ON j.user_id = u.id 
            ORDER BY j.created_at DESC
        """)

    def get_journey_by_id(self, journey_id):
        """Get a single journey by its ID"""
        cursor = self.db.execute("SELECT * FROM journeys WHERE id = ?", (journey_id,))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def _row_to_dict(self, row):
        """Convert SQLite Row to dictionary and parse images JSON"""
        journey = dict(row)
        if journey.get('images'):
            journey['images'] = json.loads(journey['images'])
        else:
            journey['images'] = []
        # format timestamp nicely
        journey['created_at'] = journey['created_at']
        return journey
    
    def count_journeys(self):
        result = self.db.fetchone("SELECT COUNT(*) as count FROM journeys")
        return result["count"] if result else 0
    
    def delete_journey(self, journey_id):
        self.db.execute("DELETE FROM journeys WHERE id = ?", (journey_id,))
        
