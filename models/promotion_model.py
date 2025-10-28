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
            start_date TEXT,
            end_date TEXT,
            status TEXT CHECK(status IN ('Pending', 'Rejected', 'Confirmed')) DEFAULT 'Pending',
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (provider_id) REFERENCES providers(id)
        )
        """)

    def add_promotion(self,provider_id, title, description, image, start_date, end_date):
        self.db.execute("""
            INSERT INTO promotions (provider_id, title, description, image, start_date, end_date, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Pending')
        """, (provider_id, title, description, image, start_date, end_date))

    def get_promotions_by_provider(self, provider_id):
        return self.db.fetchall("SELECT * FROM promotions WHERE provider_id = ?", (provider_id,))

    def update_promotion(self,promo_id, title, description, image, start_date, end_date):
        if image:
            self.db.execute("""
                UPDATE promotions
                SET title=?, description=?, image=?, start_date=?, end_date=?, status='Pending'
                WHERE id=?
            """, (title, description, image, start_date, end_date, promo_id))
        else:
            self.db.execute("""
                UPDATE promotions
                SET title=?, description=?, start_date=?, end_date=?, status='Pending'
                WHERE id=?
            """, (title, description, start_date, end_date, promo_id))

    def delete_promotion(self,promo_id):
        self.db.execute("DELETE FROM promotions WHERE id=?", (promo_id,))

    def update_status(self,promo_id, new_status):
        self.db.execute("UPDATE promotions SET status=? WHERE id=?", (new_status, promo_id))
    
    def get_promotion_by_id(self, promotion_id):
            return self.db.fetchone(
                "SELECT * FROM promotions WHERE id = ?", (promotion_id,)
            )

    def count_promotions(self, provider_id):
            result = self.db.fetchone(
                "SELECT COUNT(*) as count FROM promotions WHERE provider_id=?", (provider_id,)
            )
            return result["count"] if result else 0
        
    def get_promotions_by_status(self, status):
        return self.db.fetchall("""
            SELECT p.*, u.username, pr.hotel_name
            FROM promotions p
            JOIN providers pr ON p.provider_id = pr.id
            JOIN users u ON pr.user_id = u.id
            WHERE p.status = ?
        """, (status,))

    
    def get_recent_promotions(self, limit=3):
        """Fetch the most recent confirmed promotions ordered by date."""
        return self.db.fetchall("""
            SELECT title, description, image, start_date, end_date
            FROM promotions
            WHERE status = 'Confirmed'
            ORDER BY created_date DESC
            LIMIT ?
        """, (limit,))
