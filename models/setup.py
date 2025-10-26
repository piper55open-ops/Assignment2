import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database
import sqlite3

db = Database()

providers = [
    (2, 'Ocean View Hotel', '123 Beach Rd', 'www.oceanviewhotel.nz', 'Kupe_sites2.jpg', '2025-10-25 12:00:00'),
    (3, 'Mountain Retreat', '45 Alpine St', 'www.mountainretreat.nz', 'hawke1.jpg', '2025-10-25 12:05:00'),
    (4, 'City Central Inn', '78 Downtown Ave', 'www.citycentralinn.nz', 'hawke2.jpg', '2025-10-25 12:10:00'),
    (5, 'Lakefront Lodge', '90 Lakeview Dr', 'www.lakefrontlodge.nz', 'Cape1.jpg', '2025-10-25 12:15:00'),
]

for p in providers:
    db.execute(
        "INSERT INTO providers (user_id, hotel_name, hotel_address, website_url, image, registered_date) VALUES (?, ?, ?, ?, ?, ?)",
        p
    )

print("Sample providers added successfully!")


