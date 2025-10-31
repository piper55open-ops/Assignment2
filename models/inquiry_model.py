import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database

class InquiryModel:
    def __init__(self):
        self.db = Database()
    

    def create_table(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS inquiry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                sender_role TEXT NOT NULL, -- 'traveller' or 'provider'
                message TEXT NOT NULL,
                reply TEXT,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(property_id) REFERENCES properties(id)
            )
        """)

    def add_inquiry(self, property_id, sender_id, sender_role, message):
        self.db.execute(
            "INSERT INTO inquiry (property_id, sender_id, sender_role, message) VALUES (?, ?, ?, ?)",
            (property_id, sender_id, sender_role, message)
        )

    def get_inquiries_by_property(self, property_id):
        return self.db.fetchall(
            "SELECT * FROM inquiry WHERE property_id=? ORDER BY created_at DESC", 
            (property_id,)
        )

    def get_inquiries_by_user(self, user_id, role):
        return self.db.fetchall(
            "SELECT * FROM inquiry WHERE sender_id=? AND sender_role=? ORDER BY created_at DESC",
            (user_id, role)
        )

    def update_reply(self, inquiry_id, reply, status):
        self.db.execute(
            "UPDATE inquiry SET reply=?, status=? WHERE id=?",
            (reply, status, inquiry_id)
        )
