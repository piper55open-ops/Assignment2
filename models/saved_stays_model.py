class SavedStaysModel:
    def __init__(self, db):
        self.db = db

    def create_table(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS saved_stays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                hotel_name TEXT NOT NULL,
                address TEXT,
                rating TEXT,
                distance TEXT,
                duration TEXT,
                google_maps_url TEXT,
                saved_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

    def save(self, user_id, hotel):
        query = """
            INSERT INTO saved_stays (user_id, hotel_name, address, rating, distance, duration, google_maps_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.db.execute(query, (
            user_id,
            hotel["name"],
            hotel.get("address"),
            hotel.get("rating"),
            hotel.get("distance"),
            hotel.get("duration"),
            hotel.get("maps_url"),
        ))
        return True

    def get_by_user(self, user_id):
        return self.db.execute(
            "SELECT * FROM saved_stays WHERE user_id = ? ORDER BY saved_date DESC",
            (user_id,)
        ).fetchall()
