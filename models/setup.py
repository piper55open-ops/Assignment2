import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database

import sqlite3
db = Database()


def update_tables():


    # --- Update trips table ---
    try:
        db.execute("ALTER TABLE trips ADD COLUMN title TEXT")
    except sqlite3.OperationalError:
        print("Column 'title' already exists in trips")
    try:
        db.execute("ALTER TABLE trips ADD COLUMN status TEXT DEFAULT 'planned'")
    except sqlite3.OperationalError:
        print("Column 'status' already exists in trips")
    try:
        db.execute("ALTER TABLE trips ADD COLUMN description TEXT")
    except sqlite3.OperationalError:
        print("Column 'description' already exists in trips")
    try:
       db.execute("ALTER TABLE trips ADD COLUMN cover_image TEXT")
    except sqlite3.OperationalError:
        print("Column 'cover_image' already exists in trips")
    try:
        db.execute("ALTER TABLE trips ADD COLUMN google_maps_url TEXT")
    except sqlite3.OperationalError:
        print("Column 'google_maps_url' already exists in trips")

    # --- Update travel_memories table ---
    try:
        db.execute("ALTER TABLE travel_memories ADD COLUMN trip_id INTEGER")
    except sqlite3.OperationalError:
        print("Column 'trip_id' already exists in travel_memories")
    try:
        db.execute("ALTER TABLE travel_memories ADD COLUMN hotel_id INTEGER")
    except sqlite3.OperationalError:
        print("Column 'hotel_id' already exists in travel_memories")

    # --- Create trip_hotels linking table ---
    db.execute("""
        CREATE TABLE IF NOT EXISTS trip_hotels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            hotel_id INTEGER NOT NULL,
            FOREIGN KEY (trip_id) REFERENCES trips(id),
            FOREIGN KEY (hotel_id) REFERENCES saved_stays(id)
        )
    """)

    print("Tables updated successfully!")

if __name__ == "__main__":
    update_tables()
