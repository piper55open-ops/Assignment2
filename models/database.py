import os
import sqlite3

class Database:
    _instance = None
    connection = None 

    def __new__(cls):
        if cls._instance is None:
            db_path = os.path.join(os.path.dirname(__file__), "..", "database", "app.db")
            db_path = os.path.abspath(db_path)
            os.makedirs(os.path.dirname(db_path), exist_ok=True)

            cls._instance = super(Database, cls).__new__(cls)

            try:
                cls._instance.connection = sqlite3.connect(db_path, check_same_thread=False)
                cls._instance.connection.row_factory = sqlite3.Row
                print(f"Database connected successfully at: {db_path}")
            except sqlite3.OperationalError as e:
                print(f"Error connecting to database: {e}")
                raise e

        return cls._instance

    def get_connection(self):
        return self.connection

    def close_connection(self):
        if self.connection:
            self.connection.close()
            type(self)._instance = None

    # -------------------- EXECUTE --------------------
    def execute(self, query, params=None):
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.connection.commit()
        return cursor

    # -------------------- FETCH SINGLE --------------------
    def fetchone(self, query, params=None):
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        row = cursor.fetchone()
        if row:
            return dict(row)  # <-- Automatically convert to dict
        return None

    # -------------------- FETCH ALL --------------------
    def fetchall(self, query, params=None):
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]  # <-- Automatically convert all rows to dict
