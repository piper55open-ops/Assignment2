import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database

class PropertyModel:
    def __init__(self):
        self.db = Database()

    def create_table(self):
        """Create the properties table."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                location TEXT,
                image TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (provider_id) REFERENCES providers(id)
            )
        """)

    def add_property(self, provider_id, name, location, image):
        self.db.execute(
            "INSERT INTO properties (provider_id, name, location, image) VALUES (?, ?, ?, ?)",
            (provider_id, name, location, image)
        )

    def get_properties_by_provider(self, provider_id):
        return self.db.fetchall(
            "SELECT * FROM properties WHERE provider_id = ?", (provider_id,)
        )

    def get_property_by_id(self, property_id):
        return self.db.fetchone(
            "SELECT * FROM properties WHERE id = ?", (property_id,)
        )

    def update_property(self, property_id, name, location, image):
        self.db.execute(
            "UPDATE properties SET name=?, location=?, image=? WHERE id=?",
            (name, location, image, property_id)
        )

    def delete_property(self, property_id):
        self.db.execute(
            "DELETE FROM properties WHERE id=?", (property_id,)
        )

    def count_properties(self, provider_id):
        result = self.db.fetchone(
            "SELECT COUNT(*) as count FROM properties WHERE provider_id=?", (provider_id,)
        )
        return result["count"] if result else 0

    def get_analytics(self, provider_id):
        # Example: total properties
        total = self.count_properties(provider_id)
        return {"total_properties": total}
    