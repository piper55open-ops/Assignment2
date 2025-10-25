import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database

import sqlite3
db = Database()


import os
import sqlite3
from models.database import Database  # make sure path is correct

def create_tables():
    db = Database()

    # ------------------ Properties Table ------------------
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
                food_available INTEGER DEFAULT 0,
                facilities TEXT,
                image TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Active',
                FOREIGN KEY (provider_id) REFERENCES providers(id)
            )
    """)

    print("✅ Table 'properties' created or already exists.")

    

    
    print("\n🎉 All required tables created successfully!")

if __name__ == "__main__":
    create_tables()
