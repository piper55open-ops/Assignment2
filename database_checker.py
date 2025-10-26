import os
import sqlite3
from prettytable import PrettyTable

# ✅ Path to your real database
DB_PATH = r"C:\Users\oshad\OneDrive\Documents\Yobee\TravelMate\Assignment2\database\app.db"

def check_database():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print(f"\n✅ Connected to database: {DB_PATH}\n")

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row["name"] for row in cursor.fetchall()]

        if not tables:
            print("⚠️ No tables found in the database.")
            return

        for table in tables:
            print(f"\n📘 Table: {table}")
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()

            if rows:
                table_obj = PrettyTable()
                table_obj.field_names = rows[0].keys()
                for row in rows:
                    table_obj.add_row([str(v) if v is not None else '' for v in row])
                print(table_obj)
            else:
                print("   (No data in this table)")

        conn.close()
        print("\n✅ Database check complete.")

    except Exception as e:
        print(f"❌ Error while checking database: {e}")

if __name__ == "__main__":
    check_database()
