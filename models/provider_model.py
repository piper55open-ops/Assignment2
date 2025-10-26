import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database

class ProviderModel:
    def __init__(self):
        self.db = Database()

    def create_table(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                hotel_name TEXT NOT NULL,
                hotel_address TEXT NOT NULL,
                website_url TEXT,
                image TEXT,
                registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
    def add_provider(self, user_id, hotel_name, hotel_address, website_url=None, image=None):
        # Check if provider already exists
        existing = self.db.fetchone("SELECT * FROM providers WHERE user_id = ?", (user_id,))
        if existing:
            return {"success": False, "message": "Provider for this user already exists."}

        self.db.execute(
            """
            INSERT INTO providers (user_id, hotel_name, hotel_address, website_url, image)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, hotel_name, hotel_address, website_url, image)
        )
        return {"success": True, "message": "Provider added successfully."}


    def get_current_provider(self,user_id):
        query = """
            SELECT p.*, u.username, u.email
            FROM providers p
            JOIN users u ON p.user_id = u.id
            WHERE p.user_id = ?
        """
        return self.db.fetchone(query, (user_id,))


    def count_properties(self, provider_id):
        """Count total properties owned by provider"""
        result = self.db.fetchone("SELECT COUNT(*) as total FROM properties WHERE provider_id = ?", (provider_id,))
        return result["total"] if result else 0

    def count_promotions(self, provider_id):
        """Count total promotions created by provider"""
        result = self.db.fetchone("SELECT COUNT(*) as total FROM promotions WHERE provider_id = ?", (provider_id,))
        return result["total"] if result else 0

    def calculate_profile_completion(self, provider):
        """Rough profile completion calculation"""
        filled_fields = sum(bool(provider[field]) for field in ["hotel_name", "hotel_address", "website_url", "image"])
        total_fields = 4
        return int((filled_fields / total_fields) * 100)
    
    def get_all_providers(self):
        query = """
            SELECT p.*, u.username, u.email
            FROM providers p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.id ASC
        """
        return self.db.fetchall(query)

