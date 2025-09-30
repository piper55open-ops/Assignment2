from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Attraction(Base):
    __tablename__ = 'attractions'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    short_description = Column(Text)
    long_description = Column(Text)
    image_url = Column(String(200))

class Photo(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True)
    user_name = Column(String(50))
    location = Column(String(100))
    image_url = Column(String(200))

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    role = Column(String(20))  # Admin, Tourist, Provider
