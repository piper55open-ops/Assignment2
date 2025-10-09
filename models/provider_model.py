from models.database import Database

class ProviderModel:
    def __init__(self):
        self.db = Database()
        self.create_table()

    def create_table(self):
        # Drop table if exists
        self.db.execute("DROP TABLE IF EXISTS providers")

        # Create new providers table
        self.db.execute("""
            CREATE TABLE providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hotel_name TEXT NOT NULL,
                hotel_address TEXT NOT NULL,
                website_url TEXT,
                image TEXT,
                registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def add_provider(self, username, email, hotel_name, hotel_address, website_url=None, image=None):
        self.db.execute(
            "INSERT INTO providers (username, email, hotel_name, hotel_address, website_url, image) VALUES (?, ?, ?, ?, ?, ?)",
            (username, email, hotel_name, hotel_address, website_url, image)
        )

    def get_all_providers(self):
        return self.db.fetchall("SELECT * FROM providers")

    def get_provider_by_id(self, provider_id):
        return self.db.fetchone("SELECT * FROM providers WHERE id=?", (provider_id,))

    def update_provider(self, provider_id, username, email, hotel_name, hotel_address, website_url=None, image=None):
        self.db.execute("""
            UPDATE providers SET username=?, email=?, hotel_name=?, hotel_address=?, website_url=?, image=?
            WHERE id=?
        """, (username, email, hotel_name, hotel_address, website_url, image, provider_id))

    def delete_provider(self, provider_id):
        self.db.execute("DELETE FROM providers WHERE id=?", (provider_id,))
