import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database
from datetime import datetime

class AdModel:
    def __init__(self):
        self.db = Database()
        self.create_table()

    def create_table(self):
        """Create ads table if not exists"""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_id INTEGER NOT NULL,
                provider_name TEXT,
                title TEXT NOT NULL,
                description TEXT,
                date_submitted TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Pending', 'Approved', 'Rejected'))
            )
        """)

    def add_ad(self, provider_id, provider_name, title, description):
        """Add a new advertisement request"""
        date_submitted = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.execute("""
            INSERT INTO ads (provider_id, provider_name, title, description, date_submitted, status)
            VALUES (?, ?, ?, ?, ?, 'Pending')
        """, (provider_id, provider_name, title, description))

    def get_all_ads_pending_or_approved(self):
        """Get all ads to show in admin page"""
        return self.db.fetchall("""
            SELECT * FROM ads
            ORDER BY date_submitted DESC
        """)

    def update_status(self, ad_id, status):
        """Approve or Reject an advertisement"""
        if status not in ['Approved', 'Rejected']:
            raise ValueError("Invalid status")
        self.db.execute("UPDATE ads SET status=? WHERE id=?", (status, ad_id))
