import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database

class PromotionModel:
    def __init__(self):
        self.db = Database()

    def create_table(self):
        """Create the promotions table."""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS promotions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                image TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (provider_id) REFERENCES providers(id)
            )
        """)

    def add_promotion(self, provider_id, title, description, image):
        self.db.execute(
            "INSERT INTO promotions (provider_id, title, description, image) VALUES (?, ?, ?, ?)",
            (provider_id, title, description, image)
        )

    def get_promotions_by_provider(self, provider_id):
        return self.db.fetchall(
            "SELECT * FROM promotions WHERE provider_id = ?", (provider_id,)
        )

    def get_promotion_by_id(self, promotion_id):
        return self.db.fetchone(
            "SELECT * FROM promotions WHERE id = ?", (promotion_id,)
        )

    def update_promotion(self, promotion_id, title, description, image):
        self.db.execute(
            "UPDATE promotions SET title=?, description=?, image=? WHERE id=?",
            (title, description, image, promotion_id)
        )

    def delete_promotion(self, promotion_id):
        self.db.execute(
            "DELETE FROM promotions WHERE id=?", (promotion_id,)
        )

    def count_promotions(self, provider_id):
        result = self.db.fetchone(
            "SELECT COUNT(*) as count FROM promotions WHERE provider_id=?", (provider_id,)
        )
        return result["count"] if result else 0
