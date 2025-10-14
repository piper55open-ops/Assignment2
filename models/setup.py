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
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        provider_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        property_type TEXT CHECK(property_type IN ('House', 'Apartment', 'Room', 'Hut', 'Cabin', 'Villa', 'Bungalow')),
        location TEXT,
        price_per_day REAL NOT NULL,
        max_guests INTEGER DEFAULT 1,
        food_available INTEGER DEFAULT 0, -- 0 = No, 1 = Yes
        facilities TEXT, -- Facilities all in one column
        image TEXT,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'Active',
        FOREIGN KEY (provider_id) REFERENCES providers(id)
    )
""")

print("✅ Properties table recreated successfully!")
