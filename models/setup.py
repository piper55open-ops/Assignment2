import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database


# Initialize DB connection
db = Database()

# 🧱 1. Drop the old table if it exists
db.execute("DROP TABLE IF EXISTS properties")

# 🏗️ 2. Create the new updated table
db.execute("""
    CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                destination TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                budget REAL,
                ai_plan TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
""")

print("✅ Trips table recreated successfully!")
