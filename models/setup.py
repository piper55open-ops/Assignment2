# test_provider_inquiries.py
import os
import sqlite3


import sqlite3
from datetime import datetime

# Path to your database (adjust if needed)
DB_PATH = r"C:\Users\oshad\OneDrive\Documents\Yobee\TravelMate\Assignment2\database\app.db"

def reset_inquiries_and_insert_properties():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    print(f"✅ Connected to database at {DB_PATH}\n")

    try:
        # Step 1: Clear existing inquiries & messages
        cursor.execute("DELETE FROM inquiry_messages;")
        cursor.execute("DELETE FROM inquiries;")
        print("🧹 Cleared all data from 'inquiry_messages' and 'inquiries' tables.")


        # Step 3: Verify new properties
        cursor.execute("""
            SELECT id, provider_id, name, property_type, location, price_per_day, status
            FROM properties
            ORDER BY id DESC
            LIMIT 5;
        """)
        rows = cursor.fetchall()
        print("✅ Recently added properties:\n")
        for row in rows:
            print(f"ID: {row[0]} | Provider: {row[1]} | Name: {row[2]} | Type: {row[3]} | Location: {row[4]} | Price: {row[5]} | Status: {row[6]}")
        print("\n🎉 Database reset and property setup complete!")

    except Exception as e:
        print("❌ Error:", e)
        conn.rollback()

    finally:
        conn.close()
        print("🔒 Connection closed.")

if __name__ == "__main__":
    reset_inquiries_and_insert_properties()

