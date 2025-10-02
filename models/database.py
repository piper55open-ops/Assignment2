import os
import sqlite3

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            # Determine path for the database
            db_path = os.path.join(os.path.dirname(__file__), "..", "database", "app.db")
            db_path = os.path.abspath(db_path)  # convert to absolute path

            # Ensure the folder exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

            # Create the instance
            cls._instance = super(Database, cls).__new__(cls)
            
            # Connect to the SQLite database (it will create the file if it doesn't exist)
            try:
                cls._instance.connection = sqlite3.connect(db_path, check_same_thread=False)
                cls._instance.connection.row_factory = sqlite3.Row
                print(f"Database connected successfully at: {db_path}")
            except sqlite3.OperationalError as e:
                print(f"Error connecting to database: {e}")
                raise e

        return cls._instance
    
    def execute(self, query, params=None):
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.connection.commit()
        return cursor

    def get_connection(self):
        return self._instance.connection

    def close_connection(self):
        if self._instance and hasattr(self._instance, "connection"):
            self._instance.connection.close()
            type(self)._instance = None
