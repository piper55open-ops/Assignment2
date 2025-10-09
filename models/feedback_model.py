import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database

class FeedbackModel:
    def __init__(self):
        self.db = Database()
        self.create_table()

    def create_table(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                reply TEXT,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def add_feedback(self, name, email, message):
        self.db.execute(
            "INSERT INTO feedbacks (name, email, message) VALUES (?, ?, ?)",
            (name, email, message)
        )

    def get_all_feedbacks(self):
        return self.db.fetchall("SELECT * FROM feedbacks ORDER BY created_at DESC")

    def update_feedback(self, feedback_id, reply, status):
        self.db.execute(
            "UPDATE feedbacks SET reply=?, status=? WHERE id=?",
            (reply, status, feedback_id)
        )

    def delete_feedback(self, feedback_id):
        self.db.execute(
            "DELETE FROM feedbacks WHERE id=?",
            (feedback_id,)
        )
