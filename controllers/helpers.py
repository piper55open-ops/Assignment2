from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Database:
    __instance = None

    def __init__(self):
        if Database.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            engine = create_engine('sqlite:///tourism.db', echo=True)
            Session = sessionmaker(bind=engine)
            self.session = Session()
            Database.__instance = self

    @staticmethod
    def get_instance():
        if Database.__instance is None:
            Database()
        return Database.__instance.session

def get_db_connection():
    return Database.get_instance()
