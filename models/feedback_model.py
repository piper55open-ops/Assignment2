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
                user_id INTEGER,
                user_type TEXT CHECK(user_type IN ('tourist', 'provider', 'admin')) NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                reply TEXT,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def add_feedback(self, user_id, user_type, name, email, message):
        self.db.execute(
            "INSERT INTO feedbacks (user_id, user_type, name, email, message) VALUES (?, ?, ?, ?, ?)",
            (user_id, user_type, name, email, message)
        )

    def get_all_feedbacks(self):
        return self.db.fetchall("SELECT * FROM feedbacks ORDER BY created_at DESC")

    def get_feedbacks_by_user(self, user_id, user_type):
        return self.db.fetchall(
            "SELECT * FROM feedbacks WHERE user_id=? AND user_type=? ORDER BY created_at DESC",
            (user_id, user_type)
        )

    def update_feedback(self, feedback_id, reply, status):
        self.db.execute(
            "UPDATE feedbacks SET reply=?, status=? WHERE id=?",
            (reply, status, feedback_id)
        )

    def delete_feedback(self, feedback_id):
        self.db.execute("DELETE FROM feedbacks WHERE id=?", (feedback_id,))
        

    def get_unread_replies_count(self, user_id, user_type):
        result = self.db.fetchall(
            "SELECT COUNT(*) AS count FROM feedbacks WHERE user_id=? AND user_type=? AND reply IS NOT NULL AND status='Resolved'",
            (user_id, user_type)
        )
        return result[0]["count"] if result else 0
