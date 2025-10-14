import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database

class PropertyModel:
    def __init__(self):
        self.db = Database()

    def create_table(self):
        """Create or update the properties table."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                property_type TEXT CHECK(property_type IN ('House', 'Apartment', 'Room', 'Hut', 'Cabin', 'Villa', 'Bungalow')),
                location TEXT,
                price_per_day REAL NOT NULL,
                max_guests INTEGER DEFAULT 1,
                food_available INTEGER DEFAULT 0,
                facilities TEXT,
                image TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Active',
                FOREIGN KEY (provider_id) REFERENCES providers(id)
            )
        """)

    # -------------------- CRUD OPERATIONS --------------------


    def get_properties_by_provider(self, provider_id):
        query = "SELECT * FROM properties WHERE provider_id = ? ORDER BY created_date DESC"
        return self.db.fetchall(query, (provider_id,))

    def add_property(self, provider_id, name, description, property_type, location,
                     price_per_day, max_guests, food_available, facilities, image):
        query = """
            INSERT INTO properties 
            (provider_id, name, description, property_type, location, price_per_day, 
             max_guests, food_available, facilities, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute(query, (
            provider_id, name, description, property_type, location,
            price_per_day, max_guests, food_available, facilities, image
        ))

    def update_property(self, property_id, name, property_type, location,
                        price_per_day, max_guests, food_available, facilities, status):
        query = """
            UPDATE properties
            SET name = ?, property_type = ?, location = ?, price_per_day = ?,
                max_guests = ?, food_available = ?, facilities = ?, status = ?
            WHERE id = ?
        """
        self.db.execute(query, (
            name, property_type, location, price_per_day,
            max_guests, food_available, facilities, status, property_id
        ))

    def delete_property(self, property_id):
        query = "DELETE FROM properties WHERE id = ?"
        self.db.execute(query, (property_id,))

    def get_property_by_id(self, property_id):
        return self.db.fetchone("SELECT * FROM properties WHERE id = ?", (property_id,))


    def count_properties(self, provider_id):
        result = self.db.fetchone("SELECT COUNT(*) as count FROM properties WHERE provider_id=?", (provider_id,))
        return result["count"] if result else 0

    # -------------------- ANALYTICS --------------------
    def get_analytics(self, provider_id):
        total = self.count_properties(provider_id)
        active = self.db.fetchone(
            "SELECT COUNT(*) as count FROM properties WHERE provider_id=? AND status='Active'", (provider_id,)
        )
        return {
            "total_properties": total,
            "active_properties": active["count"] if active else 0
        }
