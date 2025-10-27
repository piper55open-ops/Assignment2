import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.database import Database
import sqlite3
import datetime
from models.event_model import EventModel

# Initialize DB and model
db = Database()
event_model = EventModel()



# Event list to insert
events = [
    {
        "title": "Queenstown Wine Festival",
        "description": "Celebrate the region’s finest wines, live music, and stunning lakeside views.",
        "date": "2025-11-12",
        "image": "event1.jpg",
        "location": "Queenstown"
    },
    {
        "title": "Auckland Lantern Festival",
        "description": "Immerse in beautiful lanterns, food stalls, and cultural performances.",
        "date": "2026-02-08",
        "image": "event2.jpg",
        "location": "Auckland"
    },
    {
        "title": "Rotorua Adventure Week",
        "description": "Adrenaline-packed adventures including zip-lining, rafting, and geothermal hikes.",
        "date": "2026-03-20",
        "image": "event3.jpg",
        "location": "Rotorua"
    },
    {
        "title": "Wellington Food Carnival",
        "description": "Explore world flavors and street food in New Zealand’s culinary capital.",
        "date": "2026-04-10",
        "image": "event4.jpg",
        "location": "Wellington"
    },
    {
        "title": "Christchurch Art Parade",
        "description": "Celebrate local art, creative workshops, and live street performances.",
        "date": "2026-05-02",
        "image": "event5.jpg",
        "location": "Christchurch"
    },
    {
        "title": "Bay of Islands Music Fest",
        "description": "Live bands, sea breeze, and the perfect coastal vibe for every traveler.",
        "date": "2026-06-14",
        "image": "event6.jpg",
        "location": "Bay of Islands"
    }
]

# Insert events
for e in events:
    db.execute(
        """
        INSERT INTO events (title, description, date, image, location)
        VALUES (?, ?, ?, ?, ?)
        """,
        (e["title"], e["description"], e["date"], e["image"], e["location"])
    )


print("✅ Events successfully added to the database!")
